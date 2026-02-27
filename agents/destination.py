from crewai import Agent
from tools import serper_search


def create_destination_researcher(llm) -> Agent:
    """
    Returns the Destination Researcher agent.

    Responsibilities:
    - Search for top attractions and highlights at the destination
    - Find best neighbourhoods to stay
    - Research local cuisine and restaurant options
    - Identify transport options (airport transfers, local metro/bus/taxi)
    - Collect cultural tips and etiquette notes
    - Report typical weather during the travel dates
    """
    return Agent(
        role="Destination Researcher",
        goal=(
            "Thoroughly research the travel destination using only the SerperSearch tool. "
            "Produce an accurate, up-to-date Destination Overview covering attractions, "
            "stay areas, food, transport, culture, and weather. "
            "Never fabricate facts – every claim must come from a search result."
        ),
        backstory=(
            "You are a seasoned travel journalist who has visited over 80 countries. "
            "You are famous for your obsessive fact-checking and your ability to surface "
            "hidden gems alongside iconic landmarks. You always cite your sources and "
            "refuse to guess – if you don't know something you search for it."
        ),
        tools=[serper_search],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5,
        max_retry_limit=2,
    )


def create_destination_research_task(agent, destination: str, travel_dates: str,
                                     duration_days: int, preferences: str):
    """Returns the Task object for destination research."""
    from crewai import Task

    return Task(
        description=(
            f"Research {destination} for dates {travel_dates} ({duration_days} days).\n"
            f"Preferences: {preferences}.\n"
            "Use SerperSearch and return concise, practical information only."
        ),
        expected_output=(
            "Markdown with these short sections:\n"
            "- Highlights: 5 bullets\n"
            "- Best Areas to Stay: max 3 bullets\n"
            "- Food and Drink: max 5 bullets\n"
            "- Getting Around: max 5 bullets\n"
            "- Cultural Tips: max 5 bullets\n"
            "- Weather and Packing: max 4 bullets\n"
            "Keep total output under 250 words."
        ),
        agent=agent,
    )
