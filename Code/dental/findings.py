from dataclasses import dataclass
from typing import Optional, Tuple

PATHOLOGIES = {"caries", "deep caries", "periapical lesion", "impacted tooth", "bone loss", "root remnant", "cyst"}
TREATMENTS = {"filling", "crown", "root canal treatment", "implant", "bridge"}


@dataclass
class Finding:
    id: str                               # F1, F2, ... cited by report sentences
    label: str
    confidence: float
    bbox: Tuple[float, float, float, float]
    tooth: Optional[str] = None           # FDI number, e.g. "36"
    mask_area_px: Optional[int] = None

    @property
    def kind(self):
        return "pathology" if self.label in PATHOLOGIES else "treatment" if self.label in TREATMENTS else "other"
