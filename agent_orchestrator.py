import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from pydantic import BaseModel, Field
from google import genai
from google.generativeai.errors import APIError
from dotenv import load_dotenv

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()

# --- 1. A2A Communication Schemas (Pydantic) ---
# This ensures structured data handoff between the Profiler and Market Analyst
class UserProfile(BaseModel):
    """Structured data defining the user's current status and goals."""
    current_skills: str = Field(description="Comma-separated list of the user's current professional skills.")
    target_role: str = Field(description="The exact job title the user is aiming for (e.g., Senior Data Scientist).")
    years_of_experience: int = Field(description="Total years of professional experience.")

class MarketAnalysis(BaseModel):
    """Structured data defining the market gap found by the Analyst."""
    required_skills_found: str = Field(description="Comma-separated list of mandatory skills found in job postings for the target role.")
    critical_skill_gap: str = Field(description="The most important 1-3 skills the user is missing based on current market data.")
    average_salary_range: str = Field(description="The current typical salary range for the target role.")

# --- 2. Tool Definition (Dynamic Tool Use) ---
# NOTE: In a real-world scenario, this tool would use a specialized API (like Google Search)
# for real-time data. Here, we simulate the function call structure.

@tool("Google Search Market Data")
def google_search_market_data(target_role: str) -> str:
    """
    Analyzes current Q4 2025 job postings and market trends for a specified job title.
    Returns the required hard skills and salary expectations.
    """
    print(f"\n--- TOOL ACTIVATED: Searching live market data for {target_role} ---")
    
    # Simulation based on target role
    if "Data Analyst" in target_role:
        return (
            "Market Data: The primary mandatory skills for a Junior Data Analyst are: "
            "Advanced SQL, Tableau Visualization, and Python (Pandas/NumPy). "
            "Secondary skills include basic cloud proficiency (AWS/Azure). "
            "Typical salary range in major US metro areas is $75,000 - $95,000."
        )
    elif "Software Engineer" in target_role:
        return (
            "Market Data: Mandatory skills for a Mid-Level Software Engineer are: "
            "Expertise in Python/GoLang, proficiency in Docker/Kubernetes, and AWS/GCP services. "
            "Typical salary range is $120,000 - $160,000."
        )
    else:
        return "Market Data: No specific data found. General requirements: excellent communication, problem-solving, and continuous learning."

# --- 3. Agent Definitions ---

# Shared Configuration
llm = genai.Client(model="gemini-2.5-flash-preview-09-2025")
# The LLM must be passed to the agents when using the Google GenAI library

# 3.1. Profiler Agent (The Interviewer)
profiler_agent = Agent(
    role='Career Profiler',
    goal="""Engage the user to accurately gather their current skills, experience, and specific career goals.
            Structure the raw input into a perfect, validated JSON format using the provided Pydantic Schema.
            Your output MUST be a valid JSON object matching the UserProfile schema.""",
    backstory="A specialized HR consultant focused on deep, conversational skill elicitation. You manage the session context and ensure zero ambiguity in user data.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 3.2. Market Analyst Agent (The Data Scientist)
market_analyst = Agent(
    role='Real-Time Market Analyst',
    goal="""Receive the structured user profile. Use the 'Google Search Market Data' tool to fetch current job requirements and salary.
            Perform a critical skill-gap analysis by comparing the user's skills against the market requirements.
            Your final output MUST be a valid JSON object matching the MarketAnalysis schema.""",
    backstory="A data scientist focused purely on objective market data. You use external tools to validate job requirements and identify high-value skill gaps.",
    tools=[google_search_market_data],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 3.3. Strategist Agent (The Career Coach)
strategist_agent = Agent(
    role='Career Strategy Coach',
    goal="""Synthesize the Skill Gap Analysis into a structured, motivational, and actionable Career Roadmap Report.
            The report MUST include a Skill Gap Analysis Summary, a clear Action Plan, and specific, high-value resource recommendations.
            Do not output JSON; output a well-formatted Markdown report.""",
    backstory="""A seasoned career coach with access to a wide internal Knowledge Base of highly-rated courses (Simulated Memory). 
                 You bridge the gap between data and action, providing concrete steps.""",
    # Simulate Long-Term Memory (Knowledge Base) in the system prompt
    system_prompt="""You are the world's best career coach. You have access to the following top-tier resources (your Knowledge Base):
                 - SQL/Data Warehousing: 'Advanced SQL Mastery for Data Science' (Certification)
                 - Visualization: 'Tableau Desktop Specialist Training' (Course)
                 - Cloud Basics: 'AWS Certified Cloud Practitioner Basics' (Certification)
                 - Programming: 'Python Data Structures & Algorithms Refresher' (Course)
                 Use these specific names when recommending resources to the user.""",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# --- 4. Task Definitions (The Workflow) ---

# --- USER INPUT ---
# NOTE: Change these inputs to test different scenarios
USER_CURRENT_SKILLS = "Python, basic Excel, strong theoretical statistics, good communication."
USER_TARGET_ROLE = "Junior Data Analyst"
USER_EXPERIENCE = 2
# --------------------

task_profiler = Task(
    description=f"""
    Conduct an internal interview based on the following raw user data:
    - Skills: {USER_CURRENT_SKILLS}
    - Target Role: {USER_TARGET_ROLE}
    - Experience: {USER_EXPERIENCE} years.
    Your task is to structure this data into the required JSON format ({UserProfile.schema_json()}).
    """,
    agent=profiler_agent,
    output_json=UserProfile,
    expected_output="A single, valid JSON object matching the UserProfile schema."
)

task_analyst = Task(
    description="""
    Execute the following steps sequentially:
    1. Receive the structured UserProfile.
    2. Use the 'Google Search Market Data' tool, passing the 'target_role' from the input.
    3. Compare the user's skills against the market data found by the tool.
    4. Identify the 'critical_skill_gap' (the most vital missing skills).
    5. Output the result as a valid JSON object matching the MarketAnalysis schema.
    """,
    agent=market_analyst,
    output_json=MarketAnalysis,
    expected_output="A single, valid JSON object matching the MarketAnalysis schema."
)

task_strategist = Task(
    description=f"""
    Execute the following steps sequentially:
    1. Receive the MarketAnalysis JSON (Skill Gap, Salary, etc.).
    2. Reference your internal Knowledge Base (specific courses listed in your system prompt).
    3. Generate a highly detailed and motivational Career Roadmap Report in Markdown.
    
    The report MUST contain:
    - **I. Executive Summary:** A 1-paragraph verdict (e.g., INVEST, HOLD).
    - **II. Skill Gap Analysis Summary:** (Based on the Analyst's JSON).
    - **III. Action Plan (Specific Steps):** A list of 3-5 concrete steps.
    - **IV. Resource Recommendations:** Match the critical skill gaps to specific course names from your Knowledge Base (e.g., 'Advanced SQL Mastery for Data Science').
    """,
    agent=strategist_agent,
    expected_output="A complete, well-formatted Markdown report (no JSON).",
)

# --- 5. Crew Setup and Execution ---

career_crew = Crew(
    agents=[profiler_agent, market_analyst, strategist_agent],
    tasks=[task_profiler, task_analyst, task_strategist],
    process=Process.sequential,  # Ensures clean handoffs (A2A)
    verbose=2, # High verbosity to show agent thinking and tool use
)

# Exception handling for API key issues
try:
    print("--- Starting the Autonomous Career Guidance Agent ---")
    
    # Kick off the execution
    final_result = career_crew.kickoff()
    
    print("\n" + "="*80)
    print("FINAL CAREER ROADMAP REPORT GENERATED:")
    print("="*80)
    print(final_result)
    print("="*80)

except APIError as e:
    print("\n" + "="*80)
    print("FATAL ERROR: Gemini API Key Issue.")
    print("Please ensure your GEMINI_API_KEY is correctly set in your .env file.")
    print(f"Details: {e}")
    print("="*80)
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")