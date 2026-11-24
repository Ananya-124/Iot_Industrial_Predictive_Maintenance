from datetime import datetime, timezone
from backend.app.schemas import Telemetry
from backend.app.features import extract_features


def test_rms_feature():
    item = Telemetry(device_id="test", timestamp=datetime.now(timezone.utc),
                     vibration_x=1.0, vibration_y=1.0, vibration_z=1.0,
                     temperature_c=25.0, current_a=0.5)
    features = extract_features(item)
    assert abs(features["vibration_rms"] - 1.0) < 1e-9
