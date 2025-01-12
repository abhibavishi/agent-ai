import streamlit as st
from langchain_openai import AzureChatOpenAI
from browser_use import Agent, Browser
from playwright.async_api import BrowserContext
import asyncio
import os
from dotenv import load_dotenv
from agent_formatter import AgentFormatter

# Page configuration
st.set_page_config(
    page_title="Browser AI Agent",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    .agent-result {
        background-color: #000000;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    .step-log {
        background-color: #f1f3f5;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-family: monospace;
    }
    .result-container {
        display: flex;
        align-items: center;
    }
    .result-image {
        flex: 0 0 auto;
        margin-right: 1rem;
    }
    .result-text {
        flex: 1 1 auto;
    }
    </style>
    """, unsafe_allow_html=True)

def load_environment():
    """Load environment variables and validate them."""
    load_dotenv()
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}")
        st.stop()

def initialize_llm():
    """Initialize the Azure OpenAI model."""
    return AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    )

async def run_agent_task(task):
    """Execute the task using the browser agent."""
    browser = Browser()
    agent = Agent(
        task=task,
        llm=initialize_llm(),
        browser=browser
    )
    result = await agent.run()
    formatted_result = AgentFormatter.format_final_output(result)
    return formatted_result

def display_agent_history(history):
    """Display the agent's action history in a structured way."""
    if not history or not hasattr(history, 'all_results'):
        return
    
    st.markdown("### 📝 Agent Actions Log")
    for idx, result in enumerate(history.all_results, 1):
        with st.expander(f"Step {idx}"):
            st.markdown(f"```\n{result.extracted_content}\n```")
            if result.error:
                st.error(f"Error: {result.error}")

def main():
    st.title("🤖 Browser AI Agent")
    st.write("Tell me what you'd like me to help you with, and I'll navigate the web to find what you need!")

    # Load environment variables
    load_environment()

    # Example tasks
    st.markdown("### Example tasks you can try:")
    st.markdown("""
    - Find the cheapest flight from New York to London next month
    - Check the weather forecast for Paris this weekend
    - Look up the latest news about artificial intelligence
    - Find the opening hours of the Louvre museum
    - Search for laptop deals under $1000
    """)

    # Task input
    task = st.text_area(
        "What would you like me to do?",
        height=100,
        placeholder="E.g., Find a one-way flight from Ahmedabad to New York on 25 January 2025 on Google Flights"
    )

    if st.button("Run Task", type="primary"):
        if not task:
            st.warning("Please enter a task first!")
            return

        with st.spinner("Working on your task..."):
            try:
                # Create a container for real-time updates
                status_container = st.empty()
                
                # Run the agent
                result = asyncio.run(run_agent_task(task))
                
                # Display the final result
                st.success("Task completed!")
                st.markdown("""
                    <div class="result-text">
                        <h3>🎯 Result</h3>
                        {}
                    </div>
                </div>
                """.format(result), unsafe_allow_html=True)
                
                # Display detailed history if available
                if hasattr(result, 'all_results'):
                    display_agent_history(result)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.markdown("""
                    <div class="error-details">
                        <p>If you see this error, please try:</p>
                        <ul>
                            <li>Refreshing the page</li>
                            <li>Rephrasing your task</li>
                            <li>Making sure your task is specific and clear</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()