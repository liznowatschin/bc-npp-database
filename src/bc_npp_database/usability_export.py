#!/usr/bin/env python3
"""
Usability data export module for BC-NPPD.
This module provides functionality to export usability layer data to Excel format.
"""


from pathlib import Path

import pandas as pd


def export_usability_to_excel(
    input_dir: str = "data/poc/vancouver/usability_layer",
    output_file: str = "data/poc/vancouver/usability_export.xlsx"
) -> bool:
    """
    Export usability data to Excel format.

    Args:
        input_dir (str): Path to the usability layer directory containing CSV files
        output_file (str): Path where the Excel file will be saved

    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # Check if input directory exists
        if not Path(input_dir).exists():
            print(f"Error: Input directory {input_dir} does not exist")
            return False

        # Create a Pandas Excel writer object
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

            # Export plant_table.csv to 'Plant_Table' sheet
            plant_table_path = Path(input_dir) / "plant_table.csv"
            if plant_table_path.exists():
                df_plant = pd.read_csv(plant_table_path)
                df_plant.to_excel(writer, sheet_name='Plant_Table', index=False)
                print(f"Exported {len(df_plant)} rows to Plant_Table sheet")

            # Export use_case_views.csv to 'Use_Case_Views' sheet
            use_case_path = Path(input_dir) / "use_case_views.csv"
            if use_case_path.exists():
                df_use_case = pd.read_csv(use_case_path)
                df_use_case.to_excel(writer, sheet_name='Use_Case_Views', index=False)
                print(f"Exported {len(df_use_case)} rows to Use_Case_Views sheet")

            # Export view_summary.csv to 'View_Summary' sheet
            view_summary_path = Path(input_dir) / "view_summary.csv"
            if view_summary_path.exists():
                df_view_summary = pd.read_csv(view_summary_path)
                df_view_summary.to_excel(writer, sheet_name='View_Summary', index=False)
                print(f"Exported {len(df_view_summary)} rows to View_Summary sheet")

            # Export diagnostics.csv to 'Diagnostics' sheet
            diagnostics_path = Path(input_dir) / "diagnostics.csv"
            if diagnostics_path.exists():
                df_diagnostics = pd.read_csv(diagnostics_path)
                df_diagnostics.to_excel(writer, sheet_name='Diagnostics', index=False)
                print(f"Exported {len(df_diagnostics)} rows to Diagnostics sheet")

        print(f"All data exported successfully to {output_file}")
        return True

    except Exception as e:
        print(f"Error during export: {str(e)}")
        return False
