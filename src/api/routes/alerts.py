from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.database import Alert, get_db
from src.api.models import AlertListResponse, AlertResponse

router = APIRouter()


@router.get("/alerts", response_model=AlertListResponse)
async def get_alerts(
    limit:              int           = Query(50, ge=1, le=500),
    offset:             int           = Query(0, ge=0),
    severity:           Optional[str] = None,
    attack_type:        Optional[str] = None,
    hours:              Optional[int] = None,
    unacknowledged_only: bool         = False,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).order_by(desc(Alert.timestamp))

    if severity:
        stmt = stmt.where(Alert.severity_label == severity)
    if attack_type:
        stmt = stmt.where(Alert.attack_type == attack_type)
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = stmt.where(Alert.timestamp >= since)
    if unacknowledged_only:
        stmt = stmt.where(Alert.is_acknowledged == False)

    all_rows = (await db.execute(stmt)).all()
    total    = len(all_rows)

    paged    = (await db.execute(stmt.offset(offset).limit(limit))).scalars().all()

    return AlertListResponse(
        total=total,
        alerts=[
            AlertResponse(
                id=a.id,
                timestamp=a.timestamp,
                attack_type=a.attack_type,
                severity_label=a.severity_label,
                severity_score=a.severity_score,
                confidence=a.confidence,
                source_ip=a.source_ip,
                dest_ip=a.dest_ip,
                is_acknowledged=a.is_acknowledged,
            )
            for a in paged
        ],
    )


@router.patch("/alerts/{alert_id}/acknowledge")
async def acknowledge(alert_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(Alert).where(Alert.id == alert_id).values(is_acknowledged=True)
    )
    await db.commit()
    return {"id": alert_id, "acknowledged": True}