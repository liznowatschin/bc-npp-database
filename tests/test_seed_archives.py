from zipfile import ZipFile

from bc_npp_database.seed_archives import categorize_seed_path, inventory_seed_archive


def test_categorize_seed_path_marks_raw_artifacts_for_review():
    assert (
        categorize_seed_path("BC-NPPD/data/raw/table_screenshot_original.png")
        == "raw_source_artifact"
    )
    assert categorize_seed_path("BC-NPPD/docs/project_brief.md") == "documentation"
    assert categorize_seed_path("BC-NPPD/schemas/lookups_seed.csv") == "schema_or_table_seed"


def test_inventory_seed_archive_uses_default_dispositions(tmp_path):
    archive_path = tmp_path / "seed.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("docs/project_brief.md", "# brief")
        archive.writestr("data/raw/source.pdf", b"pdf")
        archive.writestr("workbooks/template.xlsx", b"xlsx")

    inventory = inventory_seed_archive(archive_path)

    dispositions = {entry.path: entry.disposition for entry in inventory.entries}
    assert dispositions["docs/project_brief.md"] == "candidate_clean_derivative_or_already_tracked"
    assert dispositions["data/raw/source.pdf"] == "ignored_pending_review"
    assert (
        dispositions["workbooks/template.xlsx"]
        == "candidate_clean_derivative_or_already_tracked"
    )
