from drift_model import analyze_spill
from datetime import datetime, timezone
from pathlib import Path
import json


# ==========================================
# SAMPLE OBSERVED SPILL
# ==========================================

observed_time = datetime(
    2026,
    9,
    6,
    12,
    0,
    tzinfo=timezone.utc
)

result = analyze_spill(
    spill_id="SP-001",
    observed_lat=10.710,
    observed_lon=76.050,
    observed_time=observed_time
)


# ==========================================
# CREATE OUTPUT DIRECTORY
# ==========================================

project_root = Path(__file__).resolve().parents[1]

output_dir = project_root / "output"

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# SAVE JSON
# ==========================================

output_file = output_dir / "SP-001.json"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        result,
        file,
        indent=2
    )


# ==========================================
# DISPLAY RESULT
# ==========================================

print("\n========================================")
print("        OCEANNOVA - DRIFT ENGINE")
print("========================================")

print("\n✓ Spill processed:", result["spill_id"])

print("\nProbable Origin")
print("-------------------------")
print("Latitude    :", result["origin"]["lat"])
print("Longitude   :", result["origin"]["lon"])
print(
    "Uncertainty :",
    result["origin"]["uncertainty_km"],
    "km"
)
print(
    "Confidence  :",
    result["origin"]["confidence"]
)

print("\nOrigin Time Window")
print("-------------------------")
print(
    result["origin_time_window"]["start"]
)
print("       ↓")
print(
    result["origin_time_window"]["end"]
)

print("\nTrajectory")
print("-------------------------")
print(
    "Backward points:",
    len(
        result["backward_hindcast"]["coordinates"]
    )
)

print(
    "Forward points :",
    len(
        result["forward_forecast"]["coordinates"]
    )
)

print("\n✓ JSON output saved!")
print(output_file)

print("\n========================================")