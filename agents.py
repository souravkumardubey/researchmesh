import os
import ssl
import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, web_scrape

load_dotenv()

insecure_ctx = ssl.create_default_context()
insecure_ctx.check_hostname = False
insecure_ctx.verify_mode = ssl.CERT_NONE

api_key = os.getenv("MISTRAL_API_KEY")
httpx_client = httpx.Client(
    base_url="https://api.mistral.ai/v1",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    },
    verify=insecure_ctx,
    timeout=120,
)

llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=api_key,
    client=httpx_client,
)

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt= "You are a web search specialist. Your task is to search the web for information relevant to the user's query. Return the search results with titles, URLs, and key snippets.",
        name="search_agent",
    )

def build_read_agent():
    return create_agent(
        model=llm,
        tools=[web_scrape],
        system_prompt=
            "You are a content extraction specialist. Given a list of URLs, scrape each page and extract the main content. Summarize the key information found on each page.",
        name="read_agent",
    )   

# writer chains
write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a expert research writer. Your task is to write a comprehensive research report based on the information provided by the search and read agents. Use the following format for your report:\n\n"),
        ("human", """"
            Write a detailed research report based on the following information:
            Topic: {topic}
            Research gathered: {research}
        Structure the report as:
            1. Introduction: Provide an overview of the topic and its significance.
            2. Key finding (minimum 3 well explained points)
            3. Conclusion: Summarize the key insights and implications of the research.
            4. Sources: List the URLs of the sources used in the research.
         
        Be detailed, factual and professional in your writing. Ensure that the report is well-organized and clearly presents the information gathered from the search and read agents.
         """),
    ]
)

writer_chain = write_prompt | llm | StrOutputParser()

# critic chain
critic_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a critical research analyst. Your task is to evaluate the quality and reliability of the research report written by the writer agent. Assess the report based on the following criteria:\n\n"),
        ("human", """
            Report: {report} 
            1. Accuracy: Are the facts presented in the report correct and supported by credible sources?
            2. Depth: Does the report provide a comprehensive analysis of the topic, covering multiple perspectives and key findings?
            3. Clarity: Is the report well-organized and easy to understand? Are complex ideas explained clearly?
            4. Sources: Are the sources cited in the report reliable and relevant to the topic?

        Provide a detailed critique of the report, highlighting its strengths and weaknesses based on these criteria. Offer constructive feedback on how the report could be improved in terms of content, structure, and sourcing.
         """),
    ]
)

critic_chain = critic_prompt | llm | StrOutputParser()