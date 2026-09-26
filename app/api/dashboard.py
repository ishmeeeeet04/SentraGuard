"""
Analyst dashboard endpoints: traffic feed and summary metrics.
Restricted to admin and analyst roles — developers don't need visibility
into org-wide traffic.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.request_log import RequestLog
from app.models.user import User
from app.schemas.dashboard import MetricsResponse, TrafficItem, TrafficListResponse

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/traffic", response_model=TrafficListResponse)
def get_traffic(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_role("admin", "analyst")),
    db: Session = Depends(get_db),
):
    base_query = db.query(RequestLog).filter(RequestLog.org_id == current_user.org_id)

    total = base_query.count()
    items = (
        base_query.order_by(RequestLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return TrafficListResponse(
        items=[TrafficItem.model_validate(item) for item in items],
        total=total,
    )


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    current_user: User = Depends(require_role("admin", "analyst")),
    db: Session = Depends(get_db),
):
    base_query = db.query(RequestLog).filter(RequestLog.org_id == current_user.org_id)

    total = base_query.count()
    blocked = base_query.filter(RequestLog.final_verdict == "block").count()
    safe = total - blocked
    block_rate = round((blocked / total * 100), 2) if total > 0 else 0.0

    return MetricsResponse(
        total_requests=total,
        blocked_requests=blocked,
        safe_requests=safe,
        block_rate_percent=block_rate,
    )