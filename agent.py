import os
import ssl
import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI

load_dotenv()

insecure_ctx = ssl.create_default_context()
insecure_ctx.check_hostname = False
insecure_ctx.verify_mode = ssl.CERT_NONE

# Must set base_url + headers when passing a custom client
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
    temperature=0.3,
    client=httpx_client,
)

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful research assistant.",
)

def run():
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "what is the capital of france?"}]},
        stream_mode="updates",
    ):
        for node, update in chunk.items():
            if "messages" in update:
                for msg in update["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        print(f"[{node}]: {msg.content[:200]}")

if __name__ == "__main__":
    run()
