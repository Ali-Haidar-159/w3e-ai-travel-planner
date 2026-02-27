# AI Travel Planner (CrewAI Multi-Agent CLI)

A command-line travel planner built with CrewAI.

It uses 4 specialized agents to generate a complete Markdown travel plan:
1. Destination research
2. Budget planning
3. Day-wise itinerary design
4. Final validation and risk review

## Features

- Multi-agent architecture with clear responsibility split
- Live web search support via Serper Dev API
- Budget math verification with a restricted calculator tool
- Auto-saved plan output in Markdown
- Run log generation for debugging

## Tech Stack

- Python 3
- CrewAI
- Groq-hosted model through OpenAI-compatible API (`llama-3.3-70b-versatile`)
- Serper Dev Search API
- Requests + python-dotenv

## Project Structure

```text
.
├── main.py
├── requirements.txt
├── agents/
│   ├── destination.py
│   ├── budget.py
│   ├── itinerary.py
│   ├── validation.py
│   └── __init__.py
├── tools/
│   ├── serper_tool.py
│   ├── calculator.py
│   └── __init__.py
├── utils/
│   ├── markdown_output.py
│   └── __init__.py
├── output/
├── sample_output.md
└── README.md
```

## Full Setup (From GitHub Clone)

### 1. Prerequisites

Make sure you have:
- Python 3.10+
- `pip`
- Git

Check versions:

```bash
python --version
git --version
```

### 2. Clone the repository

```bash
git clone https://github.com/Ali-Haidar-159/w3e-ai-travel-planner.git
cd w3e-ai-travel-planner
```

### 3. Create virtual environment

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in project root:

```env
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key
```

Where to get keys:
- Groq API key: https://console.groq.com/keys
- Serper API key: https://serper.dev

### 6. Run the app

```bash
python main.py
```

You will be prompted for:
- `Destination`
- `Travel dates`
- `Budget (USD)`

Example:

```text
Destination:  Japan
Travel dates: April 10, 2026 - April 17, 2026
Budget (USD): 2500
```

## How the Process Works Internally

Execution is sequential (`Process.sequential`):

1. `Destination Researcher`
- Tool: `SerperSearch`
- Output: destination highlights, stay areas, food, transport, weather, culture

2. `Budget Planner`
- Tools: `SerperSearch`, `Calculator`
- Input context: destination research
- Output: itemized budget table + status (PASS/WARNING/FAIL)

3. `Itinerary Designer`
- Tool: `SerperSearch`
- Input context: destination + budget
- Output: day-wise plan with timing and estimated costs

4. `Validation Agent`
- Tools: `SerperSearch`, `Calculator`
- Input context: all previous outputs
- Output: final checks, risks, recommendation

Final result is assembled in `main.py` and saved as Markdown.

## Input Rules

- Destination and travel dates are required.
- Budget must be numeric.
- Duration is inferred automatically from travel dates.
- Duration is calculated inclusively (e.g. April 10 to April 13 = 4 days).
- If date parsing fails, duration defaults to 7 days.

Recognized date patterns:
- `YYYY-MM-DD ... YYYY-MM-DD`
- `Month DD, YYYY ... Month DD, YYYY`
- `Month DD ... Month DD, YYYY`

## Output Files

After each run:
- Plan file: `output/travel_plan_<destination>_<YYYYMMDD_HHMMSS>.md`
- Log file: `travel_planner.log` (overwritten every run)

Generated plan sections:
- Destination Overview
- Budget Breakdown
- Day-wise Itinerary
- Validation Summary

## Troubleshooting

- `GROQ_API_KEY is not set`
  - Add `GROQ_API_KEY` to `.env`.

- Search results look mocked or incomplete
  - Add valid `SERPER_API_KEY` to `.env`.
  - Without this key, `SerperSearch` returns mock text by design.

- `Invalid budget. Use a number`
  - Enter numeric values only (example: `2500` or `2500.50`).

- Empty/low-quality output
  - Retry with more specific destination and date range.
  - Verify API keys are valid and active.

## Security Notes

- Calculator only accepts arithmetic characters (`0-9 + - * / ( ) .` and spaces).
- Calculator eval runs with restricted builtins.
- Agents are configured with `allow_delegation=False`.

## Dependencies

From `requirements.txt`:
- `crewai`
- `python-dotenv`
- `requests`

## Quick Start (Copy/Paste)

```bash
git clone https://github.com/Ali-Haidar-159/w3e-ai-travel-planner.git
cd w3e-ai-travel-planner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
