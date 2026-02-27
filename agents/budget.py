from crewai import Agent
from tools import serper_search, calculator


def create_budget_planner(llm) -> Agent:
    """
    Returns the Budget Planner agent.

    Responsibilities:
    - Search for current accommodation prices at the destination
    - Research realistic food costs (street food to mid-range restaurants)
    - Estimate local transport daily costs
    - Find entrance fees for major attractions
    - Compute a grand total using the Calculator tool
    - Flag budget warnings if the stated budget is insufficient
    """
    return Agent(
        role="Budget Planner", 
        goal=(
            "Build a realistic, itemised budget breakdown for the trip by searching "
            "for real, current prices with SerperSearch and verifying all arithmetic "
            "with the Calculator tool. "
            "Always flag a BUDGET WARNING if the stated budget is too low for the destination. "
            "Never invent prices – search first, calculate second."
        ),
        backstory=(
            "You are a certified financial travel consultant with 15 years of experience "
            "helping budget-conscious and luxury travellers alike. You have an encyclopedic "
            "knowledge of real-world travel costs and an eagle eye for arithmetic errors. "
            "You always check your totals twice and you never let a client overspend."
        ),
        tools=[serper_search, calculator],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=6,
        max_retry_limit=2,
    )


def create_budget_task(agent, destination: str, budget: float,
                       duration_days: int, preferences: str,
                       context_tasks: list):
    """Returns the Task object for budget planning."""
    from crewai import Task

    return Task(
        description=(
            f"Create a concise budget for {duration_days} days in {destination}.\n"
            f"Budget: USD {budget:,.2f}. Preferences: {preferences}.\n"
            "Use SerperSearch for real prices and Calculator for totals."
        ),
        expected_output=(
            "Markdown with:\n"
            "- One table: Category | Cost (USD)\n"
            "- Grand Total\n"
            "- Budget Status: PASS/WARNING/FAIL with one-line reason\n"
            "Use no more than 150 words outside the table."
        ),
        agent=agent,
        context=context_tasks,
    )
