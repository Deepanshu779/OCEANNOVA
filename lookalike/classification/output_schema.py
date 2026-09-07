from typing import List, Dict, Any

def format_pipeline_output(
    spill_id: str,
    valid_spill: bool,
    confidence: float,
    lookalike_prob: float,
    reasons: List[str],
    geom_characterization: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Standardizes output matching the required OCEANNOVA Task 4 + Task 6 contract.
    """
    return {
        "spill_id": spill_id,
        "valid_spill": valid_spill,
        "confidence": round(float(confidence), 2),
        "lookalike_probability": round(float(lookalike_prob), 2),
        "reason": reasons,
        "characterization": geom_characterization
    }