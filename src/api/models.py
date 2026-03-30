from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NetworkFlowRequest(BaseModel):
    features: dict[str, float] = Field(
        description="Feature name to float value",
        example={
            "SYN Flag Count": 1,
            "Flow Duration": 50000,
            "Total Fwd Packets": 10,
            "Flow Bytes/s": 1200,
            "FIN Flag Count": 1,
        }
    )
    source_ip: Optional[str] = None
    dest_ip:   Optional[str] = None


class DetectionResponse(BaseModel):
    is_attack:      bool
    attack_type:    str
    confidence:     float
    severity_score: int
    severity_label: str
    should_alert:   bool
    ensemble_votes: dict
    model_results:  dict
    timestamp:      datetime
    alert_id:       Optional[str] = None


class AlertResponse(BaseModel):
    id:              int
    timestamp:       datetime
    attack_type:     str
    severity_label:  str
    severity_score:  int
    confidence:      float
    source_ip:       Optional[str]
    dest_ip:         Optional[str]
    is_acknowledged: bool


class AlertListResponse(BaseModel):
    total:  int
    alerts: list[AlertResponse]


class StatsResponse(BaseModel):
    total_analyzed:  int
    total_alerts:    int
    attack_rate:     float
    by_attack_type:  dict[str, int]
    by_severity:     dict[str, int]
    recent_24h:      int