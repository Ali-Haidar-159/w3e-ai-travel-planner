"""
Utilities for creating and saving travel plan markdown output.
"""

import os
from datetime import datetime
from typing import Mapping, Optional


def build_final_markdown(
    destination: str,
    travel_dates: str,
    budget: float,
    duration_days: int,
    sections: Mapping[str, str],
) -> str:
   
    return f"""# AI Travel Plan

Destination: {destination}
Travel Dates: {travel_dates}
Budget: USD {budget:,.2f}
Duration: {duration_days} days

## Destination Overview

{sections["destination"]}

## Budget Breakdown

{sections["budget"]}

## Day-wise Itinerary

{sections["itinerary"]}

## Validation Summary

{sections["validation"]}
"""


def save_markdown_output(destination: str, content: str) -> Optional[str]:
    safe_dest = destination.replace(" ", "_").replace(",", "")
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"travel_plan_{safe_dest}_{ts_str}.md")

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(content)
        return output_filename
    except IOError:
        return None
