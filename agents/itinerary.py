from crewai import Agent
from tools import serper_search


def create_itinerary_designer(llm) -> Agent:
    """
    Returns the Itinerary Designer agent.

    Responsibilities:
    - Create a detailed day-by-day itinerary for the full trip duration
    - Group geographically close attractions on the same day
    - Include realistic timings and travel time between locations
    - Respect typical opening hours (search if unsure)
    - Include at least one restaurant recommendation per day
    - Handle Day 1 arrival logistics and last-day departure logistics
    """
    return Agent(
        role="Itinerary Designer",
        goal=(
            "Design a detailed, realistic, and conflict-free day-by-day travel itinerary "
            "that respects opening hours, minimises unnecessary travel, balances sightseeing "
            "with rest, and fits within the approved budget. "
            "Use SerperSearch to verify opening hours and prices when unsure."
        ),
        backstory=(
            "You are a professional tour designer who has crafted thousands of travel "
            "itineraries for travel agencies worldwide. You have an instinct for pacing – "
            "you know that rushing tourists is as bad as boring them. You group attractions "
            "geographically, you never double-book, and you always leave room for spontaneous "
            "exploration. You treat every day as a story with a theme."
        ),
        tools=[serper_search],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=6,
        max_retry_limit=2,
    )


def create_itinerary_task(agent, destination: str, travel_dates: str,
                          duration_days: int, preferences: str,
                          context_tasks: list):
    """Returns the Task object for itinerary design."""
    from crewai import Task

    return Task(
        description=(
            f"Create a concise day-wise itinerary for {duration_days} days in {destination}.\n"
            f"Travel dates: {travel_dates}. Preferences: {preferences}.\n"
            "Include arrival on Day 1 and departure on last day."
        ),
        expected_output=(
            "Markdown only:\n"
            "- For each day: heading and 3-4 bullet points\n"
            "- Each bullet includes time range and estimated cost\n"
            "- End each day with one-line daily total\n"
            "Keep each day under 80 words."
        ),
        agent=agent,
        context=context_tasks,
    )
