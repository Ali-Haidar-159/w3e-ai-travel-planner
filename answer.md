# Mandatory Analysis Section

## 1) Why multi-agent?
This codebase uses a 4-agent pipeline . If all the work is done with a single prompt (research + budget + itinerary + validation), then the problem is:

- Answers can be random
- More likely to make mathematical mistakes
- Difficult to verify information
- Accountability is low because 
- responsibilities are not specified

But in a Multi-Agent system:

- Everyone does their own specific work
- Output is clear and constructive

The Agents are : 

- `Destination Researcher` gathers facts (attractions, food, transport, weather).
- `Budget Planner` converts research into itemized costs and uses `Calculator` for arithmetic.
- `Itinerary Designer` builds day-by-day plans using prior research and budget context.
- `Validation Agent` re-checks math/facts and flags risks.

In this implementation (`Process.sequential`), each later task consumes earlier outputs as context, which improves structure and accountability compared to a single prompt trying to do everything at once.

## 2) What if Serper returns incorrect data?
This system uses the SerperSearch tool for web search. If Serper returns incorrect, outdated, or incomplete information, that incorrect information can spread throughout the multi-agent pipeline.

Risk:
- Incorrect or outdated web information
- Research Agent will use that information
- Budget Planner will calculate at the wrong price
- Itinerary Designer will plan in the wrong context
- Validation Agent may not catch errors by relying on the same source

This causes error propagation and the quality of the entire plan may be lost.

## 3) What if budget is unrealistic?
If the budget given by the user is not realistic, the current system can partially detect it, but cannot fully control it.

Current behavior:

1.Budget Agent
- Calculates the total estimated cost
- Returns PASS / WARNING / FAIL
- Flags if the budget is too low

2.Validation Agent
- Re-validates the mathematical calculations
- Provides recommendations (APPROVED / NEEDS REVISION)

3.User input validation (main.py)
- Verifies whether the budget is numeric


## 4) Hallucination risks?
Even though it uses a multi-agent architecture, the system is largely LLM (Large Language Model)-based. So there is still the possibility of errors, fabrications, or confident but incorrect information.

Why:
- Agents rely on LLM outputs even though prompts say “never fabricate.”
- Validation is LLM-based too; it may miss subtle errors.
- Serper snippets are summarized text, not full verified datasets.

Existing controls:
- Tool-constrained workflow (`SerperSearch`, `Calculator`).
- Dedicated validation stage.
- Low temperature (`0.3`) and bounded iteration/retry settings.

Remaining risk areas:
- Unsourced claims in itinerary details (opening hours, fees).
- Confident but stale facts.
- Cascading errors from early tasks.

## 5) Token usage?
Current token profile is moderate per run but can grow with trip length.

#### Why does the token increase? (Drivers)

- 4 Sequential Tasks
In your system, 4 agents work sequentially:

    Research → Budget → Itinerary → Validation

Each subsequent agent takes the output of the previous agent as input as context.
As a result, the token increases as the text accumulates.

🔹Real example

**3 day trip:**

Research: 800 tokens

Budget: 500

Itinerary: 700

Validation: 600

Total ≈ 2600 tokens

**For a 10 day trip:**

The itinerary section will be much larger

More text will go into Validation

Total can be ≈ 4500–6000+ tokens.

## 6) Scalability?
Current design scales well for single CLI runs, but has limits for higher throughput.

Strengths:
- Clear modular agents/tools.
- Deterministic sequential orchestration.
- Stateless run model and markdown output persistence.

Constraints:
- Sequential pipeline increases latency per request.
- External dependency on Serper/Groq APIs (rate limits, outages).
- CLI-oriented input/output (not service-oriented API architecture yet).

What is needed for production scaling:
- Convert to API service + job queue.
- Add observability (metrics for latency, token usage, failure causes).
- Add structured outputs and automated validation gates before final approval.
