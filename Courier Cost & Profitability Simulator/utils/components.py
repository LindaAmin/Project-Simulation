"""
Reusable Streamlit UI components for the Courier Analysis application.

Responsibilities
----------------
- Page headings
- Section headings
- Notes and information boxes
- Status messages
- Metric rows
- Empty-state messages
- Dividers
- Cost-basis explanations

This module must not contain:
- Business calculations
- CSV loading
- Session-state logic
- Page configuration
"""

from __future__ import annotations

from typing import Any

import streamlit as st


# =========================================================
# INTERNAL HELPERS
# =========================================================
def _clean_text(
    value: Any,
) -> str:
    """
    Convert a value into clean display text.
    """

    if value is None:
        return ""

    return " ".join(
        str(value).split()
    )


def _title_with_icon(
    title: str,
    icon: str = "",
) -> str:
    """
    Combine an optional icon and title.
    """

    clean_title = _clean_text(
        title
    )

    clean_icon = _clean_text(
        icon
    )

    if clean_icon:
        return f"{clean_icon} {clean_title}"

    return clean_title


# =========================================================
# PAGE HEADER
# =========================================================
def page_header(
    title: str,
    subtitle: str = "",
    icon: str = "",
) -> None:
    """
    Display a page title and optional subtitle.
    """

    display_title = _title_with_icon(
        title=title,
        icon=icon,
    )

    st.title(
        display_title
    )

    if subtitle:
        st.caption(
            _clean_text(
                subtitle
            )
        )


# =========================================================
# SECTION TITLES
# =========================================================
def section_title(
    title: str,
    icon: str = "",
) -> None:
    """
    Display a major section heading.
    """

    display_title = _title_with_icon(
        title=title,
        icon=icon,
    )

    st.markdown(
        f"### {display_title}"
    )


def subsection_title(
    title: str,
    icon: str = "",
) -> None:
    """
    Display a subsection heading.
    """

    display_title = _title_with_icon(
        title=title,
        icon=icon,
    )

    st.markdown(
        f"#### {display_title}"
    )


# =========================================================
# DIVIDER
# =========================================================
def divider() -> None:
    """
    Display a horizontal divider.
    """

    st.divider()


# =========================================================
# NOTE BOX
# =========================================================
def note_box(
    title: str,
    message: str,
    icon: str = "📝",
) -> None:
    """
    Display a standard explanatory note.
    """

    display_title = _title_with_icon(
        title=title,
        icon=icon,
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"**{display_title}**"
        )

        st.write(
            message
        )


# =========================================================
# INFORMATION BOX
# =========================================================
def info_box(
    title: str,
    message: str,
    icon: str = "ℹ️",
) -> None:
    """
    Display an informational message.
    """

    display_title = _title_with_icon(
        title=title,
        icon=icon,
    )

    st.info(
        f"**{display_title}**\n\n{message}"
    )


# =========================================================
# STATUS BOX
# =========================================================
def status_box(
    status: str,
    title: str,
    message: str,
) -> None:
    """
    Display a status-based message.

    Supported status values:
    - success
    - warning
    - error
    - info
    """

    normalised_status = (
        str(status)
        .strip()
        .lower()
    )

    content = (
        f"**{_clean_text(title)}**"
        f"\n\n{message}"
    )

    if normalised_status == "success":
        st.success(
            content
        )

    elif normalised_status == "warning":
        st.warning(
            content
        )

    elif normalised_status == "error":
        st.error(
            content
        )

    else:
        st.info(
            content
        )


# =========================================================
# EMPTY STATE
# =========================================================
def empty_state(
    title: str,
    message: str,
    icon: str = "📭",
) -> None:
    """
    Display an empty-state card.
    """

    display_title = _title_with_icon(
        title=title,
        icon=icon,
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### {display_title}"
        )

        st.caption(
            message
        )


# =========================================================
# METRIC CARDS
# =========================================================
def metric_cards(
    metrics: list[dict[str, Any]],
    columns: int | None = None,
) -> None:
    """
    Display multiple Streamlit metric cards.

    Example
    -------
    metric_cards(
        metrics=[
            {
                "label": "Total Parcels",
                "value": "100,000",
            },
            {
                "label": "Operating Cost",
                "value": "RM 250,000",
                "delta": "-2.5%",
            },
        ],
        columns=2,
    )
    """

    if not metrics:
        return

    requested_columns = (
        columns
        if columns is not None
        else len(metrics)
    )

    column_count = max(
        int(requested_columns),
        1,
    )

    metric_columns = st.columns(
        column_count
    )

    for index, metric in enumerate(
        metrics
    ):
        target_column = metric_columns[
            index % column_count
        ]

        with target_column:
            st.metric(
                label=_clean_text(
                    metric.get(
                        "label",
                        "",
                    )
                ),
                value=metric.get(
                    "value",
                    "",
                ),
                delta=metric.get(
                    "delta",
                    None,
                ),
                help=metric.get(
                    "help",
                    None,
                ),
            )


# =========================================================
# COST BASIS
# =========================================================
def cost_basis(
    title: str = "Calculation Basis",
    message: str | None = None,
    items: list[str] | None = None,
    basis: str | None = None,
) -> None:
    """
    Display the assumptions or calculation basis used by a page.

    Supported usage
    ---------------
    cost_basis()

    cost_basis(
        title="Shipment Information Basis",
        message="Shipment assumptions support later calculations.",
    )

    cost_basis(
        title="Operating Cost Basis",
        items=[
            "Fuel cost based on journey distance",
            "Manpower cost based on working hours",
        ],
    )

    cost_basis(
        basis="Per shipment",
    )
    """

    default_items = [
        "Per shipment",
        "Per parcel",
        "Per kilogram",
        "Per cubic metre",
        "Per vehicle",
        "Per kilometre",
    ]

    if basis:
        selected_items = [
            basis
        ]

    elif items is not None:
        selected_items = [
            _clean_text(
                item
            )
            for item in items
            if _clean_text(
                item
            )
        ]

    else:
        selected_items = (
            default_items
        )

    with st.container(
        border=True
    ):
        st.markdown(
            f"**📌 {_clean_text(title)}**"
        )

        if message:
            st.write(
                message
            )

        if selected_items:
            for item in selected_items:
                st.markdown(
                    f"- {item}"
                )