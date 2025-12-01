🚀 Smart Career Guidance Agent: A Multi-Agent Strategist

This project implements a sophisticated Multi-Agent System (MAS) designed to provide autonomous, personalized, and data-driven career upskilling roadmaps. It replaces generic career advice by leveraging real-time market data and layered memory.

🧐 Core Architecture & Features

1. The Three-Agent Flow

The system operates as a sequential consulting firm, enforcing high data integrity via A2A communication.

Agent Role

Responsibility

Key Feature

Output

Profiler Agent

Data Elicitation & Standardization

Session Memory Management

UserProfile JSON Schema

Market Analyst

Real-Time Gap Analysis

Dynamic Tool Use (Web Search)

MarketAnalysis JSON Schema

Strategist Agent

Strategy Synthesis & Planning

Long-Term Memory (Knowledge Base)

Final Career Roadmap Report (Markdown)

2. Technical Features

Dynamic Tool Use: The Market Analyst is equipped with a search tool, activated only when external market data is required.

A2A Protocol: Communication between agents is strictly enforced using Pydantic Schemas, ensuring clean, structured data handoffs between the Profiler and Analyst.

Layered Memory: The system utilizes short-term context for conversational flow (Profiler) and integrates a Knowledge Base (simulated in the Strategist's prompt) for resource recommendations (Long-Term Memory).

🛠️ Setup and Installation

1. Prerequisites

Python 3.10+

A Gemini API Key from Google AI Studio.

2. Environment Setup

Clone the repository:

git clone [https://github.com/YourUsername/Smart-Career-Guidance-Agent.git](https://github.com/YourUsername/Smart-Career-Guidance-Agent.git)
cd Smart-Career-Guidance-Agent


Create a virtual environment (Recommended):

python -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


3. API Key Configuration

Create a file named .env in the root directory and add your API key:

GEMINI_API_KEY="YOUR_API_KEY_HERE"


▶️ How to Run the Agent

Execute the main script from your terminal. It will run the entire three-agent sequential process autonomously.

python agent_orchestrator.py


The final, structured roadmap will be printed directly to your console.