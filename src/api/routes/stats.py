from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.database import Alert, AnalysisLog, get_db
from src.api.models import StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_analyzed = (await db.execute(
        select(func.count()).select_from(AnalysisLog)
    )).scalar() or 0

    total_alerts = (await db.execute(
        select(func.count()).select_from(Alert)
    )).scalar() or 0

    attack_rate = total_alerts / total_analyzed if total_analyzed > 0 else 0.0

    rows = (await db.execute(
        select(Alert.attack_type, func.count().label("cnt"))
        .group_by(Alert.attack_type)
    )).all()
    by_attack_type = {r.attack_type: r.cnt for r in rows}

    rows2 = (await db.execute(
        select(Alert.severity_label, func.count().label("cnt"))
        .group_by(Alert.severity_label)
    )).all()
    by_severity = {r.severity_label: r.cnt for r in rows2}

    since = datetime.utcnow() - timedelta(hours=24)
    recent_24h = (await db.execute(
        select(func.count()).select_from(Alert)
        .where(Alert.timestamp >= since)
    )).scalar() or 0

    return StatsResponse(
        total_analyzed=total_analyzed,
        total_alerts=total_alerts,
        attack_rate=round(attack_rate, 4),
        by_attack_type=by_attack_type,
        by_severity=by_severity,
        recent_24h=recent_24h,
    )


@router.get("/model-report")
async def model_report(request: Request):
    engine = request.app.state.engine
    return engine.status()