import json

from bc_npp_database.scoring import (
    ScoreFamily,
    ScoreInputRecord,
    ScoreWeightRecord,
    calculate_scores,
    score_family_values,
    validate_score_inputs,
    validate_score_weights,
)


def test_score_family_vocabulary_is_stable():
    assert score_family_values() == {"UNI", "PSI", "RVI"}
    assert ScoreFamily.UNI.value == "UNI"


def test_score_input_record_round_trips_from_mapping():
    record = ScoreInputRecord.from_mapping(
        {
            "Species ID": "BCNPPD-0001",
            "Score Family": "PSI",
            "Metric": "Native Bee Score",
            "Value": "4",
            "Source ID": "SRC-0001",
            "Evidence Confidence": "A",
            "Review Status": "accepted",
            "Context ID": "figrecover:review:abc",
        }
    )

    assert record.species_id == "BCNPPD-0001"
    assert record.to_dict()["context_id"] == "figrecover:review:abc"
    assert json.dumps(record.to_dict())


def test_weight_validation_checks_family_metric_and_weight():
    diagnostics = validate_score_weights(
        [
            {
                "Score Family": "BAD",
                "Metric": "",
                "Weight": "-1",
            }
        ]
    )

    codes = {diagnostic.code for diagnostic in diagnostics}
    assert {"invalid_score_family", "missing_required_field", "invalid_score_weight"} <= codes


def test_score_input_validation_checks_review_gate_and_required_source():
    diagnostics = validate_score_inputs(
        [
            {
                "Species ID": "CDF-0001",
                "Score Family": "PSI",
                "Metric": "Native Bee Score",
                "Value": "6",
                "Evidence Confidence": "Certain",
                "Review Status": "pending_review",
            }
        ],
        [{"Score Family": "PSI", "Metric": "Native Bee Score", "Weight": "1"}],
    )

    codes = {diagnostic.code for diagnostic in diagnostics}
    assert {
        "invalid_species_id",
        "invalid_score_value",
        "invalid_evidence_confidence",
        "missing_required_field",
        "unreviewed_score_input",
    } <= codes


def test_calculate_scores_uses_reviewed_numeric_inputs_only():
    summary = calculate_scores(
        [
            {
                "Species ID": "BCNPPD-0001",
                "Score Family": "PSI",
                "Metric": "Native Bee Score",
                "Value": "4",
                "Source ID": "SRC-0001",
                "Evidence Confidence": "A",
                "Review Status": "accepted",
            },
            {
                "Species ID": "BCNPPD-0001",
                "Score Family": "PSI",
                "Metric": "Butterfly Nectar Score",
                "Value": "2",
                "Source ID": "SRC-0002",
                "Evidence Confidence": "B",
                "Review Status": "manually_corrected",
            },
            {
                "Species ID": "BCNPPD-0001",
                "Score Family": "PSI",
                "Metric": "Hoverfly Score",
                "Value": "5",
                "Source ID": "SRC-0003",
                "Evidence Confidence": "C",
                "Review Status": "rejected",
            },
        ],
        [
            {"Score Family": "PSI", "Metric": "Native Bee Score", "Weight": "2"},
            {"Score Family": "PSI", "Metric": "Butterfly Nectar Score", "Weight": "1"},
            {"Score Family": "PSI", "Metric": "Hoverfly Score", "Weight": "1"},
        ],
    )

    assert len(summary.results) == 1
    assert summary.results[0].score == 66.67
    assert summary.results[0].evidence_summary == {"A": 1, "B": 1}
    assert any(diagnostic.code == "unreviewed_score_input" for diagnostic in summary.diagnostics)


def test_calculate_scores_requires_weight_or_weight_record():
    summary = calculate_scores(
        [
            {
                "Species ID": "BCNPPD-0001",
                "Score Family": "UNI",
                "Metric": "Urban Toughness",
                "Value": "4",
                "Source ID": "SRC-0001",
                "Evidence Confidence": "A",
                "Review Status": "accepted",
            }
        ]
    )

    assert summary.results == ()
    assert any(diagnostic.code == "missing_score_weight" for diagnostic in summary.diagnostics)


def test_input_weight_can_override_weight_records():
    summary = calculate_scores(
        [
            {
                "Species ID": "BCNPPD-0001",
                "Score Family": "RVI",
                "Metric": "Restoration Suitability",
                "Value": "5",
                "Weight": "3",
                "Source ID": "SRC-0001",
                "Evidence Confidence": "B",
                "Review Status": "accepted",
            }
        ]
    )

    assert summary.results[0].score == 100.0
    assert summary.results[0].weight_total == 3.0


def test_weight_record_serializes_cleanly():
    record = ScoreWeightRecord.from_mapping(
        {
            "Score Family": "UNI",
            "Metric": "Urban Toughness",
            "Weight": "1.5",
            "Review Status": "pending_review",
        }
    )

    assert record.to_dict()["weight"] == "1.5"
