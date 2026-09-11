#  Look-alike Detection & Validation

### SAR Look-alike Filtering & Spill Validation

**OCEANNOVA • Task 3**

---

##  Overview

The Look-alike Detection & Validation module validates candidate oil-spill regions detected from Sentinel-1 SAR imagery.

A dark SAR region is not automatically an oil spill. Similar signatures can be produced by low-wind conditions, biogenic slicks, and other environmental effects.

This module reduces false positives by combining:

- Geometric features
- Radiometric features
- Environmental conditions
- Baseline validation rules
- Random Forest prototype classification

The module operates after U-Net segmentation and before spill characterization, drift modelling, and vessel attribution.

---

##  Validation Pipeline

```text
Candidate SAR Region
        ↓
Geometry Feature Extraction
        ↓
Radiometric Feature Extraction
        ↓
Environmental / Baseline Checks
        ↓
Random Forest Prototype
        ↓
Validation Decision
        ↓
Likely Oil / Possible Look-alike