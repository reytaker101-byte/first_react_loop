import json
import os
from openai import OpenAI
from tools import check_service

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS = [{
    "type": "function",
    "function": {
        "name": "check_service",
        "description": "Investigate a microservice's Docker nginx container. Discover it by Docker labels and return status, health, HTTP reachability and recent logs.",
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Logical microservice name such as checkout or payment."
                }
            },
            "required": ["service_name"]
        }
    }
}]

SYSTEM_PROMPT = """
You are a DevOps Incident Triage Agent.

Investigate the requested microservice using the available Docker tool.
The user does NOT need to know whether nginx is down.

Rules:
1. If a service is named, call check_service.
2. Use only returned evidence.
3. If found=false, clearly say the service was not found. Do not guess.
4. Never claim a root cause unless the evidence supports it.
5. If evidence is insufficient, say the root cause is not confirmed and give next investigation steps.
6. Never restart, delete or modify containers.
7. Final format: Status -> Evidence -> Interpretation -> Next investigation steps.
"""

def run_agent(user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or "No final response returned."

        for call in message.tool_calls:
            try:
                args = json.loads(call.function.arguments)
                result = check_service(args["service_name"])
            except Exception as exc:
                result = {"found": False, "error": f"Tool execution failed: {exc}"}

            print(f"\n[TOOL] {call.function.name}")
            print(json.dumps(result, indent=2))

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": call.function.name,
                "content": json.dumps(result)
            })

    return "Agent stopped after the maximum investigation steps."

if __name__ == "__main__":
    prompt = input("Describe the DevOps issue: ").strip()
    if not prompt:
        prompt = "Investigate the checkout service and tell me what I should check."
    print("\n--- AI DEVOPS INCIDENT TRIAGE AGENT ---")
    print(run_agent(prompt))
