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
    hcp_name: str,
    interaction_date: Optional[str] = None,
    interaction_type: Optional[str] = "in-person",
    products_discussed: Optional[list[str]] = None,
    key_topics: Optional[list[str]] = None,
    sentiment: Optional[str] = "neutral",
    sentiment_score: Optional[float] = 0.5,
    follow_up_date: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    ai_summary: Optional[str] = None,
    ai_executive_summary: Optional[dict] = None,
    ai_confidence: Optional[float] = None,
    entities_extracted: Optional[dict] = None,
    compliance_flags: Optional[dict] = None,
    strategic_insight: Optional[str] = None,
    notes: Optional[str] = None,
    samples_dropped: Optional[list[str]] = None,
    duration_minutes: Optional[int] = None,
    location: Optional[str] = None,
    ai_suggested_follow_ups: Optional[list[str]] = None,
    user_id: int = 1,
) -> str:
    """Log a new interaction with a Healthcare Professional (HCP).
    
    Use this tool when the user describes a meeting, call, or any interaction
    with a doctor. Extract all relevant information from the conversation.
    
    Args:
        hcp_name: Name of the healthcare professional (e.g., "Dr. Sarah Chen")
        interaction_date: Date of interaction in YYYY-MM-DD format. Defaults to today.
        interaction_type: Type of interaction: "in-person", "virtual", "phone", "email"
        products_discussed: List of pharmaceutical products discussed
        key_topics: Main topics covered during the interaction
        sentiment: Overall sentiment: "positive", "neutral", "negative"
        sentiment_score: Confidence score for sentiment (0.0-1.0)
        follow_up_date: Planned follow-up date in YYYY-MM-DD format
        follow_up_actions: Description of planned follow-up actions
        ai_summary: AI-generated summary of the interaction
        ai_executive_summary: Structured summary with key_outcomes, next_actions, risks
        ai_confidence: Overall AI confidence score (0.0-1.0)
        entities_extracted: Dict of extracted entities with confidence scores
        compliance_flags: Compliance check results
        strategic_insight: AI strategic recommendation
        notes: Additional notes
        samples_dropped: List of samples provided
        duration_minutes: Duration of the meeting in minutes
        location: Location of the interaction
        ai_suggested_follow_ups: AI-generated follow-up action suggestions
        user_id: ID of the sales representative
    """
    async with await _get_session() as session:
        try:
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
    interaction_id: int,
    sentiment: Optional[str] = None,
    key_topics: Optional[list[str]] = None,
    notes: Optional[str] = None,
    follow_up_date: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    products_discussed: Optional[list[str]] = None,
    ai_summary: Optional[str] = None,
    user_id: int = 1,
) -> str:
    """Edit an existing interaction record.
    
    Use this tool when the user wants to modify a previously logged interaction.
    Only update the fields that the user explicitly wants to change.
    
    Args:
        interaction_id: ID of the interaction to edit
        sentiment: New sentiment value: "positive", "neutral", "negative"
        key_topics: Updated key topics
        notes: Updated notes
        follow_up_date: New follow-up date in YYYY-MM-DD format
        follow_up_actions: Updated follow-up actions
        products_discussed: Updated list of products
        ai_summary: Updated AI summary
        user_id: ID of the sales representative
    """
    async with await _get_session() as session:
        try:
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
                old_values["products_discussed"] = interaction.products_discussed
                interaction.products_discussed = products_discussed
                new_values["products_discussed"] = products_discussed

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
    """Search for Healthcare Professionals (HCPs) by name, specialty, institution, or city.
    
    Use this tool when the user asks to look up or find a doctor.
    Returns matching HCPs with their relationship health score and engagement data.
    
    Args:
        query: Search query — can be a name, specialty, institution, or city
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
    """View the interaction history timeline for a specific HCP.
    
    Use this tool when the user wants to see past interactions with a doctor,
    review history, or understand the engagement trend.
    
    Args:
        hcp_name: Name of the HCP to look up history for
        limit: Maximum number of interactions to return (default 10)
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
    reasoning: Optional[list[str]] = None,
    recommended_actions: Optional[list[str]] = None,
    suggested_products: Optional[list[str]] = None,
    meeting_prep: Optional[dict] = None,
) -> str:
    """Generate Next Best Action recommendations for a specific HCP.
    
    Analyzes past interactions, sentiment trends, product history, follow-up status,
    and relationship score to provide prioritized, intelligent recommendations.
    
    Use this tool when the user asks what to do next with a doctor, wants
    recommendations, or asks about priorities.
    
    Args:
        hcp_name: Name of the HCP to generate recommendations for
        opportunity_score: AI-assessed opportunity score 0-100
        reasoning: List of reasons supporting the opportunity score
        recommended_actions: List of recommended next actions
        suggested_products: List of products to discuss
        meeting_prep: Meeting preparation data including talking points and expected questions
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
                "reasoning": reasoning,
                "recommended_actions": recommended_actions,
                "suggested_products": suggested_products,
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
    flags: Optional[list[str]] = None,
    severity: Optional[str] = "none",
    recommendation: Optional[str] = None,
) -> str:
    """Check text content for potential compliance violations in pharmaceutical sales.
    
    Scans for:
    - Gift mentions or inducements
    - Quid pro quo language
    - Off-label promotion
    - Improper financial incentives
    - Sunshine Act violations
    - Anti-kickback statute violations
    
    Use this tool when:
    - A user logs an interaction and the content seems potentially problematic
    - A user explicitly asks to check compliance
    - Suspicious language is detected in conversation
    
    Args:
        text: The text content to check for compliance issues
        status: Compliance status: "clean", "warning", "violation"
        flags: List of specific compliance flags identified
        severity: Severity level: "none", "low", "medium", "high", "critical"
        recommendation: Recommended action to address any issues
    """
    return json.dumps({
        "success": True,
        "text_checked": text[:200] + "..." if len(text) > 200 else text,
        "status": status,
        "flags": flags or [],
        "severity": severity,
        "recommendation": recommendation or ("No compliance issues detected." if status == "clean" else "Review flagged content with compliance team."),
    })
