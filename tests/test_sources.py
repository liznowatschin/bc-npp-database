import json

from bc_npp_database.sources import (
    MaterializationManifest,
    MediaExtractionManifest,
    SourceAttributionRecord,
    SourceRecord,
    validate_materialization_manifests,
    validate_media_extraction_manifests,
    validate_source_attribution_records,
    validate_source_records,
)


def test_source_record_round_trips_from_mapping():
    record = SourceRecord.from_mapping(
        {
            "Source ID": "SRC-0001",
            "Source Name": "Land Management Handbook 77",
            "Source Tier": "Tier 2",
            "Citation": "Klassen et al. 2026.",
            "External ID": "bcdc:package:abc123",
            "Review Status": "accepted",
        }
    )

    assert record.source_id == "SRC-0001"
    assert record.to_dict()["source_tier"] == "Tier 2"


def test_source_record_validation_checks_tier_id_and_citation():
    diagnostics = validate_source_records(
        [
            {
                "Source ID": "BAD-1",
                "Source Name": "Source",
                "Source Tier": "Tier 9",
            }
        ]
    )

    codes = {diagnostic.code for diagnostic in diagnostics}
    assert {"invalid_source_id", "invalid_source_tier", "missing_citation_or_url"} <= codes


def test_source_attribution_requires_species_for_species_claims():
    diagnostics = validate_source_attribution_records(
        [
            {
                "Source ID": "SRC-0001",
                "Claim Field": "habitat",
                "Evidence Confidence": "A",
                "Claim Scope": "species",
            }
        ]
    )

    assert any(diagnostic.field == "species_id" for diagnostic in diagnostics)


def test_source_attribution_accepts_non_species_claim_without_species_id():
    diagnostics = validate_source_attribution_records(
        [
            {
                "Source ID": "SRC-0001",
                "Claim Field": "source_policy",
                "Evidence Confidence": "A",
                "Claim Scope": "project",
            }
        ]
    )

    assert diagnostics == []


def test_invalid_evidence_confidence_and_species_id_are_diagnostic():
    diagnostics = validate_source_attribution_records(
        [
            {
                "Source ID": "SRC-0001",
                "Species ID": "CDF-0001",
                "Claim Field": "habitat",
                "Evidence Confidence": "Certain",
            }
        ]
    )

    codes = {diagnostic.code for diagnostic in diagnostics}
    assert {"invalid_species_id", "invalid_evidence_confidence"} <= codes


def test_excluded_source_detection_scans_nested_mapping_values():
    diagnostics = validate_source_records(
        [
            {
                "Source ID": "SRC-0001",
                "Source Name": "Bad source",
                "Source Tier": "Tier 2",
                "Citation": "Source",
                "metadata": {
                    "url": "https://vancouver.ca/files/cov/vancouver-gri-planting-guidelines.pdf"
                },
            }
        ]
    )

    assert any(diagnostic.code == "excluded_source" for diagnostic in diagnostics)


def test_external_ids_must_be_namespaced():
    diagnostics = validate_source_records(
        [
            {
                "Source ID": "SRC-0001",
                "Source Name": "Source",
                "Source Tier": "Tier 2",
                "Citation": "Citation",
                "External ID": "abc123",
            }
        ]
    )

    assert any(diagnostic.code == "invalid_external_id" for diagnostic in diagnostics)


def test_materialization_review_gate_blocks_unreviewed_accepted_outputs():
    manifest = MaterializationManifest(
        manifest_id="MAT-0001",
        source_id="SRC-0001",
        artifact_type="bcdc_manifest",
        status="accepted",
        review_status="pending_review",
    )

    diagnostics = validate_materialization_manifests([manifest.to_dict()])

    assert any(diagnostic.code == "unreviewed_materialization" for diagnostic in diagnostics)


def test_media_review_gate_blocks_unreviewed_accepted_table_paths():
    manifest = MediaExtractionManifest(
        extraction_id="MED-0001",
        source_id="SRC-0001",
        source_document_id="LMH77",
        accepted_table_path="outputs/lmh77/table.csv",
        review_status="rejected",
    )

    diagnostics = validate_media_extraction_manifests([manifest.to_dict()])

    assert any(diagnostic.code == "unreviewed_media_extraction" for diagnostic in diagnostics)


def test_source_attribution_record_serializes_cleanly():
    record = SourceAttributionRecord.from_mapping(
        {
            "Source ID": "SRC-0001",
            "Species ID": "BCNPPD-0001",
            "Claim Field": "habitat",
            "Claim Value": "rocky headland",
            "Evidence Confidence": "B",
            "External ID": "figrecover:review:abc",
        }
    )

    assert json.dumps(record.to_dict())
    assert record.to_dict()["species_id"] == "BCNPPD-0001"
