"""API routes for MediFlow AI CRM."""

import json
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, case
from sqlalchemy.orm import selectinload

from database.db import get_db
from database.models import (
    User, HCP, Interaction, FollowUp, AuditLog,
    InteractionType, Sentiment, FollowUpStatus, Priority
)
from auth.auth import get_current_user
from agent.graph import invoke_agent, get_llm
from agent.prompts import MEETING_BRIEF_PROMPT
from api.schemas import (
    ChatRequest, ChatResponse,
    InteractionCreate, InteractionUpdate, InteractionResponse,
    HCPResponse, DashboardStats, FollowUpResponse, FollowUpUpdate,
    AnalyticsData, SearchResponse,
)

router = APIRouter(prefix="/api", tags=["api"])


# ═══════════════════════════════════════════════════
# Chat (LangGraph Agent)
# ═══════════════════════════════════════════════════

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a message to the MediFlow AI copilot."""
    thread_id = request.thread_id or str(uuid.uuid4())
    result = await invoke_agent(
        message=request.message,
        thread_id=thread_id,
        user_id=current_user.id,
    )
    return ChatResponse(**result)


# ═══════════════════════════════════════════════════
# Interactions
# ═══════════════════════════════════════════════════

@router.get("/interactions")
async def list_interactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    hcp_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List interactions with filtering and pagination."""
    query = (
        select(Interaction)
        .where(Interaction.user_id == current_user.id)
        .order_by(Interaction.interaction_date.desc(), Interaction.created_at.desc())
    )

    if hcp_id:
        query = query.where(Interaction.hcp_id == hcp_id)
    if sentiment:
        sent_map = {"positive": Sentiment.POSITIVE, "neutral": Sentiment.NEUTRAL, "negative": Sentiment.NEGATIVE}
        if sentiment in sent_map:
            query = query.where(Interaction.sentiment == sent_map[sentiment])
    if interaction_type:
        type_map = {"in-person": InteractionType.IN_PERSON, "virtual": InteractionType.VIRTUAL, "phone": InteractionType.PHONE, "email": InteractionType.EMAIL}
        if interaction_type in type_map:
            query = query.where(Interaction.interaction_type == type_map[interaction_type])
    if date_from:
        query = query.where(Interaction.interaction_date >= date.fromisoformat(date_from))
    if date_to:
        query = query.where(Interaction.interaction_date <= date.fromisoformat(date_to))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    interactions = result.scalars().all()

    # Build response with HCP info
    items = []
    for i in interactions:
        hcp_result = await db.execute(select(HCP).where(HCP.id == i.hcp_id))
        hcp = hcp_result.scalar_one_or_none()
        items.append({
            "id": i.id,
            "hcp_id": i.hcp_id,
            "hcp_name": hcp.name if hcp else "Unknown",
            "hcp_specialty": hcp.specialty if hcp else "",
            "interaction_date": i.interaction_date.isoformat(),
            "interaction_type": i.interaction_type.value,
            "products_discussed": i.products_discussed,
            "key_topics": i.key_topics,
            "sentiment": i.sentiment.value,
            "sentiment_score": i.sentiment_score,
            "ai_summary": i.ai_summary,
            "ai_executive_summary": i.ai_executive_summary,
            "ai_confidence": i.ai_confidence,
            "entities_extracted": i.entities_extracted,
            "compliance_flags": i.compliance_flags,
            "strategic_insight": i.strategic_insight,
            "notes": i.notes,
            "samples_dropped": i.samples_dropped,
            "duration_minutes": i.duration_minutes,
            "location": i.location,
            "follow_up_date": i.follow_up_date.isoformat() if i.follow_up_date else None,
            "follow_up_actions": i.follow_up_actions,
            "relationship_score": hcp.relationship_score if hcp else None,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        })

    return {"items": items, "total": total, "page": page, "limit": limit}


@router.post("/interactions")
async def create_interaction(
    data: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new interaction via the structured form."""
    # Verify HCP exists
    hcp_result = await db.execute(select(HCP).where(HCP.id == data.hcp_id))
    hcp = hcp_result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    type_map = {"in-person": InteractionType.IN_PERSON, "virtual": InteractionType.VIRTUAL, "phone": InteractionType.PHONE, "email": InteractionType.EMAIL}
    sent_map = {"positive": Sentiment.POSITIVE, "neutral": Sentiment.NEUTRAL, "negative": Sentiment.NEGATIVE}

    i_date = date.fromisoformat(data.interaction_date) if data.interaction_date else date.today()
    f_date = date.fromisoformat(data.follow_up_date) if data.follow_up_date else None

    # Generate AI summary via the agent
    summary_text = f"Interaction with {hcp.name} on {i_date}. "
    if data.products_discussed:
        summary_text += f"Products: {', '.join(data.products_discussed)}. "
    if data.key_topics:
        summary_text += f"Topics: {data.key_topics}. "
    summary_text += f"Sentiment: {data.sentiment}."

    # Use the agent for AI processing
    try:
        agent_result = await invoke_agent(
            message=f"Generate an executive summary, strategic insight, and compliance check for this interaction: {summary_text}. The HCP is {hcp.name}, a {hcp.specialty} at {hcp.institution}. Respond with just the analysis, don't call any tools.",
            thread_id=f"form-{uuid.uuid4()}",
            user_id=current_user.id,
        )
        ai_summary = agent_result.get("response", summary_text)
    except Exception:
        ai_summary = summary_text

    interaction = Interaction(
        hcp_id=data.hcp_id,
        user_id=current_user.id,
        interaction_date=i_date,
        interaction_type=type_map.get(data.interaction_type, InteractionType.IN_PERSON),
        products_discussed=data.products_discussed,
        key_topics=data.key_topics,
        sentiment=sent_map.get(data.sentiment, Sentiment.NEUTRAL),
        sentiment_score={"positive": 0.85, "neutral": 0.5, "negative": 0.2}.get(data.sentiment, 0.5),
        follow_up_date=f_date,
        follow_up_actions=data.follow_up_actions,
        ai_summary=ai_summary,
        ai_confidence=0.85,
        compliance_flags={"status": "clean", "flags": []},
        notes=data.notes,
        samples_dropped=data.samples_dropped,
        duration_minutes=data.duration_minutes,
        location=data.location,
    )
    db.add(interaction)

    # Create follow-up if date provided
    if f_date:
        follow_up = FollowUp(
            interaction_id=None,  # Will be set after flush
            hcp_id=data.hcp_id,
            user_id=current_user.id,
            due_date=f_date,
            action_description=data.follow_up_actions or "Follow up",
            ai_suggested_actions=[],
            status=FollowUpStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        db.add(follow_up)

    # Update HCP engagement
    eng = hcp.engagement_data or {}
    eng["visit_count"] = eng.get("visit_count", 0) + 1
    if data.products_discussed:
        eng["last_product_discussed"] = data.products_discussed[0]
    eng["last_sentiment"] = data.sentiment
    hcp.engagement_data = eng
    score_delta = 3 if data.sentiment == "positive" else (-2 if data.sentiment == "negative" else 0)
    hcp.relationship_score = min(100, max(0, (hcp.relationship_score or 50) + score_delta))

    await db.flush()

    # Update follow-up interaction_id
    if f_date and follow_up:
        follow_up.interaction_id = interaction.id

    return {
        "id": interaction.id,
        "hcp_name": hcp.name,
        "ai_summary": ai_summary,
        "message": "Interaction logged successfully",
    }


@router.put("/interactions/{interaction_id}")
async def update_interaction(
    interaction_id: int,
    data: InteractionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing interaction."""
    result = await db.execute(
        select(Interaction).where(
            Interaction.id == interaction_id,
            Interaction.user_id == current_user.id,
        )
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    old_values = {}
    new_values = {}

    sent_map = {"positive": Sentiment.POSITIVE, "neutral": Sentiment.NEUTRAL, "negative": Sentiment.NEGATIVE}

    if data.sentiment is not None and data.sentiment in sent_map:
        old_values["sentiment"] = interaction.sentiment.value
        interaction.sentiment = sent_map[data.sentiment]
        new_values["sentiment"] = data.sentiment
    if data.key_topics is not None:
        old_values["key_topics"] = interaction.key_topics
        interaction.key_topics = data.key_topics
        new_values["key_topics"] = data.key_topics
    if data.notes is not None:
        old_values["notes"] = interaction.notes
        interaction.notes = data.notes
        new_values["notes"] = data.notes
    if data.follow_up_date is not None:
        old_values["follow_up_date"] = str(interaction.follow_up_date)
        interaction.follow_up_date = date.fromisoformat(data.follow_up_date)
        new_values["follow_up_date"] = data.follow_up_date
    if data.follow_up_actions is not None:
        old_values["follow_up_actions"] = interaction.follow_up_actions
        interaction.follow_up_actions = data.follow_up_actions
        new_values["follow_up_actions"] = data.follow_up_actions
    if data.products_discussed is not None:
        old_values["products_discussed"] = interaction.products_discussed
        interaction.products_discussed = data.products_discussed
        new_values["products_discussed"] = data.products_discussed

    interaction.updated_at = datetime.utcnow()

    audit = AuditLog(
        user_id=current_user.id,
        action="update",
        entity_type="interaction",
        entity_id=interaction_id,
        old_values=old_values,
        new_values=new_values,
    )
    db.add(audit)

    return {"message": "Interaction updated", "updated_fields": list(new_values.keys())}


@router.get("/interactions/{interaction_id}")
async def get_interaction(
    interaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single interaction with full details."""
    result = await db.execute(
        select(Interaction).where(
            Interaction.id == interaction_id,
            Interaction.user_id == current_user.id,
        )
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    hcp_result = await db.execute(select(HCP).where(HCP.id == interaction.hcp_id))
    hcp = hcp_result.scalar_one_or_none()

    return {
        "id": interaction.id,
        "hcp_id": interaction.hcp_id,
        "hcp_name": hcp.name if hcp else "Unknown",
        "hcp_specialty": hcp.specialty if hcp else "",
        "interaction_date": interaction.interaction_date.isoformat(),
        "interaction_type": interaction.interaction_type.value,
        "products_discussed": interaction.products_discussed,
        "key_topics": interaction.key_topics,
        "sentiment": interaction.sentiment.value,
        "sentiment_score": interaction.sentiment_score,
        "ai_summary": interaction.ai_summary,
        "ai_executive_summary": interaction.ai_executive_summary,
        "ai_confidence": interaction.ai_confidence,
        "entities_extracted": interaction.entities_extracted,
        "compliance_flags": interaction.compliance_flags,
        "strategic_insight": interaction.strategic_insight,
        "notes": interaction.notes,
        "samples_dropped": interaction.samples_dropped,
        "duration_minutes": interaction.duration_minutes,
        "location": interaction.location,
        "follow_up_date": interaction.follow_up_date.isoformat() if interaction.follow_up_date else None,
        "follow_up_actions": interaction.follow_up_actions,
        "relationship_score": hcp.relationship_score if hcp else None,
        "created_at": interaction.created_at.isoformat() if interaction.created_at else None,
    }


# ═══════════════════════════════════════════════════
# HCPs
# ═══════════════════════════════════════════════════

@router.get("/hcps")
async def list_hcps(
    search: Optional[str] = None,
    specialty: Optional[str] = None,
    tier: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List and search HCPs."""
    query = select(HCP).order_by(HCP.relationship_score.desc())

    if search:
        s = f"%{search}%"
        query = query.where(
            or_(HCP.name.ilike(s), HCP.institution.ilike(s), HCP.city.ilike(s))
        )
    if specialty:
        query = query.where(HCP.specialty.ilike(f"%{specialty}%"))
    if tier:
        from database.models import HCPTier
        tier_map = {"A": HCPTier.A, "B": HCPTier.B, "C": HCPTier.C}
        if tier in tier_map:
            query = query.where(HCP.tier == tier_map[tier])

    result = await db.execute(query)
    hcps = result.scalars().all()

    items = []
    for hcp in hcps:
        # Get interaction count and last date
        count_result = await db.execute(
            select(func.count()).select_from(Interaction).where(Interaction.hcp_id == hcp.id)
        )
        count = count_result.scalar()

        last_result = await db.execute(
            select(Interaction.interaction_date)
            .where(Interaction.hcp_id == hcp.id)
            .order_by(Interaction.interaction_date.desc())
            .limit(1)
        )
        last_date = last_result.scalar_one_or_none()

        items.append({
            "id": hcp.id,
            "name": hcp.name,
            "specialty": hcp.specialty,
            "institution": hcp.institution,
            "city": hcp.city,
            "state": hcp.state,
            "tier": hcp.tier.value,
            "relationship_score": hcp.relationship_score,
            "engagement_data": hcp.engagement_data,
            "preferred_contact_method": hcp.preferred_contact_method,
            "interaction_count": count,
            "last_interaction_date": last_date.isoformat() if last_date else None,
        })

    return {"items": items}


@router.get("/hcps/{hcp_id}")
async def get_hcp(
    hcp_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get HCP detail with engagement data."""
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    count_result = await db.execute(
        select(func.count()).select_from(Interaction).where(Interaction.hcp_id == hcp.id)
    )

    return {
        "id": hcp.id,
        "name": hcp.name,
        "specialty": hcp.specialty,
        "institution": hcp.institution,
        "city": hcp.city,
        "state": hcp.state,
        "tier": hcp.tier.value,
        "relationship_score": hcp.relationship_score,
        "engagement_data": hcp.engagement_data,
        "preferred_contact_method": hcp.preferred_contact_method,
        "interaction_count": count_result.scalar(),
    }


@router.get("/hcps/{hcp_id}/meeting-brief")
async def get_meeting_brief(
    hcp_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI Meeting Brief for pre-visit preparation."""
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    # Get interactions
    int_result = await db.execute(
        select(Interaction)
        .where(Interaction.hcp_id == hcp_id)
        .order_by(Interaction.interaction_date.desc())
        .limit(10)
    )
    interactions = int_result.scalars().all()

    # Get follow-ups
    fu_result = await db.execute(
        select(FollowUp)
        .where(FollowUp.hcp_id == hcp_id)
        .where(FollowUp.status.in_([FollowUpStatus.PENDING, FollowUpStatus.OVERDUE]))
    )
    follow_ups = fu_result.scalars().all()

    # Build context for LLM
    history_text = f"HCP: {hcp.name}, {hcp.specialty} at {hcp.institution}.\n"
    history_text += f"Tier: {hcp.tier.value}, Relationship Score: {hcp.relationship_score}\n\n"

    eng = hcp.engagement_data or {}
    history_text += f"Engagement: {eng.get('visit_count', 0)} visits, "
    history_text += f"trend: {eng.get('engagement_trend', 'stable')}, "
    history_text += f"buying interest: {eng.get('buying_interest', 'unknown')}\n"
    history_text += f"Typical objections: {', '.join(eng.get('typical_objections', []))}\n\n"

    history_text += "Interaction History:\n"
    for i in interactions:
        history_text += f"- {i.interaction_date}: {i.interaction_type.value}, {i.sentiment.value}, "
        history_text += f"Products: {', '.join(i.products_discussed or [])}\n"
        if i.ai_summary:
            history_text += f"  Summary: {i.ai_summary}\n"

    history_text += "\nPending Follow-ups:\n"
    for fu in follow_ups:
        history_text += f"- {fu.due_date}: {fu.action_description} ({fu.status.value}, {fu.priority.value})\n"

    # Generate meeting brief via agent
    try:
        brief_result = await invoke_agent(
            message=f"{MEETING_BRIEF_PROMPT}\n\nHere is the interaction history:\n{history_text}",
            thread_id=f"brief-{hcp_id}-{uuid.uuid4()}",
            user_id=current_user.id,
        )
        brief_response = brief_result.get("response", "")

        # Try to parse JSON from response
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', brief_response)
            if json_match:
                brief_data = json.loads(json_match.group())
            else:
                brief_data = None
        except (json.JSONDecodeError, Exception):
            brief_data = None

        if not brief_data:
            # Fallback structured brief
            last_int = interactions[0] if interactions else None
            brief_data = {
                "last_meeting": {
                    "date": last_int.interaction_date.isoformat() if last_int else "N/A",
                    "summary": last_int.ai_summary if last_int else "No previous meetings",
                    "sentiment": last_int.sentiment.value if last_int else "N/A",
                },
                "products_history": [
                    {"name": eng.get("last_product_discussed", "N/A"), "meetings_discussed": eng.get("visit_count", 0), "reception": eng.get("buying_interest", "unknown")}
                ],
                "talking_points": [
                    f"Follow up on {eng.get('last_product_discussed', 'previous discussion')}",
                    f"Address concerns about {', '.join(eng.get('typical_objections', ['N/A']))}",
                    "Share latest clinical data",
                ],
                "expected_questions": eng.get("typical_objections", ["No known objections"]),
                "open_follow_ups": [
                    {"action": fu.action_description, "status": fu.status.value, "priority": fu.priority.value}
                    for fu in follow_ups
                ],
                "opportunity_score": int(hcp.relationship_score),
                "engagement_trend": eng.get("engagement_trend", "stable"),
                "engagement_reasoning": f"Based on {eng.get('visit_count', 0)} visits with {eng.get('buying_interest', 'unknown')} buying interest.",
            }

    except Exception as e:
        brief_data = {"error": str(e), "message": "Could not generate meeting brief."}

    return {
        "hcp": {
            "name": hcp.name,
            "specialty": hcp.specialty,
            "institution": hcp.institution,
            "tier": hcp.tier.value,
            "relationship_score": hcp.relationship_score,
        },
        "brief": brief_data,
        "model": "gemma2-9b-it",
    }


# ═══════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard stats and AI focus items."""
    today = date.today()
    week_ago = today - timedelta(days=7)

    # Today's visits
    today_count = await db.execute(
        select(func.count()).select_from(Interaction).where(
            Interaction.user_id == current_user.id,
            Interaction.interaction_date == today,
        )
    )
    todays_visits = today_count.scalar()

    # Week's interactions
    week_count = await db.execute(
        select(func.count()).select_from(Interaction).where(
            Interaction.user_id == current_user.id,
            Interaction.interaction_date >= week_ago,
        )
    )
    weeks_interactions = week_count.scalar()

    # Pending follow-ups
    pending_result = await db.execute(
        select(func.count()).select_from(FollowUp).where(
            FollowUp.user_id == current_user.id,
            FollowUp.status == FollowUpStatus.PENDING,
        )
    )
    pending = pending_result.scalar()

    # Overdue follow-ups
    overdue_result = await db.execute(
        select(func.count()).select_from(FollowUp).where(
            FollowUp.user_id == current_user.id,
            FollowUp.status == FollowUpStatus.OVERDUE,
        )
    )

    # Also check pending that are past due
    overdue_pending = await db.execute(
        select(func.count()).select_from(FollowUp).where(
            FollowUp.user_id == current_user.id,
            FollowUp.status == FollowUpStatus.PENDING,
            FollowUp.due_date < today,
        )
    )
    overdue = overdue_result.scalar() + overdue_pending.scalar()

    # Avg sentiment this week
    avg_sent = await db.execute(
        select(func.avg(Interaction.sentiment_score)).where(
            Interaction.user_id == current_user.id,
            Interaction.interaction_date >= week_ago,
        )
    )
    avg_sentiment = round((avg_sent.scalar() or 0.5) * 100)

    # Recent activity (last 5 interactions)
    recent_result = await db.execute(
        select(Interaction)
        .where(Interaction.user_id == current_user.id)
        .order_by(Interaction.interaction_date.desc(), Interaction.created_at.desc())
        .limit(5)
    )
    recent_interactions = recent_result.scalars().all()

    recent_activity = []
    for i in recent_interactions:
        hcp_r = await db.execute(select(HCP).where(HCP.id == i.hcp_id))
        hcp = hcp_r.scalar_one_or_none()
        recent_activity.append({
            "id": i.id,
            "hcp_name": hcp.name if hcp else "Unknown",
            "hcp_specialty": hcp.specialty if hcp else "",
            "interaction_date": i.interaction_date.isoformat(),
            "interaction_type": i.interaction_type.value,
            "sentiment": i.sentiment.value,
            "ai_summary": i.ai_summary[:100] + "..." if i.ai_summary and len(i.ai_summary) > 100 else i.ai_summary,
            "products": i.products_discussed,
        })

    # Upcoming follow-ups
    upcoming_result = await db.execute(
        select(FollowUp)
        .where(
            FollowUp.user_id == current_user.id,
            FollowUp.status.in_([FollowUpStatus.PENDING, FollowUpStatus.OVERDUE]),
        )
        .order_by(FollowUp.due_date)
        .limit(5)
    )
    upcoming_fus = upcoming_result.scalars().all()

    upcoming_follow_ups = []
    for fu in upcoming_fus:
        hcp_r = await db.execute(select(HCP).where(HCP.id == fu.hcp_id))
        hcp = hcp_r.scalar_one_or_none()

        status = fu.status.value
        if fu.status == FollowUpStatus.PENDING and fu.due_date < today:
            status = "overdue"

        upcoming_follow_ups.append({
            "id": fu.id,
            "hcp_name": hcp.name if hcp else "Unknown",
            "due_date": fu.due_date.isoformat(),
            "action": fu.action_description,
            "status": status,
            "priority": fu.priority.value,
            "ai_suggested_actions": fu.ai_suggested_actions,
        })

    # AI Focus items — find priority doctor, opportunity, compliance reminder
    ai_focus = []

    # Priority doctor (highest relationship score with recent interaction)
    top_hcp_result = await db.execute(
        select(HCP)
        .join(Interaction, Interaction.hcp_id == HCP.id)
        .where(Interaction.user_id == current_user.id)
        .order_by(HCP.relationship_score.desc())
        .limit(1)
    )
    top_hcp = top_hcp_result.scalar_one_or_none()
    if top_hcp:
        eng = top_hcp.engagement_data or {}
        ai_focus.append({
            "type": "priority",
            "icon": "🎯",
            "title": f"Priority: {top_hcp.name}",
            "description": f"Relationship at {int(top_hcp.relationship_score)}%. "
                          f"{eng.get('engagement_trend', 'Stable').capitalize()} interest in {eng.get('last_product_discussed', 'your products')}. "
                          f"Consider scheduling a follow-up.",
        })

    # Opportunity — HCP with growing interest
    opp_result = await db.execute(
        select(HCP).where(HCP.relationship_score >= 70).order_by(HCP.relationship_score.desc()).limit(3)
    )
    opp_hcps = opp_result.scalars().all()
    for opp in opp_hcps[1:2]:  # Second highest
        eng = opp.engagement_data or {}
        if eng.get("engagement_trend") == "growing" or eng.get("buying_interest") == "high":
            ai_focus.append({
                "type": "opportunity",
                "icon": "💡",
                "title": f"Opportunity: {opp.name}",
                "description": f"Shows buying signals ({eng.get('buying_interest', 'moderate')} interest). "
                              f"Recommend in-person follow-up this week.",
            })

    # Overdue items
    if overdue > 0:
        ai_focus.append({
            "type": "warning",
            "icon": "⚠️",
            "title": f"Overdue: {overdue} follow-up{'s' if overdue > 1 else ''}",
            "description": "Review and complete overdue follow-ups to maintain relationship health.",
        })

    return {
        "greeting": current_user.full_name.split()[0],
        "todays_visits": todays_visits,
        "pending_follow_ups": pending,
        "overdue_follow_ups": overdue,
        "weeks_interactions": weeks_interactions,
        "avg_sentiment": avg_sentiment,
        "ai_focus": ai_focus,
        "recent_activity": recent_activity,
        "upcoming_follow_ups": upcoming_follow_ups,
    }


# ═══════════════════════════════════════════════════
# Follow-ups
# ═══════════════════════════════════════════════════

@router.get("/follow-ups")
async def list_follow_ups(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List follow-ups, optionally filtered by status."""
    query = (
        select(FollowUp)
        .where(FollowUp.user_id == current_user.id)
        .order_by(FollowUp.due_date)
    )

    if status:
        status_map = {"pending": FollowUpStatus.PENDING, "completed": FollowUpStatus.COMPLETED, "overdue": FollowUpStatus.OVERDUE}
        if status in status_map:
            query = query.where(FollowUp.status == status_map[status])

    result = await db.execute(query)
    follow_ups = result.scalars().all()

    items = []
    for fu in follow_ups:
        hcp_r = await db.execute(select(HCP).where(HCP.id == fu.hcp_id))
        hcp = hcp_r.scalar_one_or_none()

        s = fu.status.value
        if fu.status == FollowUpStatus.PENDING and fu.due_date < date.today():
            s = "overdue"

        items.append({
            "id": fu.id,
            "interaction_id": fu.interaction_id,
            "hcp_id": fu.hcp_id,
            "hcp_name": hcp.name if hcp else "Unknown",
            "due_date": fu.due_date.isoformat(),
            "action_description": fu.action_description,
            "ai_suggested_actions": fu.ai_suggested_actions,
            "status": s,
            "priority": fu.priority.value,
            "completed_at": fu.completed_at.isoformat() if fu.completed_at else None,
        })

    return {"items": items}


@router.put("/follow-ups/{follow_up_id}")
async def update_follow_up(
    follow_up_id: int,
    data: FollowUpUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a follow-up (e.g., mark as completed)."""
    result = await db.execute(
        select(FollowUp).where(
            FollowUp.id == follow_up_id,
            FollowUp.user_id == current_user.id,
        )
    )
    fu = result.scalar_one_or_none()
    if not fu:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    if data.status == "completed":
        fu.status = FollowUpStatus.COMPLETED
        fu.completed_at = datetime.utcnow()
    elif data.status:
        status_map = {"pending": FollowUpStatus.PENDING, "overdue": FollowUpStatus.OVERDUE}
        if data.status in status_map:
            fu.status = status_map[data.status]

    return {"message": "Follow-up updated", "status": fu.status.value}


# ═══════════════════════════════════════════════════
# Analytics
# ═══════════════════════════════════════════════════

@router.get("/analytics")
async def get_analytics(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics chart data."""
    start_date = date.today() - timedelta(days=days)

    # Interactions per week
    result = await db.execute(
        select(Interaction)
        .where(
            Interaction.user_id == current_user.id,
            Interaction.interaction_date >= start_date,
        )
        .order_by(Interaction.interaction_date)
    )
    interactions = result.scalars().all()

    # Group by week
    weeks = {}
    for i in interactions:
        week_start = i.interaction_date - timedelta(days=i.interaction_date.weekday())
        key = week_start.isoformat()
        weeks[key] = weeks.get(key, 0) + 1

    interactions_per_week = [{"week": k, "count": v} for k, v in sorted(weeks.items())]

    # Top products
    product_counts = {}
    for i in interactions:
        for p in (i.products_discussed or []):
            product_counts[p] = product_counts.get(p, 0) + 1

    top_products = sorted(
        [{"name": k, "count": v} for k, v in product_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:8]

    # Sentiment distribution
    sent_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for i in interactions:
        sent_counts[i.sentiment.value] = sent_counts.get(i.sentiment.value, 0) + 1

    # Follow-up completion rate
    total_fus = await db.execute(
        select(func.count()).select_from(FollowUp).where(FollowUp.user_id == current_user.id)
    )
    completed_fus = await db.execute(
        select(func.count()).select_from(FollowUp).where(
            FollowUp.user_id == current_user.id,
            FollowUp.status == FollowUpStatus.COMPLETED,
        )
    )
    total = total_fus.scalar()
    completed = completed_fus.scalar()
    completion_rate = round((completed / total * 100) if total > 0 else 0)

    # Top HCPs by engagement
    hcp_result = await db.execute(
        select(HCP).order_by(HCP.relationship_score.desc()).limit(5)
    )
    top_hcps_list = hcp_result.scalars().all()

    top_hcps = []
    for hcp in top_hcps_list:
        last_result = await db.execute(
            select(Interaction.interaction_date)
            .where(Interaction.hcp_id == hcp.id)
            .order_by(Interaction.interaction_date.desc())
            .limit(1)
        )
        last_date = last_result.scalar_one_or_none()
        eng = hcp.engagement_data or {}

        top_hcps.append({
            "name": hcp.name,
            "specialty": hcp.specialty,
            "relationship_score": hcp.relationship_score,
            "engagement_trend": eng.get("engagement_trend", "stable"),
            "last_interaction": last_date.isoformat() if last_date else None,
        })

    return {
        "interactions_per_week": interactions_per_week,
        "top_products": top_products,
        "sentiment_distribution": sent_counts,
        "follow_up_completion_rate": completion_rate,
        "top_hcps": top_hcps,
    }


# ═══════════════════════════════════════════════════
# Search
# ═══════════════════════════════════════════════════

@router.get("/search")
async def global_search(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Global search across HCPs and interactions."""
    search = f"%{q}%"

    # Search HCPs
    hcp_result = await db.execute(
        select(HCP).where(
            or_(
                HCP.name.ilike(search),
                HCP.specialty.ilike(search),
                HCP.institution.ilike(search),
                HCP.city.ilike(search),
            )
        ).limit(5)
    )
    hcps = [
        {
            "id": h.id,
            "name": h.name,
            "specialty": h.specialty,
            "institution": h.institution,
            "relationship_score": h.relationship_score,
        }
        for h in hcp_result.scalars().all()
    ]

    # Search interactions
    int_result = await db.execute(
        select(Interaction).where(
            Interaction.user_id == current_user.id,
            or_(
                Interaction.key_topics.ilike(search),
                Interaction.ai_summary.ilike(search),
                Interaction.notes.ilike(search),
            ),
        ).limit(5)
    )
    interaction_items = []
    for i in int_result.scalars().all():
        hcp_r = await db.execute(select(HCP).where(HCP.id == i.hcp_id))
        hcp = hcp_r.scalar_one_or_none()
        interaction_items.append({
            "id": i.id,
            "hcp_name": hcp.name if hcp else "Unknown",
            "date": i.interaction_date.isoformat(),
            "summary": i.ai_summary[:80] + "..." if i.ai_summary and len(i.ai_summary) > 80 else i.ai_summary,
            "sentiment": i.sentiment.value,
        })

    return {"hcps": hcps, "interactions": interaction_items}
