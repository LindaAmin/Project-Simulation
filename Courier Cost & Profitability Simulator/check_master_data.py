from pathlib import Path

import pandas as pd


PROJECT_FOLDER = Path(__file__).parent
DATA_FOLDER = PROJECT_FOLDER / "data"


def inspect_csv(csv_path: Path) -> None:
    print("\n" + "=" * 70)
    print(f"FILE: {csv_path.name}")
    print("=" * 70)

    try:
        dataframe = pd.read_csv(
            csv_path
        )

        print("Default comma delimiter:")
        print(f"Rows: {len(dataframe)}")
        print(f"Columns: {len(dataframe.columns)}")
        print(
            "Column names:",
            dataframe.columns.tolist(),
        )

        if len(dataframe.columns) == 1:
            print(
                "\nWARNING: Only one column was detected."
            )

            print(
                "Trying semicolon delimiter..."
            )

            semicolon_dataframe = pd.read_csv(
                csv_path,
                sep=";",
            )

            print(
                "Semicolon columns:",
                semicolon_dataframe.columns.tolist(),
            )

            if len(
                semicolon_dataframe.columns
            ) > 1:
                print(
                    "RESULT: This file probably uses ';' "
                    "as its delimiter."
                )

        print("\nFirst three rows:")
        print(
            dataframe.head(
                3
            ).to_string(
                index=False
            )
        )

    except Exception as error:
        print(
            f"ERROR: {type(error).__name__}: {error}"
        )


if not DATA_FOLDER.exists():
    print(
        f"Data folder not found: {DATA_FOLDER}"
    )

else:
    csv_files = sorted(
        DATA_FOLDER.glob(
            "*.csv"
        )
    )

    if not csv_files:
        print(
            f"No CSV files found in: {DATA_FOLDER}"
        )

    for csv_file in csv_files:
        inspect_csv(
            csv_file
        )
        