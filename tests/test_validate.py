from bc_npp_database.validate import (
    diagnose_duplicate_species_ids,
    diagnose_excluded_sources,
    diagnose_invalid_evidence_confidence,
    find_duplicate_species_ids,
    find_excluded_sources,
    find_invalid_evidence_confidence,
)


def test_excluded_source_detection_searches_any_field():
    rows = [
        {"Species ID": "BCNPPD-0001", "Source": "https://example.org/ok"},
        {
            "Species ID": "BCNPPD-0002",
            "Notes": (
                "Do not use "
                "https://vancouver.ca/files/cov/vancouver-gri-planting-guidelines.pdf"
            ),
        },
    ]
    violations = find_excluded_sources(rows)
    assert len(violations) == 1
    assert violations[0]["row_number"] == 2


def test_duplicate_species_ids_accepts_space_and_underscore_columns():
    rows = [
        {"Species ID": "BCNPPD-0002"},
        {"Species_ID": "BCNPPD-0001"},
        {"Species ID": "BCNPPD-0002"},
    ]
    assert find_duplicate_species_ids(rows) == ["BCNPPD-0002"]


def test_invalid_evidence_confidence_accepts_configured_values():
    rows = [
        {"Evidence Level": "A"},
        {"Evidence_Confidence": "Mixed"},
        {"Evidence Confidence": "Pending review"},
        {"Evidence Level": "Z"},
    ]
    invalid = find_invalid_evidence_confidence(rows)
    assert len(invalid) == 1
    assert invalid[0]["value"] == "Z"


def test_validation_diagnostics_are_structured():
    rows = [
        {
            "Species ID": "BCNPPD-0001",
            "Evidence Level": "Z",
            "Source": "https://vancouver.ca/files/cov/vancouver-gri-planting-guidelines.pdf",
        },
        {"Species ID": "BCNPPD-0001", "Evidence Level": "A"},
    ]

    diagnostics = [
        *diagnose_excluded_sources(rows),
        *diagnose_duplicate_species_ids(rows),
        *diagnose_invalid_evidence_confidence(rows),
    ]

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "excluded_source",
        "duplicate_species_id",
        "invalid_evidence_confidence",
    }
    assert all(diagnostic.to_dict()["severity"] == "error" for diagnostic in diagnostics)
