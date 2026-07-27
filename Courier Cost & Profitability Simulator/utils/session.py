"""
Session-state management for the Courier Cost Analysis application.

Responsibilities
----------------
- Initialise Streamlit session state
- Store page outputs
- Retrieve page outputs
- Check page completion
- Clear individual page data
- Clear downstream dependent pages
- Reset the complete application
- Track page update timestamps
- Support workflow validation

This module must not contain:
- Business calculations
- CSV loading
- CSS
- Page styling
- Cost calculations
- Route calculations
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Iterable

import streamlit as st


# =========================================================
# SESSION-STATE KEYS
# =========================================================
SHIPMENT_INFORMATION_KEY = "shipment_information"
ROUTE_INTELLIGENCE_KEY = "route_intelligence"
PARCEL_ASSESSMENT_KEY = "parcel_assessment"
FLEET_CAPACITY_KEY = "fleet_capacity"
OPERATING_COST_KEY = "operating_cost"
COST_PER_PARCEL_KEY = "cost_per_parcel"
PROFITABILITY_KEY = "profitability"
SCENARIO_SIMULATION_KEY = "scenario_simulation"

PAGE_STATUS_KEY = "page_status"
PAGE_UPDATED_AT_KEY = "page_updated_at"
APP_METADATA_KEY = "app_metadata"


# =========================================================
# PAGE ORDER
# =========================================================
PAGE_SEQUENCE = [
    SHIPMENT_INFORMATION_KEY,
    ROUTE_INTELLIGENCE_KEY,
    PARCEL_ASSESSMENT_KEY,
    FLEET_CAPACITY_KEY,
    OPERATING_COST_KEY,
    COST_PER_PARCEL_KEY,
    PROFITABILITY_KEY,
    SCENARIO_SIMULATION_KEY,
]


PAGE_DISPLAY_NAMES = {
    SHIPMENT_INFORMATION_KEY: "Shipment Information",
    ROUTE_INTELLIGENCE_KEY: "Route Intelligence",
    PARCEL_ASSESSMENT_KEY: "Parcel Assessment",
    FLEET_CAPACITY_KEY: "Fleet Capacity",
    OPERATING_COST_KEY: "Operating Cost",
    COST_PER_PARCEL_KEY: "Cost per Parcel",
    PROFITABILITY_KEY: "Profitability",
    SCENARIO_SIMULATION_KEY: "Scenario Simulation",
}


# =========================================================
# PAGE DEPENDENCIES
# =========================================================
PAGE_DEPENDENCIES = {
    SHIPMENT_INFORMATION_KEY: [],

    ROUTE_INTELLIGENCE_KEY: [
        SHIPMENT_INFORMATION_KEY,
    ],

    PARCEL_ASSESSMENT_KEY: [
        SHIPMENT_INFORMATION_KEY,
    ],

    FLEET_CAPACITY_KEY: [
        SHIPMENT_INFORMATION_KEY,
        ROUTE_INTELLIGENCE_KEY,
        PARCEL_ASSESSMENT_KEY,
    ],

    OPERATING_COST_KEY: [
        SHIPMENT_INFORMATION_KEY,
        ROUTE_INTELLIGENCE_KEY,
        PARCEL_ASSESSMENT_KEY,
        FLEET_CAPACITY_KEY,
    ],

    COST_PER_PARCEL_KEY: [
        PARCEL_ASSESSMENT_KEY,
        FLEET_CAPACITY_KEY,
        OPERATING_COST_KEY,
    ],

    PROFITABILITY_KEY: [
        PARCEL_ASSESSMENT_KEY,
        OPERATING_COST_KEY,
        COST_PER_PARCEL_KEY,
    ],

    SCENARIO_SIMULATION_KEY: [
        PARCEL_ASSESSMENT_KEY,
        FLEET_CAPACITY_KEY,
        OPERATING_COST_KEY,
        COST_PER_PARCEL_KEY,
        PROFITABILITY_KEY,
    ],
}


# =========================================================
# DEFAULT SESSION STRUCTURE
# =========================================================
DEFAULT_SESSION_STATE: dict[str, Any] = {
    SHIPMENT_INFORMATION_KEY: {},
    ROUTE_INTELLIGENCE_KEY: {},
    PARCEL_ASSESSMENT_KEY: {},
    FLEET_CAPACITY_KEY: {},
    OPERATING_COST_KEY: {},
    COST_PER_PARCEL_KEY: {},
    PROFITABILITY_KEY: {},
    SCENARIO_SIMULATION_KEY: {},

    PAGE_STATUS_KEY: {
        page_key: False
        for page_key in PAGE_SEQUENCE
    },

    PAGE_UPDATED_AT_KEY: {
        page_key: None
        for page_key in PAGE_SEQUENCE
    },

    APP_METADATA_KEY: {
        "session_started_at": None,
        "last_updated_at": None,
        "application_version": "1.0",
    },
}


# =========================================================
# INITIALISATION
# =========================================================
def initialise_session_state() -> None:
    """
    Initialise all required Streamlit session-state keys.

    Existing values are preserved.

    This function should be called near the top of every page,
    after st.set_page_config().
    """

    for key, default_value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(
                default_value
            )

    metadata = st.session_state[
        APP_METADATA_KEY
    ]

    if not metadata.get(
        "session_started_at"
    ):
        current_time = get_current_timestamp()

        metadata[
            "session_started_at"
        ] = current_time

        metadata[
            "last_updated_at"
        ] = current_time


def ensure_session_state() -> None:
    """
    Alias for initialise_session_state().
    """

    initialise_session_state()


# =========================================================
# TIMESTAMP
# =========================================================
def get_current_timestamp() -> str:
    """
    Return the current timestamp in ISO format.

    Example
    -------
    2026-07-23T16:30:00
    """

    return datetime.now().isoformat(
        timespec="seconds"
    )


# =========================================================
# PAGE-KEY VALIDATION
# =========================================================
def validate_page_key(
    page_key: str,
) -> str:
    """
    Validate and return a recognised page key.
    """

    if page_key not in PAGE_SEQUENCE:
        valid_keys = ", ".join(
            PAGE_SEQUENCE
        )

        raise KeyError(
            f"Unknown session page key: "
            f"{page_key}. Valid keys: "
            f"{valid_keys}"
        )

    return page_key


# =========================================================
# SAVE PAGE DATA
# =========================================================
def save_page_data(
    page_key: str,
    data: dict[str, Any],
    clear_downstream: bool = True,
    merge_existing: bool = False,
) -> dict[str, Any]:
    """
    Save a page result into Streamlit session state.

    Parameters
    ----------
    page_key:
        Session-state key, for example:
        "parcel_assessment"

    data:
        Dictionary containing page output.

    clear_downstream:
        Clear dependent later-page results when an earlier
        page is updated.

    merge_existing:
        Merge new values with existing page data instead of
        replacing the entire record.

    Returns
    -------
    dict[str, Any]
        The saved page data.
    """

    initialise_session_state()

    validated_key = validate_page_key(
        page_key
    )

    if not isinstance(data, dict):
        raise TypeError(
            "Page data must be provided as a dictionary."
        )

    if clear_downstream:
        clear_downstream_pages(
            page_key=validated_key,
            include_current=False,
        )

    if merge_existing:
        existing_data = get_page_data(
            validated_key
        )

        saved_data = {
            **existing_data,
            **deepcopy(data),
        }

    else:
        saved_data = deepcopy(
            data
        )

    current_time = get_current_timestamp()

    st.session_state[
        validated_key
    ] = saved_data

    st.session_state[
        PAGE_STATUS_KEY
    ][validated_key] = bool(
        saved_data
    )

    st.session_state[
        PAGE_UPDATED_AT_KEY
    ][validated_key] = current_time

    st.session_state[
        APP_METADATA_KEY
    ][
        "last_updated_at"
    ] = current_time

    return deepcopy(
        saved_data
    )


# =========================================================
# LOAD PAGE DATA
# =========================================================
def get_page_data(
    page_key: str,
    default: dict[str, Any] | None = None,
    copy_data: bool = True,
) -> dict[str, Any]:
    """
    Retrieve page data from session state.

    Parameters
    ----------
    page_key:
        Session-state page key.

    default:
        Value returned when no data exists.

    copy_data:
        Return a deep copy to prevent accidental mutation.

    Returns
    -------
    dict[str, Any]
    """

    initialise_session_state()

    validated_key = validate_page_key(
        page_key
    )

    fallback = (
        default
        if default is not None
        else {}
    )

    page_data = st.session_state.get(
        validated_key,
        fallback,
    )

    if not isinstance(page_data, dict):
        return deepcopy(
            fallback
        )

    if copy_data:
        return deepcopy(
            page_data
        )

    return page_data


def load_page_data(
    page_key: str,
    default: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Alias for get_page_data().
    """

    return get_page_data(
        page_key=page_key,
        default=default,
    )


# =========================================================
# GET ONE SESSION VALUE
# =========================================================
def get_page_value(
    page_key: str,
    field_name: str,
    default: Any = None,
) -> Any:
    """
    Retrieve one value from a saved page dictionary.

    Example
    -------
    parcel_quantity = get_page_value(
        "parcel_assessment",
        "parcel_quantity",
        0,
    )
    """

    page_data = get_page_data(
        page_key
    )

    return page_data.get(
        field_name,
        default,
    )


# =========================================================
# UPDATE ONE OR MORE PAGE VALUES
# =========================================================
def update_page_data(
    page_key: str,
    updates: dict[str, Any],
    clear_downstream: bool = True,
) -> dict[str, Any]:
    """
    Update selected fields within an existing page record.
    """

    return save_page_data(
        page_key=page_key,
        data=updates,
        clear_downstream=clear_downstream,
        merge_existing=True,
    )


# =========================================================
# PAGE COMPLETION
# =========================================================
def is_page_complete(
    page_key: str,
    required_fields: Iterable[str] | None = None,
) -> bool:
    """
    Check whether a page has been completed.

    When required_fields are supplied, each field must exist
    and contain a meaningful value.
    """

    initialise_session_state()

    validated_key = validate_page_key(
        page_key
    )

    page_data = get_page_data(
        validated_key
    )

    if not page_data:
        return False

    if required_fields is None:
        return bool(
            st.session_state[
                PAGE_STATUS_KEY
            ].get(
                validated_key,
                False,
            )
        )

    for field_name in required_fields:
        if field_name not in page_data:
            return False

        field_value = page_data[
            field_name
        ]

        if field_value is None:
            return False

        if isinstance(
            field_value,
            str,
        ) and not field_value.strip():
            return False

        if isinstance(
            field_value,
            (
                dict,
                list,
                tuple,
                set,
            ),
        ) and not field_value:
            return False

    return True


def mark_page_complete(
    page_key: str,
    completed: bool = True,
) -> None:
    """
    Manually set page-completion status.
    """

    initialise_session_state()

    validated_key = validate_page_key(
        page_key
    )

    st.session_state[
        PAGE_STATUS_KEY
    ][validated_key] = bool(
        completed
    )


# =========================================================
# REQUIRED DEPENDENCIES
# =========================================================
def get_page_dependencies(
    page_key: str,
) -> list[str]:
    """
    Return dependency keys for a page.
    """

    validated_key = validate_page_key(
        page_key
    )

    return list(
        PAGE_DEPENDENCIES.get(
            validated_key,
            [],
        )
    )


def get_missing_dependencies(
    page_key: str,
) -> list[str]:
    """
    Return incomplete dependency keys for a page.
    """

    dependencies = get_page_dependencies(
        page_key
    )

    return [
        dependency
        for dependency in dependencies
        if not is_page_complete(
            dependency
        )
    ]


def get_missing_dependency_names(
    page_key: str,
) -> list[str]:
    """
    Return user-friendly names for incomplete dependencies.
    """

    missing_keys = get_missing_dependencies(
        page_key
    )

    return [
        PAGE_DISPLAY_NAMES.get(
            key,
            key,
        )
        for key in missing_keys
    ]


def validate_page_dependencies(
    page_key: str,
    stop_page: bool = False,
) -> bool:
    """
    Check that all prerequisite pages are complete.

    When stop_page=True, st.stop() is called after displaying
    the warning.
    """

    missing_names = get_missing_dependency_names(
        page_key
    )

    if not missing_names:
        return True

    missing_text = ", ".join(
        missing_names
    )

    st.warning(
        "Complete and save the following page(s) first: "
        f"{missing_text}."
    )

    if stop_page:
        st.stop()

    return False


# =========================================================
# CLEAR ONE PAGE
# =========================================================
def clear_page_data(
    page_key: str,
    clear_downstream: bool = True,
) -> None:
    """
    Clear one page result.

    By default, later dependent pages are also cleared.
    """

    initialise_session_state()

    validated_key = validate_page_key(
        page_key
    )

    if clear_downstream:
        clear_downstream_pages(
            page_key=validated_key,
            include_current=True,
        )

        return

    st.session_state[
        validated_key
    ] = {}

    st.session_state[
        PAGE_STATUS_KEY
    ][validated_key] = False

    st.session_state[
        PAGE_UPDATED_AT_KEY
    ][validated_key] = None

    st.session_state[
        APP_METADATA_KEY
    ][
        "last_updated_at"
    ] = get_current_timestamp()


# =========================================================
# DOWNSTREAM PAGES
# =========================================================
def get_downstream_pages(
    page_key: str,
    include_current: bool = False,
) -> list[str]:
    """
    Return all pages positioned after the selected page.
    """

    validated_key = validate_page_key(
        page_key
    )

    current_index = PAGE_SEQUENCE.index(
        validated_key
    )

    start_index = (
        current_index
        if include_current
        else current_index + 1
    )

    return PAGE_SEQUENCE[
        start_index:
    ]


def clear_downstream_pages(
    page_key: str,
    include_current: bool = False,
) -> list[str]:
    """
    Clear all downstream page results.

    Example
    -------
    When Shipment Information changes, the route, parcel,
    fleet, cost, profitability and scenario results become
    outdated and should be cleared.
    """

    initialise_session_state()

    pages_to_clear = get_downstream_pages(
        page_key=page_key,
        include_current=include_current,
    )

    for downstream_key in pages_to_clear:
        st.session_state[
            downstream_key
        ] = {}

        st.session_state[
            PAGE_STATUS_KEY
        ][downstream_key] = False

        st.session_state[
            PAGE_UPDATED_AT_KEY
        ][downstream_key] = None

    if pages_to_clear:
        st.session_state[
            APP_METADATA_KEY
        ][
            "last_updated_at"
        ] = get_current_timestamp()

    return pages_to_clear


# =========================================================
# RESET APPLICATION
# =========================================================
def reset_application(
    preserve_keys: Iterable[str] | None = None,
) -> None:
    """
    Reset the complete application session.

    Parameters
    ----------
    preserve_keys:
        Optional session-state keys that should not be removed.

    This is useful when retaining user preferences or a theme.
    """

    preserved_keys = set(
        preserve_keys or []
    )

    preserved_values = {
        key: deepcopy(
            st.session_state[key]
        )
        for key in preserved_keys
        if key in st.session_state
    }

    for key in list(
        st.session_state.keys()
    ):
        del st.session_state[key]

    initialise_session_state()

    for key, value in preserved_values.items():
        st.session_state[key] = value


def reset_analysis() -> None:
    """
    Reset all courier-analysis outputs.
    """

    reset_application()


# =========================================================
# SESSION SNAPSHOT
# =========================================================
def get_session_snapshot(
    include_metadata: bool = True,
) -> dict[str, Any]:
    """
    Return a deep copy of the current application session.

    Useful for:
    - Export
    - Debugging
    - Audit
    - Management dashboard
    """

    initialise_session_state()

    snapshot = {
        page_key: get_page_data(
            page_key
        )
        for page_key in PAGE_SEQUENCE
    }

    snapshot[
        PAGE_STATUS_KEY
    ] = deepcopy(
        st.session_state[
            PAGE_STATUS_KEY
        ]
    )

    snapshot[
        PAGE_UPDATED_AT_KEY
    ] = deepcopy(
        st.session_state[
            PAGE_UPDATED_AT_KEY
        ]
    )

    if include_metadata:
        snapshot[
            APP_METADATA_KEY
        ] = deepcopy(
            st.session_state[
                APP_METADATA_KEY
            ]
        )

    return snapshot


# =========================================================
# RESTORE SESSION SNAPSHOT
# =========================================================
def restore_session_snapshot(
    snapshot: dict[str, Any],
) -> None:
    """
    Restore application session data from a saved snapshot.
    """

    if not isinstance(snapshot, dict):
        raise TypeError(
            "Session snapshot must be a dictionary."
        )

    initialise_session_state()

    for page_key in PAGE_SEQUENCE:
        restored_data = snapshot.get(
            page_key,
            {},
        )

        if isinstance(
            restored_data,
            dict,
        ):
            st.session_state[
                page_key
            ] = deepcopy(
                restored_data
            )

            st.session_state[
                PAGE_STATUS_KEY
            ][page_key] = bool(
                restored_data
            )

    restored_status = snapshot.get(
        PAGE_STATUS_KEY
    )

    if isinstance(
        restored_status,
        dict,
    ):
        for page_key in PAGE_SEQUENCE:
            if page_key in restored_status:
                st.session_state[
                    PAGE_STATUS_KEY
                ][page_key] = bool(
                    restored_status[
                        page_key
                    ]
                )

    restored_timestamps = snapshot.get(
        PAGE_UPDATED_AT_KEY
    )

    if isinstance(
        restored_timestamps,
        dict,
    ):
        for page_key in PAGE_SEQUENCE:
            st.session_state[
                PAGE_UPDATED_AT_KEY
            ][page_key] = (
                restored_timestamps.get(
                    page_key
                )
            )

    restored_metadata = snapshot.get(
        APP_METADATA_KEY
    )

    if isinstance(
        restored_metadata,
        dict,
    ):
        st.session_state[
            APP_METADATA_KEY
        ].update(
            deepcopy(
                restored_metadata
            )
        )

    st.session_state[
        APP_METADATA_KEY
    ][
        "last_updated_at"
    ] = get_current_timestamp()


# =========================================================
# WORKFLOW STATUS
# =========================================================
def get_workflow_status() -> list[dict[str, Any]]:
    """
    Return page-completion information for a progress display.
    """

    initialise_session_state()

    workflow_status = []

    for page_number, page_key in enumerate(
        PAGE_SEQUENCE,
        start=1,
    ):
        completed = is_page_complete(
            page_key
        )

        workflow_status.append(
            {
                "page_number": page_number,
                "page_key": page_key,
                "page_name": (
                    PAGE_DISPLAY_NAMES[
                        page_key
                    ]
                ),
                "completed": completed,
                "status": (
                    "Completed"
                    if completed
                    else "Pending"
                ),
                "updated_at": (
                    st.session_state[
                        PAGE_UPDATED_AT_KEY
                    ].get(
                        page_key
                    )
                ),
            }
        )

    return workflow_status


def calculate_workflow_progress() -> dict[str, Any]:
    """
    Calculate overall workflow progress.
    """

    workflow_status = get_workflow_status()

    completed_pages = sum(
        1
        for page in workflow_status
        if page["completed"]
    )

    total_pages = len(
        workflow_status
    )

    progress_ratio = (
        completed_pages
        / total_pages
        if total_pages > 0
        else 0
    )

    progress_pct = (
        progress_ratio
        * 100
    )

    return {
        "completed_pages": completed_pages,
        "total_pages": total_pages,
        "progress_ratio": progress_ratio,
        "progress_pct": progress_pct,
        "workflow_status": workflow_status,
    }


# =========================================================
# LATEST COMPLETED PAGE
# =========================================================
def get_latest_completed_page() -> dict[str, Any] | None:
    """
    Return the latest completed page in workflow order.
    """

    initialise_session_state()

    for page_key in reversed(
        PAGE_SEQUENCE
    ):
        if is_page_complete(
            page_key
        ):
            return {
                "page_key": page_key,
                "page_name": (
                    PAGE_DISPLAY_NAMES[
                        page_key
                    ]
                ),
                "updated_at": (
                    st.session_state[
                        PAGE_UPDATED_AT_KEY
                    ].get(
                        page_key
                    )
                ),
            }

    return None


# =========================================================
# PAGE-SPECIFIC SHORTCUTS
# =========================================================
def get_shipment_information() -> dict[str, Any]:
    return get_page_data(
        SHIPMENT_INFORMATION_KEY
    )


def get_route_intelligence() -> dict[str, Any]:
    return get_page_data(
        ROUTE_INTELLIGENCE_KEY
    )


def get_parcel_assessment() -> dict[str, Any]:
    return get_page_data(
        PARCEL_ASSESSMENT_KEY
    )


def get_fleet_capacity() -> dict[str, Any]:
    return get_page_data(
        FLEET_CAPACITY_KEY
    )


def get_operating_cost() -> dict[str, Any]:
    return get_page_data(
        OPERATING_COST_KEY
    )


def get_cost_per_parcel() -> dict[str, Any]:
    return get_page_data(
        COST_PER_PARCEL_KEY
    )


def get_profitability() -> dict[str, Any]:
    return get_page_data(
        PROFITABILITY_KEY
    )


def get_scenario_simulation() -> dict[str, Any]:
    return get_page_data(
        SCENARIO_SIMULATION_KEY
    )