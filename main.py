"""
main.py
AI Travel Planner multi-agent entry point.
"""

import os
import sys
import re
import threading
from datetime import datetime
from dotenv import load_dotenv

os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("CREWAI_DISABLE_TRACKING", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("XDG_DATA_HOME", os.path.join(os.getcwd(), ".local_share"))

from crewai import Crew, Process, LLM
from crewai.events import event_context

# Load environment variables from .env
load_dotenv()

# Suppress noisy event pairing warnings from CrewAI internals.
event_context._default_config.mismatch_behavior = event_context.MismatchBehavior.SILENT
event_context._default_config.empty_pop_behavior = event_context.MismatchBehavior.SILENT

from agents import (
    create_destination_researcher, create_destination_research_task,
    create_budget_planner,        create_budget_task,
    create_itinerary_designer,    create_itinerary_task,
    create_validation_agent,      create_validation_task,
)
from utils.logger_setup import configure_travel_planner_logger
from utils.markdown_output import build_final_markdown, save_markdown_output

logger = configure_travel_planner_logger()


def log_crew_usage_metrics(crew: Crew) -> None:
    """Log aggregate CrewAI token usage after kickoff."""
    usage = getattr(crew, "usage_metrics", None)
    if not usage:
        return

    logger.info(
        (
            "Crew total token usage | prompt=%s completion=%s "
            "cached_prompt=%s total=%s requests=%s"
        ),
        getattr(usage, "prompt_tokens", 0),
        getattr(usage, "completion_tokens", 0),
        getattr(usage, "cached_prompt_tokens", 0),
        getattr(usage, "total_tokens", 0),
        getattr(usage, "successful_requests", 0),
    )


def get_llm():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        logger.error("GROQ_API_KEY is not set. Please add it to your .env file.")
        sys.exit(1)
    llm = LLM(
        model="llama-3.3-70b-versatile" ,
        provider="openai",
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        temperature=0.3,
    )
    return llm


def run_travel_planner(
    destination: str,
    travel_dates: str,
    budget: float,
    duration_days: int,
    preferences: str = "None specified",
) -> str:
    """
    Orchestrate the CrewAI multi-agent travel planner.

    Parameters
    ----------
    destination   : e.g. "Tokyo, Japan"
    travel_dates  : e.g. "March 15 – March 22, 2025"
    budget        : total budget in USD, e.g. 2000.0
    duration_days : number of travel days, e.g. 7
    preferences   : optional traveller preferences, e.g. "cultural, budget-friendly"

    Returns
    -------
    Final travel plan as a Markdown string (also saved to a .md file).
    """
    logger.info("Starting planner for %s", destination)

    llm = get_llm()

    researcher  = create_destination_researcher(llm)
    budgeter    = create_budget_planner(llm)
    designer    = create_itinerary_designer(llm)
    validator   = create_validation_agent(llm)

    task_research   = create_destination_research_task(
        researcher, destination, travel_dates, duration_days, preferences
    )
    task_budget     = create_budget_task(
        budgeter, destination, budget, duration_days, preferences,
        context_tasks=[task_research]
    )
    task_itinerary  = create_itinerary_task(
        designer, destination, travel_dates, duration_days, preferences,
        context_tasks=[task_research, task_budget]
    )
    task_validation = create_validation_task(
        validator, destination, budget, duration_days,
        context_tasks=[task_research, task_budget, task_itinerary]
    )
    crew = Crew(
        agents=[researcher, budgeter, designer, validator],
        tasks=[task_research, task_budget, task_itinerary, task_validation],
        process=Process.sequential,
        verbose=False,
    )

    sections = {
        "destination": "Could not generate destination overview.",
        "budget": "Could not generate budget breakdown.",
        "itinerary": "Could not generate day-wise itinerary.",
        "validation": "Could not generate validation summary.",
    }

    stop_progress = threading.Event()

    def progress_logger() -> None:
        messages = [
            "Working: researching destination details...",
            "Working: estimating budget and daily costs...",
            "Working: building day-wise itinerary...",
            "Working: validating the full plan...",
        ]
        i = 0
        while not stop_progress.is_set():
            logger.info(messages[i % len(messages)])
            i += 1
            stop_progress.wait(3)

    progress_thread = threading.Thread(target=progress_logger, daemon=True)
    progress_thread.start()

    try:
        result = crew.kickoff()
        log_crew_usage_metrics(crew)
        if hasattr(result, "tasks_output") and len(result.tasks_output) >= 4:
            sections["destination"] = result.tasks_output[0].raw or sections["destination"]
            sections["budget"] = result.tasks_output[1].raw or sections["budget"]
            sections["itinerary"] = result.tasks_output[2].raw or sections["itinerary"]
            sections["validation"] = result.tasks_output[3].raw or sections["validation"]
        else:
            sections["validation"] = str(result)
    except Exception as exc:
        logger.error("Crew execution failed: %s", exc)
        sections["validation"] = f"Crew execution failed: {exc}"
    finally:
        stop_progress.set()
        progress_thread.join(timeout=0.2)

    final_document = build_final_markdown(
        destination=destination,
        travel_dates=travel_dates,
        budget=budget,
        duration_days=duration_days,
        sections=sections,
    )
    output_filename = save_markdown_output(destination=destination, content=final_document)
    if output_filename:
        logger.info("Saved: %s", output_filename)
    else:
        logger.error("Could not save output file.")

    logger.info("Done")
    return final_document


def infer_duration_days(travel_dates: str) -> int:
    """Infer inclusive duration from common date range formats; fallback to 7 days."""
    cleaned = travel_dates.strip()
    # Normalize common user input variants like "April 13 , 2026"
    cleaned = re.sub(r"\s*,\s*", ", ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    def inclusive_days(start: datetime, end: datetime) -> int:
        return max((end - start).days + 1, 1)

    # YYYY-MM-DD to YYYY-MM-DD
    m = re.search(r"(\d{4}-\d{2}-\d{2}).*?(\d{4}-\d{2}-\d{2})", cleaned)
    if m:
        start = datetime.strptime(m.group(1), "%Y-%m-%d")
        end = datetime.strptime(m.group(2), "%Y-%m-%d")
        return inclusive_days(start, end)

    # Month DD, YYYY - Month DD, YYYY
    m = re.search(
        r"([A-Za-z]+ \d{1,2}, \d{4}).*?([A-Za-z]+ \d{1,2}, \d{4})",
        cleaned,
    )
    if m:
        start = datetime.strptime(m.group(1), "%B %d, %Y")
        end = datetime.strptime(m.group(2), "%B %d, %Y")
        return inclusive_days(start, end)

    # Month DD - Month DD, YYYY
    m = re.search(
        r"([A-Za-z]+ \d{1,2}).*?([A-Za-z]+ \d{1,2}, \d{4})",
        cleaned,
    )
    if m:
        end = datetime.strptime(m.group(2), "%B %d, %Y")
        start = datetime.strptime(f"{m.group(1)}, {end.year}", "%B %d, %Y")
        return inclusive_days(start, end)

    return 7


def get_user_input() -> dict:
    destination = input("Destination: ").strip()
    travel_dates = input("Travel dates: ").strip()
    budget_text = input("Budget (USD): ").strip()

    try:
        budget = float(budget_text.replace(",", ""))
    except ValueError:
        logger.error("Invalid budget. Use a number, for example 2000")
        sys.exit(1)

    if not destination or not travel_dates:
        logger.error("Destination and travel dates are required.")
        sys.exit(1)

    return {
        "destination": destination,
        "travel_dates": travel_dates,
        "budget": budget,
        "duration_days": infer_duration_days(travel_dates),
        "preferences": "None specified",
    }


if __name__ == "__main__":
    user_input = get_user_input()
    run_travel_planner(**user_input)
