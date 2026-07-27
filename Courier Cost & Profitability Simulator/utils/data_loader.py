"""
Centralised data-loading utilities for the Courier Analysis application.

Responsibilities
----------------
- Locate project data files
- Load CSV files consistently
- Remove accidental empty Excel columns
- Standardise column names
- Validate required columns
- Convert number-like text into numeric values
- Load shipment reference data
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_ROOT / "data"
SAMPLE_DATA_FOLDER = PROJECT_ROOT / "sample_data"


# =========================================================
# GENERIC CLEANING
# =========================================================
def clean_column_names(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Strip spaces and remove accidental unnamed columns.
    """

    cleaned = dataframe.copy()

    cleaned.columns = [
        str(column).strip()
        for column in cleaned.columns
    ]

    columns_to_remove = [
        column
        for column in cleaned.columns
        if (
            column.lower().startswith(
                "unnamed:"
            )
            or not column.strip()
        )
    ]

    if columns_to_remove:
        cleaned = cleaned.drop(
            columns=columns_to_remove,
            errors="ignore",
        )

    return cleaned


def remove_empty_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove columns containing no usable values.
    """

    cleaned = dataframe.copy()

    cleaned = cleaned.dropna(
        axis=1,
        how="all",
    )

    return cleaned


def clean_text_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Trim leading and trailing spaces from text columns.
    """

    cleaned = dataframe.copy()

    text_columns = cleaned.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
        )

    return cleaned


def clean_master_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply standard cleaning to a loaded master-data table.
    """

    cleaned = clean_column_names(
        dataframe
    )

    cleaned = remove_empty_columns(
        cleaned
    )

    cleaned = clean_text_columns(
        cleaned
    )

    return cleaned


# =========================================================
# COLUMN VALIDATION
# =========================================================
def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: Iterable[str],
    file_name: str,
) -> None:
    """
    Raise a clear error when required columns are missing.
    """

    required = {
        str(column).strip()
        for column in required_columns
    }

    available = set(
        dataframe.columns
    )

    missing = sorted(
        required - available
    )

    if missing:
        raise ValueError(
            f"{file_name} is missing required columns: "
            f"{missing}. Detected columns: "
            f"{dataframe.columns.tolist()}"
        )


# =========================================================
# NUMERIC CONVERSION
# =========================================================
def convert_numeric_column(
    dataframe: pd.DataFrame,
    column_name: str,
    allow_blank: bool = True,
) -> pd.DataFrame:
    """
    Convert values such as '1,500', 'RM8.00' or '10%' to numbers.
    """

    if column_name not in dataframe.columns:
        return dataframe

    cleaned = dataframe.copy()

    numeric_text = (
        cleaned[column_name]
        .astype("string")
        .str.replace(
            ",",
            "",
            regex=False,
        )
        .str.replace(
            "RM",
            "",
            regex=False,
        )
        .str.replace(
            "%",
            "",
            regex=False,
        )
        .str.strip()
    )

    cleaned[column_name] = pd.to_numeric(
        numeric_text,
        errors=(
            "coerce"
            if allow_blank
            else "raise"
        ),
    )

    return cleaned


# =========================================================
# GENERIC FILE LOADERS
# =========================================================
def load_csv_file(
    file_path: str | Path,
    required_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Load and clean a CSV file.
    """

    path = Path(
        file_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}"
        )

    dataframe = pd.read_csv(
        path,
        encoding="utf-8-sig",
    )

    dataframe = clean_master_dataframe(
        dataframe
    )

    if required_columns:
        validate_required_columns(
            dataframe=dataframe,
            required_columns=required_columns,
            file_name=path.name,
        )

    return dataframe


def load_excel_file(
    file_path: str | Path,
    required_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Load and clean an Excel file.
    """

    path = Path(
        file_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}"
        )

    dataframe = pd.read_excel(
        path
    )

    dataframe = clean_master_dataframe(
        dataframe
    )

    if required_columns:
        validate_required_columns(
            dataframe=dataframe,
            required_columns=required_columns,
            file_name=path.name,
        )

    return dataframe


def load_uploaded_shipment_file(
    uploaded_file,
) -> pd.DataFrame:
    """
    Load a shipment file uploaded through Streamlit.
    """

    file_name = str(
        uploaded_file.name
    ).lower()

    if file_name.endswith(
        ".csv"
    ):
        dataframe = pd.read_csv(
            uploaded_file,
            encoding="utf-8-sig",
        )

    elif file_name.endswith(
        ".xlsx"
    ):
        dataframe = pd.read_excel(
            uploaded_file
        )

    else:
        raise ValueError(
            "Only CSV and XLSX shipment files are supported."
        )

    return clean_master_dataframe(
        dataframe
    )


# =========================================================
# MASTER-DATA LOADERS
# =========================================================
def load_state_master() -> pd.DataFrame:
    """
    Load state-to-region reference data.
    """

    dataframe = load_csv_file(
        DATA_FOLDER / "state_master.csv",
        required_columns=[
            "State",
            "Region",
        ],
    )

    dataframe = dataframe[
        [
            "State",
            "Region",
        ]
    ].drop_duplicates()

    return dataframe.reset_index(
        drop=True
    )


def load_service_level_master() -> pd.DataFrame:
    """
    Load courier service-level reference data.
    """

    dataframe = load_csv_file(
        DATA_FOLDER / "service_level.csv",
        required_columns=[
            "Service Level",
            "Target Delivery (Days)",
            "Priority",
            "Cost Multiplier",
        ],
    )

    dataframe = convert_numeric_column(
        dataframe,
        "Cost Multiplier",
    )

    return dataframe.reset_index(
        drop=True
    )


def load_parcel_master() -> pd.DataFrame:
    """
    Load parcel-size reference data.
    """

    dataframe = load_csv_file(
        DATA_FOLDER / "parcel_master.csv",
        required_columns=[
            "Parcel Type",
            "Length (cm)",
            "Width (cm)",
            "Height (cm)",
            "Max Weight (kg)",
            "Volumetric Divisor",
        ],
    )

    numeric_columns = [
        "Length (cm)",
        "Width (cm)",
        "Height (cm)",
        "Max Weight (kg)",
        "Volumetric Divisor",
    ]

    for column in numeric_columns:
        dataframe = convert_numeric_column(
            dataframe,
            column,
        )

    return dataframe.reset_index(
        drop=True
    )


def load_shipment_reference_data() -> dict[str, pd.DataFrame]:
    """
    Load all reference tables required by Shipment Information.
    """

    return {
        "states": load_state_master(),
        "service_levels": (
            load_service_level_master()
        ),
        "parcels": load_parcel_master(),
    }