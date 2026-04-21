"""Pydantic data schemas for baseline records."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RouteDefinition(BaseModel):
    """Definition of an abstract-step route."""

    route_id: str
    start_point: str
    end_point: str
    abstract_step_count: int = Field(gt=0)
    description: str


class RunManifest(BaseModel):
    """Raw run manifest persisted per run."""

    run_id: str
    trial_id: str
    route_id: str
    start_point: str
    end_point: str
    abstract_step_count: int = Field(gt=0)
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str
    notes: list[str] = Field(default_factory=list)


class RunSummary(BaseModel):
    """Processed summary generated from raw run files."""

    run_id: str
    route_id: str
    total_elapsed_time_sec: Optional[float] = None
    abstract_step_count: int
    estimated_step_time_sec: Optional[float] = None
    accepted_for_stats: bool
    rejection_reason: str
    anomaly_flags: list[str] = Field(default_factory=list)
    quality_score: float = Field(ge=0.0, le=1.0)


class StepTimeModelEntry(BaseModel):
    """Route-level baseline timing model."""

    route_id: str
    valid_run_count: int
    mean_total_time_sec: Optional[float] = None
    std_total_time_sec: Optional[float] = None
    mean_step_time_sec: Optional[float] = None
    std_step_time_sec: Optional[float] = None
    median_step_time_sec: Optional[float] = None
    start_offset_sec: float
    stop_offset_sec: float
    last_updated_at: datetime

    @field_validator("valid_run_count")
    @classmethod
    def non_negative_runs(cls, value: int) -> int:
        """Ensure valid run count is never negative."""
        if value < 0:
            raise ValueError("valid_run_count must be >= 0")
        return value
