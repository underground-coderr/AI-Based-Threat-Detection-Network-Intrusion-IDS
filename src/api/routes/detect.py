import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.database import Alert, AnalysisLog, get_db
from src.api.models import DetectionResponse, NetworkFlowRequest
from src.utils.logger import logger

router = APIRouter()


@router.post("/detect", response_model=DetectionResponse)
async def detect(
    request: Request,
    payload: NetworkFlowRequest,
    db: AsyncSession = Depends(get_db),
):
    engine = request.app.state.engine

    if not engine.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Detection engine not ready. Train models first.",
        )

    try:
        result = engine.predict(payload.features)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    now = datetime.utcnow()

    log = AnalysisLog(
        timestamp=now,
        is_attack=result["is_attack"],
        attack_type=result["attack_type"],
        confidence=result["confidence"],
    )
    db.add(log)

    alert_id = None
    if result["should_alert"]:
        alert = Alert(
            timestamp=now,
            attack_type=result["attack_type"],
            severity_score=result["severity_score"],
            severity_label=result["severity_label"],
            confidence=result["confidence"],
            is_attack=result["is_attack"],
            source_ip=payload.source_ip,
            dest_ip=payload.dest_ip,
            raw_result=json.dumps({
                k: v for k, v in result.items()
                if k != "model_results"
            }),
        )
        db.add(alert)
        await db.flush()
        alert_id = str(alert.id)
        logger.warning(
            f"ALERT [{result['severity_label']}] "
            f"{result['attack_type']} conf={result['confidence']:.3f}"
        )

    await db.commit()

    return DetectionResponse(
        **result,
        timestamp=now,
        alert_id=alert_id,
    )