"""Six LangGraph tools for MediFlow AI CRM agent."""

import json
import time
from datetime import datetime, date, timedelta
from typing import Optional

from langchain_core.tools import tool
from sqlalchemy import select, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import async_session
from database.models import (
    HCP, Interaction, FollowUp, AuditLog, User,
    InteractionType, Sentiment, FollowUpStatus, Priority
)


def _serialize_date(obj):
    """JSON serializer for date objects."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


async def _get_session() -> AsyncSession:
    return async_session()


# ═══════════════════════════════════════════════════════════
# Tool 1: Log Interaction
# ═══════════════════════════════════════════════════════════

@tool
async def log_interaction(
    hcp_name: Optional[str] = None,
    products_discussed: Optional[str] = None,
    key_topics: Optional[str] = None,
    sentiment: Optional[str] = "neutral",
    ai_summary: Optional[str] = None,
    ai_executive_summary: Optional[dict] = None,
    ai_confidence: Optional[float] = None,
    strategic_insight: Optional[str] = None,
    notes: Optional[str] = None,
    user_id: Optional[int] = None
) -> str:
    """Log a new HCP interaction. Extract info from the user's message.

    Args:
        hcp_name: HCP name
        products_discussed: Products discussed
        key_topics: Topics covered
        sentiment: positive, neutral, or negative
        ai_summary: Brief summary
        ai_executive_summary: Dict with key_outcomes, next_actions, risks
        ai_confidence: Confidence 0.0-1.0
        strategic_insight: Recommendation
        notes: Additional notes
    """
    user_id = 1
    # Set defaults for removed parameters
    interaction_date = None
    interaction_type = "in-person"
    sentiment_score = 0.5 if sentiment == "neutral" else (0.8 if sentiment == "positive" else 0.3)
    follow_up_date = None
    follow_up_actions = None
    entities_extracted = None
    compliance_flags = None
    samples_dropped = None
    duration_minutes = None
    location = None
    ai_suggested_follow_ups = None
    async with await _get_session() as session:
        try:
            if not hcp_name:
                return json.dumps({
                    "success": False,
                    "error": "hcp_name is required to log an interaction. Please provide the HCP's name."
                })
            # Find HCP
            result = await session.execute(
                select(HCP).where(HCP.name.ilike(f"%{hcp_name}%"))
            )
            hcp = result.scalar_one_or_none()

            if not hcp:
                return json.dumps({
                    "success": False,
                    "error": f"HCP '{hcp_name}' not found. Use smart_hcp_search to find the correct name."
                })

            # Parse dates
            i_date = date.fromisoformat(interaction_date) if interaction_date else date.today()
            f_date = date.fromisoformat(follow_up_date) if follow_up_date else None

            # Map interaction type
            type_map = {
                "in-person": InteractionType.IN_PERSON,
                "virtual": InteractionType.VIRTUAL,
                "phone": InteractionType.PHONE,
                "email": InteractionType.EMAIL,
            }
            i_type = type_map.get(interaction_type, InteractionType.IN_PERSON)

            # Map sentiment
            sent_map = {
                "positive": Sentiment.POSITIVE,
                "neutral": Sentiment.NEUTRAL,
                "negative": Sentiment.NEGATIVE,
            }
            sent = sent_map.get(sentiment, Sentiment.NEUTRAL)

            # Create interaction
            interaction = Interaction(
                hcp_id=hcp.id,
                user_id=user_id,
                interaction_date=i_date,
                interaction_type=i_type,
                products_discussed=products_discussed or [],
                key_topics=", ".join(key_topics) if isinstance(key_topics, list) else str(key_topics) if key_topics else None,
                sentiment=sent,
                sentiment_score=sentiment_score or 0.5,
                follow_up_date=f_date,
                follow_up_actions=follow_up_actions,
                ai_summary=ai_summary,
                ai_executive_summary=ai_executive_summary,
                ai_confidence=ai_confidence,
                entities_extracted=entities_extracted,
                compliance_flags=compliance_flags or {"status": "clean", "flags": []},
                strategic_insight=strategic_insight,
                notes=notes,
                samples_dropped=samples_dropped or [],
                duration_minutes=duration_minutes,
                location=location,
            )
            session.add(interaction)
            await session.flush()

            # Create follow-up if date provided
            if f_date:
                follow_up = FollowUp(
                    interaction_id=interaction.id,
                    hcp_id=hcp.id,
                    user_id=user_id,
                    due_date=f_date,
                    action_description=follow_up_actions or "Follow up on interaction",
                    ai_suggested_actions=ai_suggested_follow_ups or [],
                    status=FollowUpStatus.PENDING,
                    priority=Priority.MEDIUM,
                )
                session.add(follow_up)

            # Update HCP engagement data
            eng = hcp.engagement_data or {}
            eng["visit_count"] = eng.get("visit_count", 0) + 1
            if products_discussed:
                eng["last_product_discussed"] = products_discussed[0]
            eng["last_sentiment"] = sentiment
            # Simple relationship score update
            score_delta = 3 if sentiment == "positive" else (-2 if sentiment == "negative" else 0)
            hcp.relationship_score = min(100, max(0, (hcp.relationship_score or 50) + score_delta))
            hcp.engagement_data = eng

            await session.commit()

            return json.dumps({
                "success": True,
                "interaction_id": interaction.id,
                "hcp_name": hcp.name,
                "hcp_specialty": hcp.specialty,
                "date": i_date.isoformat(),
                "type": interaction_type,
                "products": products_discussed or [],
                "sentiment": sentiment,
                "ai_summary": ai_summary,
                "ai_executive_summary": ai_executive_summary,
                "ai_confidence": ai_confidence,
                "entities_extracted": entities_extracted,
                "compliance_flags": compliance_flags or {"status": "clean", "flags": []},
                "strategic_insight": strategic_insight,
                "follow_up_date": f_date.isoformat() if f_date else None,
                "ai_suggested_follow_ups": ai_suggested_follow_ups or [],
                "relationship_score": hcp.relationship_score,
            }, default=_serialize_date)

        except Exception as e:
            await session.rollback()
            return json.dumps({"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════
# Tool 2: Edit Interaction
# ═══════════════════════════════════════════════════════════

@tool
async def edit_interaction(
    interaction_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    key_topics: Optional[str] = None,
    notes: Optional[str] = None,
    follow_up_date: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    products_discussed: Optional[str] = None,
    ai_summary: Optional[str] = None,
    user_id: Optional[int] = None
) -> str:
    """Edit an existing interaction record.

    Args:
        interaction_id: Interaction ID to edit
        sentiment: positive, neutral, or negative
        key_topics: Updated topics
        notes: Updated notes
        follow_up_date: YYYY-MM-DD
        follow_up_actions: Updated actions
        products_discussed: Updated products
        ai_summary: Updated summary
    """
    user_id = 1
    async with await _get_session() as session:
        try:
            if not interaction_id:
                return json.dumps({"success": False, "error": "interaction_id is required. You must specify which interaction you want to edit."})
            result = await session.execute(
                select(Interaction).where(Interaction.id == interaction_id)
            )
            interaction = result.scalar_one_or_none()

            if not interaction:
                return json.dumps({"success": False, "error": f"Interaction #{interaction_id} not found."})

            old_values = {}
            new_values = {}

            if sentiment is not None:
                sent_map = {"positive": Sentiment.POSITIVE, "neutral": Sentiment.NEUTRAL, "negative": Sentiment.NEGATIVE}
                if sentiment in sent_map:
                    old_values["sentiment"] = interaction.sentiment.value
                    interaction.sentiment = sent_map[sentiment]
                    new_values["sentiment"] = sentiment

            if key_topics is not None:
                new_key_topics = ", ".join(key_topics) if isinstance(key_topics, list) else str(key_topics)
                old_values["key_topics"] = interaction.key_topics
                interaction.key_topics = new_key_topics
                new_values["key_topics"] = new_key_topics

            if notes is not None:
                old_values["notes"] = interaction.notes
                interaction.notes = notes
                new_values["notes"] = notes

            if follow_up_date is not None:
                old_values["follow_up_date"] = str(interaction.follow_up_date)
                interaction.follow_up_date = date.fromisoformat(follow_up_date)
                new_values["follow_up_date"] = follow_up_date

            if follow_up_actions is not None:
                old_values["follow_up_actions"] = interaction.follow_up_actions
                interaction.follow_up_actions = follow_up_actions
                new_values["follow_up_actions"] = follow_up_actions

            if products_discussed is not None:
                new_products = products_discussed.split(",") if isinstance(products_discussed, str) else products_discussed
                old_values["products_discussed"] = interaction.products_discussed
                interaction.products_discussed = new_products
                new_values["products_discussed"] = new_products

            if ai_summary is not None:
                old_values["ai_summary"] = interaction.ai_summary
                interaction.ai_summary = ai_summary
                new_values["ai_summary"] = ai_summary

            interaction.updated_at = datetime.utcnow()

            # Audit log
            audit = AuditLog(
                user_id=user_id,
                action="update",
                entity_type="interaction",
                entity_id=interaction_id,
                old_values=old_values,
                new_values=new_values,
            )
            session.add(audit)
            await session.commit()

            return json.dumps({
                "success": True,
                "interaction_id": interaction_id,
                "updated_fields": list(new_values.keys()),
                "old_values": old_values,
                "new_values": new_values,
                "audit_logged": True,
            }, default=_serialize_date)

        except Exception as e:
            await session.rollback()
            return json.dumps({"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════
# Tool 3: Smart HCP Search
# ═══════════════════════════════════════════════════════════

@tool
async def smart_hcp_search(
    query: str,
) -> str:
    """Search HCPs by name, specialty, institution, or city.

    Args:
        query: Search term
    """
    async with await _get_session() as session:
        try:
            search = f"%{query}%"
            result = await session.execute(
                select(HCP).where(
                    or_(
                        HCP.name.ilike(search),
                        HCP.specialty.ilike(search),
                        HCP.institution.ilike(search),
                        HCP.city.ilike(search),
                    )
                ).limit(10)
            )
            hcps = result.scalars().all()

            if not hcps:
                return json.dumps({
                    "success": True,
                    "results": [],
                    "message": f"No HCPs found matching '{query}'."
                })

            results = []
            for hcp in hcps:
                # Get last interaction date
                last_int = await session.execute(
                    select(Interaction.interaction_date)
                    .where(Interaction.hcp_id == hcp.id)
                    .order_by(Interaction.interaction_date.desc())
                    .limit(1)
                )
                last_date = last_int.scalar_one_or_none()

                eng = hcp.engagement_data or {}
                results.append({
                    "id": hcp.id,
                    "name": hcp.name,
                    "specialty": hcp.specialty,
                    "institution": hcp.institution,
                    "city": hcp.city,
                    "state": hcp.state,
                    "tier": hcp.tier.value,
                    "relationship_score": hcp.relationship_score,
                    "engagement_trend": eng.get("engagement_trend", "stable"),
                    "visit_count": eng.get("visit_count", 0),
                    "last_product_discussed": eng.get("last_product_discussed"),
                    "buying_interest": eng.get("buying_interest", "unknown"),
                    "last_interaction_date": last_date.isoformat() if last_date else None,
                    "preferred_contact": hcp.preferred_contact_method,
                })

            return json.dumps({"success": True, "results": results}, default=_serialize_date)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════
# Tool 4: Interaction Timeline
# ═══════════════════════════════════════════════════════════

@tool
async def interaction_timeline(
    hcp_name: str,
    limit: int = 10,
) -> str:
    """View interaction history for an HCP.

    Args:
        hcp_name: HCP name
        limit: Max results (default 10)
    """
    async with await _get_session() as session:
        try:
            # Find HCP
            result = await session.execute(
                select(HCP).where(HCP.name.ilike(f"%{hcp_name}%"))
            )
            hcp = result.scalar_one_or_none()

            if not hcp:
                return json.dumps({"success": False, "error": f"HCP '{hcp_name}' not found."})

            # Get interactions
            result = await session.execute(
                select(Interaction)
                .where(Interaction.hcp_id == hcp.id)
                .order_by(Interaction.interaction_date.desc())
                .limit(limit)
            )
            interactions = result.scalars().all()

            # Get pending follow-ups
            fu_result = await session.execute(
                select(FollowUp)
                .where(FollowUp.hcp_id == hcp.id)
                .where(FollowUp.status.in_([FollowUpStatus.PENDING, FollowUpStatus.OVERDUE]))
                .order_by(FollowUp.due_date)
            )
            follow_ups = fu_result.scalars().all()

            timeline = []
            for i in interactions:
                timeline.append({
                    "id": i.id,
                    "date": i.interaction_date.isoformat(),
                    "type": i.interaction_type.value,
                    "products": i.products_discussed,
                    "sentiment": i.sentiment.value,
                    "sentiment_score": i.sentiment_score,
                    "ai_summary": i.ai_summary,
                    "ai_executive_summary": i.ai_executive_summary,
                    "strategic_insight": i.strategic_insight,
                    "location": i.location,
                    "duration_minutes": i.duration_minutes,
                    "samples_dropped": i.samples_dropped,
                })

            pending_fus = []
            for fu in follow_ups:
                pending_fus.append({
                    "id": fu.id,
                    "due_date": fu.due_date.isoformat(),
                    "action": fu.action_description,
                    "status": fu.status.value,
                    "priority": fu.priority.value,
                    "ai_suggested_actions": fu.ai_suggested_actions,
                })

            # Compute trend
            sentiments = [i.sentiment_score for i in interactions]
            trend = "stable"
            if len(sentiments) >= 2:
                recent = sum(sentiments[:len(sentiments)//2]) / max(len(sentiments)//2, 1)
                older = sum(sentiments[len(sentiments)//2:]) / max(len(sentiments) - len(sentiments)//2, 1)
                if recent > older + 0.1:
                    trend = "growing"
                elif recent < older - 0.1:
                    trend = "declining"

            eng = hcp.engagement_data or {}

            return json.dumps({
                "success": True,
                "hcp": {
                    "id": hcp.id,
                    "name": hcp.name,
                    "specialty": hcp.specialty,
                    "institution": hcp.institution,
                    "tier": hcp.tier.value,
                    "relationship_score": hcp.relationship_score,
                    "engagement_trend": trend,
                },
                "timeline": timeline,
                "pending_follow_ups": pending_fus,
                "total_interactions": len(interactions),
                "avg_sentiment": sum(sentiments) / max(len(sentiments), 1) if sentiments else 0,
            }, default=_serialize_date)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════
# Tool 5: Next Best Action Engine
# ═══════════════════════════════════════════════════════════

@tool
async def next_best_action(
    hcp_name: str,
    opportunity_score: Optional[int] = None,
    reasoning: Optional[str] = None,
    recommended_actions: Optional[str] = None,
    suggested_products: Optional[str] = None,
    meeting_prep: Optional[dict] = None,
) -> str:
    """Get next best action recommendations for an HCP.

    Args:
        hcp_name: HCP name
        opportunity_score: Score 0-100
        reasoning: Reasons for score
        recommended_actions: Suggested actions
        suggested_products: Products to discuss
        meeting_prep: Prep data
    """
    async with await _get_session() as session:
        try:
            result = await session.execute(
                select(HCP).where(HCP.name.ilike(f"%{hcp_name}%"))
            )
            hcp = result.scalar_one_or_none()

            if not hcp:
                return json.dumps({"success": False, "error": f"HCP '{hcp_name}' not found."})

            # Get recent interactions for context
            int_result = await session.execute(
                select(Interaction)
                .where(Interaction.hcp_id == hcp.id)
                .order_by(Interaction.interaction_date.desc())
                .limit(5)
            )
            interactions = int_result.scalars().all()

            # Get pending follow-ups
            fu_result = await session.execute(
                select(FollowUp)
                .where(FollowUp.hcp_id == hcp.id)
                .where(FollowUp.status.in_([FollowUpStatus.PENDING, FollowUpStatus.OVERDUE]))
            )
            follow_ups = fu_result.scalars().all()

            eng = hcp.engagement_data or {}

            # Build context for the AI
            context = {
                "hcp": {
                    "name": hcp.name,
                    "specialty": hcp.specialty,
                    "institution": hcp.institution,
                    "tier": hcp.tier.value,
                    "relationship_score": hcp.relationship_score,
                    "engagement_trend": eng.get("engagement_trend", "stable"),
                    "buying_interest": eng.get("buying_interest", "unknown"),
                    "typical_objections": eng.get("typical_objections", []),
                    "last_product_discussed": eng.get("last_product_discussed"),
                },
                "recent_interactions": [
                    {
                        "date": i.interaction_date.isoformat(),
                        "sentiment": i.sentiment.value,
                        "products": i.products_discussed,
                        "summary": i.ai_summary,
                    }
                    for i in interactions
                ],
                "pending_follow_ups": [
                    {
                        "action": fu.action_description,
                        "due_date": fu.due_date.isoformat(),
                        "status": fu.status.value,
                        "priority": fu.priority.value,
                    }
                    for fu in follow_ups
                ],
                "opportunity_score": opportunity_score,
                "reasoning": reasoning.split(",") if isinstance(reasoning, str) else reasoning,
                "recommended_actions": recommended_actions.split(",") if isinstance(recommended_actions, str) else recommended_actions,
                "suggested_products": suggested_products.split(",") if isinstance(suggested_products, str) else suggested_products,
                "meeting_prep": meeting_prep,
            }

            return json.dumps({
                "success": True,
                **context,
            }, default=_serialize_date)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════
# Tool 6: Compliance Guardian
# ═══════════════════════════════════════════════════════════

@tool
async def compliance_guardian(
    text: str,
    status: Optional[str] = "clean",
    flags: Optional[str] = None,
    severity: Optional[str] = "none",
    recommendation: Optional[str] = None,
) -> str:
    """Check text for pharma compliance violations.

    Args:
        text: Text to check
        status: clean, warning, or violation
        flags: Compliance flags
        severity: none, low, medium, high, critical
        recommendation: Suggested action
    """
    return json.dumps({
        "success": True,
        "text_checked": text[:200] + "..." if len(text) > 200 else text,
        "status": status,
        "flags": flags.split(",") if isinstance(flags, str) else (flags or []),
        "severity": severity,
        "recommendation": recommendation or ("No compliance issues detected." if status == "clean" else "Review flagged content with compliance team."),
    })
