from crewai import Agent
from tools import serper_search, calculator


def create_validation_agent(llm) -> Agent:
    """
    Returns the Validation Agent.

    Responsibilities:
    - Verify that budget totals are arithmetically correct (use Calculator)
    - Cross-check 2–3 key facts with independent Serper searches
    - Confirm the itinerary has no duplicate or conflicting activities
    - Check visa and entry requirements for the destination
    - Identify risk factors (safety, weather, seasonal closures)
    - List assumptions made by other agents
    - Issue an Overall Recommendation (APPROVED / NEEDS REVISION)
    """
    return Agent(
        role="Validation Agent",
        goal=(
            "Act as a strict quality assurance reviewer. Verify every claim in the travel plan "
            "by re-running independent searches with SerperSearch and re-checking all arithmetic "
            "with the Calculator tool. Identify hallucinations, budget mismatches, itinerary "
            "conflicts, and real-world risks. Produce a clear, honest Validation Summary."
        ),
        backstory=(
            "You are a meticulous travel-plan auditor with a background in both financial "
            "auditing and risk management. You trust no number you haven't verified yourself "
            "and no fact you haven't confirmed independently. You have saved countless travellers "
            "from embarrassing (and expensive) mistakes. Your validation reports are legendary "
            "for their thoroughness."
        ),
        tools=[serper_search, calculator],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5,
        max_retry_limit=2,
    )


def create_validation_task(agent, destination: str, budget: float,
                           duration_days: int, context_tasks: list):
    """Returns the Task object for validation."""
    from crewai import Task

    return Task(
        description=(
            f"Validate the full plan for {destination}.\n"
            f"Budget: USD {budget:,.2f}, Duration: {duration_days} days.\n"
            "Check math, itinerary consistency, and key facts using tools."
        ).format(budget=budget),
        expected_output=(
            "Markdown with short sections:\n"
            "- Budget Check: PASS/FAIL (one line)\n"
            "- Itinerary Check: PASS/FAIL (one line)\n"
            "- Verified Facts: 3 bullets\n"
            "- Risks: up to 3 bullets\n"
            "- Final Recommendation: APPROVED/NEEDS REVISION (one line)\n"
            "Keep total output under 180 words."
        ),
        agent=agent,
        context=context_tasks,
    )
