"""Pydantic schemas for API request/response models."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# ── Chat ──

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    tool_calls: list[dict] = []
    tool_results: list[dict] = []
    elapsed_time: float = 0.0
    model: str = "llama-3.3-70b-versatile"


# ── Interactions ──

class InteractionCreate(BaseModel):
    hcp_id: int
    interaction_date: Optional[str] = None
    interaction_type: str = "in-person"
    products_discussed: list[str] = []
    key_topics: Optional[str] = None
    sentiment: str = "neutral"
    follow_up_date: Optional[str] = None
    follow_up_actions: Optional[str] = None
    notes: Optional[str] = None
    samples_dropped: list[str] = []
    duration_minutes: Optional[int] = None
    location: Optional[str] = None


class InteractionUpdate(BaseModel):
    sentiment: Optional[str] = None
    key_topics: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[str] = None
    follow_up_actions: Optional[str] = None
    products_discussed: Optional[list[str]] = None


class InteractionResponse(BaseModel):
    id: int
    hcp_id: int
    hcp_name: str
    hcp_specialty: str
    user_id: int
    interaction_date: str
    interaction_type: str
    products_discussed: list
    key_topics: Optional[str]
    sentiment: str
    sentiment_score: float
    follow_up_date: Optional[str]
    follow_up_actions: Optional[str]
    ai_summary: Optional[str]
    ai_executive_summary: Optional[dict]
    ai_confidence: Optional[float]
    entities_extracted: Optional[dict]
    compliance_flags: Optional[dict]
    strategic_insight: Optional[str]
    notes: Optional[str]
    samples_dropped: list
    duration_minutes: Optional[int]
    location: Optional[str]
    relationship_score: Optional[float]
    created_at: str
    updated_at: Optional[str]


# ── HCP ──

class HCPResponse(BaseModel):
    id: int
    name: str
    specialty: str
    institution: str
    city: Optional[str]
    state: Optional[str]
    tier: str
    relationship_score: float
    engagement_data: dict
    preferred_contact_method: Optional[str]
    last_interaction_date: Optional[str] = None
    interaction_count: int = 0


# ── Dashboard ──

class DashboardStats(BaseModel):
    todays_visits: int
    pending_follow_ups: int
    overdue_follow_ups: int
    weeks_interactions: int
    avg_sentiment: float
    ai_focus: list[dict]
    recent_activity: list[dict]
    upcoming_follow_ups: list[dict]


# ── Follow-ups ──

class FollowUpResponse(BaseModel):
    id: int
    interaction_id: Optional[int]
    hcp_id: int
    hcp_name: str
    due_date: str
    action_description: str
    ai_suggested_actions: list
    status: str
    priority: str
    completed_at: Optional[str]


class FollowUpUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[str] = None


# ── Analytics ──

class AnalyticsData(BaseModel):
    interactions_per_week: list[dict]
    top_products: list[dict]
    sentiment_distribution: dict
    follow_up_completion_rate: float
    top_hcps: list[dict]


# ── Search ──

class SearchResponse(BaseModel):
    hcps: list[dict]
    interactions: list[dict]
