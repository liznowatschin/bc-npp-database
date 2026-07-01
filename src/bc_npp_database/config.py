"""Project configuration constants."""

PROJECT_NAME = "BC Native Plant & Pollinator Database"
PROJECT_ABBREVIATION = "BC-NPPD"

EXCLUDED_SOURCE_URLS = {
    "https://vancouver.ca/files/cov/vancouver-gri-planting-guidelines.pdf",
}

EVIDENCE_CONFIDENCE_VALUES = {
    "",
    "A",
    "B",
    "C",
    "D",
    "Mixed",
    "Pending review",
    "Unknown",
}

SPECIES_ID_COLUMNS = ("Species ID", "Species_ID")
EVIDENCE_CONFIDENCE_COLUMNS = (
    "Evidence Level",
    "Evidence_Level",
    "Evidence Confidence",
    "Evidence_Confidence",
)
