from __future__ import annotations

import ast
from pathlib import Path


PROJECT_FOLDER = Path(__file__).parent
COMPONENT_MODULE = "utils.components"


def find_component_imports(
    python_file: Path,
) -> set[str]:
    """
    Return names imported from utils.components.
    """

    imported_names: set[str] = set()

    try:
        source = python_file.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(python_file),
        )

    except (UnicodeDecodeError, SyntaxError) as error:
        print(
            f"Could not read {python_file}: {error}"
        )
        return imported_names

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == COMPONENT_MODULE
        ):
            for imported_name in node.names:
                imported_names.add(
                    imported_name.name
                )

    return imported_names


all_imports: dict[str, list[str]] = {}

for python_file in PROJECT_FOLDER.rglob(
    "*.py"
):
    if python_file.name == "components.py":
        continue

    component_imports = find_component_imports(
        python_file
    )

    if component_imports:
        relative_path = python_file.relative_to(
            PROJECT_FOLDER
        )

        all_imports[str(relative_path)] = sorted(
            component_imports
        )


print("\nCOMPONENT IMPORTS BY FILE")
print("=" * 60)

for filename, imported_names in sorted(
    all_imports.items()
):
    print(f"\n{filename}")

    for imported_name in imported_names:
        print(f"  - {imported_name}")


all_unique_imports = sorted(
    {
        imported_name
        for names in all_imports.values()
        for imported_name in names
    }
)

print("\nALL UNIQUE COMPONENT FUNCTIONS")
print("=" * 60)

for imported_name in all_unique_imports:
    print(imported_name)