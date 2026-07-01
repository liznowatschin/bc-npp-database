from pathlib import Path

from openpyxl import Workbook

from bc_npp_database.workbooks import inventory_workbook, validate_workbook


def _write_workbook(path: Path, sheets: dict[str, list[str]]) -> Path:
    workbook = Workbook()
    default = workbook.active
    workbook.remove(default)
    for name, headers in sheets.items():
        worksheet = workbook.create_sheet(name)
        worksheet.append(headers)
        worksheet.append(["value" for _ in headers])
    workbook.save(path)
    return path


def test_inventory_workbook_reads_sheet_headers(tmp_path):
    path = _write_workbook(
        tmp_path / "fixture.xlsx",
        {"Species_Master": ["Species_ID", "Botanical_Name"]},
    )

    inventory = inventory_workbook(path)

    assert inventory.path == str(path)
    assert inventory.sheets[0].name == "Species_Master"
    assert inventory.sheets[0].headers == ("Species_ID", "Botanical_Name")


def test_validate_workbook_reports_missing_expected_sheets(tmp_path):
    path = _write_workbook(tmp_path / "fixture.xlsx", {"Species_Master": ["Species_ID"]})

    diagnostics = validate_workbook(path)

    codes = {diagnostic.code for diagnostic in diagnostics}
    assert "missing_sheet" in codes


def test_validate_workbook_accepts_expected_foundation_sheets(tmp_path):
    path = _write_workbook(
        tmp_path / "fixture.xlsx",
        {
            "Species_Master": ["Species_ID"],
            "Lookup_Tables": ["Evidence Confidence"],
            "Reference_Policy": ["Policy"],
            "Source_Attribution": ["Species_ID", "Source_Name"],
            "Bloom_Calendar": ["Species_ID", "Jan"],
            "QA_Log": ["Date", "Issue"],
        },
    )

    assert validate_workbook(path) == []
