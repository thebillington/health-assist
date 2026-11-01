"""Constants and the metric registry for Apple Health Sync."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

DOMAIN: Final = "apple_health_sync"

CONF_WEBHOOK_ID: Final = "webhook_id"
CONF_SECRET: Final = "secret"
CONF_METRICS: Final = "metrics"
CONF_QR_CODE: Final = "qr_code"

DEFAULT_NAME: Final = "Apple Health"
DEFAULT_TITLE: Final = "Apple Health Sync"

SECRET_HEADER: Final = "X-Webhook-Secret"

MAX_PAYLOAD_BYTES: Final = 256 * 1024
MAX_METRICS_PER_PAYLOAD: Final = 256
MAX_HISTORY_SAMPLES: Final = 2_000
MAX_METRIC_KEY_LENGTH: Final = 64
MAX_TEXT_LENGTH: Final = 128
MAX_UNIT_LENGTH: Final = 32

MANUFACTURER: Final = "Apple Health Sync"
MODEL: Final = "iOS App"


# Signals are per config entry so that multiple phones can coexist.
def signal_new_data(entry_id: str) -> str:
    """Return the dispatcher signal used when new data arrives for an entry."""
    return f"{DOMAIN}_new_data_{entry_id}"


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    """Describes a canonical Apple Health metric."""

    name: str
    unit: str | None
    device_class: SensorDeviceClass | None
    state_class: SensorStateClass | None


# Canonical metric keys. These are part of the webhook contract and must not be
# renamed without a migration in the iOS app.
METRICS: Final[dict[str, MetricDefinition]] = {
    "weight": MetricDefinition(
        "Weight", "kg", SensorDeviceClass.WEIGHT, SensorStateClass.MEASUREMENT
    ),
    "bmi": MetricDefinition("BMI", None, None, SensorStateClass.MEASUREMENT),
    "body_fat": MetricDefinition("Body fat", "%", None, SensorStateClass.MEASUREMENT),
    "lean_body_mass": MetricDefinition(
        "Lean body mass", "kg", SensorDeviceClass.WEIGHT, SensorStateClass.MEASUREMENT
    ),
    "muscle_mass": MetricDefinition(
        "Muscle mass", "kg", SensorDeviceClass.WEIGHT, SensorStateClass.MEASUREMENT
    ),
    "bone_mass": MetricDefinition(
        "Bone mass", "kg", SensorDeviceClass.WEIGHT, SensorStateClass.MEASUREMENT
    ),
    "body_water": MetricDefinition("Body water", "%", None, SensorStateClass.MEASUREMENT),
    "basal_metabolic_rate": MetricDefinition(
        "Basal metabolic rate", "kcal", None, SensorStateClass.MEASUREMENT
    ),
    "steps": MetricDefinition("Steps", "steps", None, SensorStateClass.MEASUREMENT),
    "distance": MetricDefinition(
        "Distance", "m", SensorDeviceClass.DISTANCE, SensorStateClass.MEASUREMENT
    ),
    "active_energy": MetricDefinition("Active energy", "kcal", None, SensorStateClass.MEASUREMENT),
    "resting_heart_rate": MetricDefinition(
        "Resting heart rate", "bpm", None, SensorStateClass.MEASUREMENT
    ),
    "heart_rate": MetricDefinition("Heart rate", "bpm", None, SensorStateClass.MEASUREMENT),
    "heart_rate_variability": MetricDefinition(
        "Heart rate variability", "ms", None, SensorStateClass.MEASUREMENT
    ),
    "respiratory_rate": MetricDefinition(
        "Respiratory rate", "breaths/min", None, SensorStateClass.MEASUREMENT
    ),
    "blood_oxygen": MetricDefinition("Blood oxygen", "%", None, SensorStateClass.MEASUREMENT),
    "systolic": MetricDefinition(
        "Systolic blood pressure", "mmHg", None, SensorStateClass.MEASUREMENT
    ),
    "diastolic": MetricDefinition(
        "Diastolic blood pressure", "mmHg", None, SensorStateClass.MEASUREMENT
    ),
    "sleep_total": MetricDefinition(
        "Sleep total", "h", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT
    ),
    "sleep_deep": MetricDefinition(
        "Deep sleep", "h", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT
    ),
    "sleep_rem": MetricDefinition(
        "REM sleep", "h", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT
    ),
    "sleep_core": MetricDefinition(
        "Core sleep", "h", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT
    ),
    "sleep_awake": MetricDefinition(
        "Awake time", "h", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT
    ),
    "vo2_max": MetricDefinition("VO2 max", "mL/kg/min", None, SensorStateClass.MEASUREMENT),
    "flights_climbed": MetricDefinition(
        "Flights climbed", "flights", None, SensorStateClass.MEASUREMENT
    ),
    "stand_hours": MetricDefinition(
        "Stand hours", "h", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT
    ),
    "water_intake": MetricDefinition(
        "Water intake", "mL", SensorDeviceClass.VOLUME, SensorStateClass.MEASUREMENT
    ),
}

# Human-readable labels used by the config flow multi-select.
METRIC_NAMES: Final[dict[str, str]] = {key: metric.name for key, metric in METRICS.items()}
