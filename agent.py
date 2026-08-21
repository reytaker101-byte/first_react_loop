import json
import os
import sys
from openai import OpenAI

from tools import AVAILABLE_FUNCTIONS

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

TOOLS = [
    {
        "type": "function",
        "name": "list_containers",
        "description": "List all Docker containers, including running and stopped containers. Use this first when the affected container/service is not known.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "inspect_container",
        "description": "Inspect a Docker container to check whether it is running, exited, restarting, unhealthy, its exit code, restart count, and timestamps.",
        "parameters": {
            "type": "object",
            "properties": {
                "container_name": {"type": "string", "description": "Exact Docker container name."}
            },
            "required": ["container_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_container_logs",
        "description": "Read recent Docker logs from a named container. Use this as evidence when investigating a failure.",
        "parameters": {
            "type": "object",
            "properties": {
                "container_name": {"type": "string", "description": "Exact Docker container name."},
                "tail": {"type": "integer", "description": "Number of recent log lines to read."}
            },
            "required": ["container_name", "tail"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

SYSTEM_PROMPT = """
You are a DevOps Incident Triage Agent.

Your job is to investigate Docker incidents using ONLY evidence returned by the tools.
You must not invent container names, statuses, errors, log messages, or root causes.

Use a ReAct-style loop:
1. Reason about what evidence is missing.
2. Select an appropriate read-only Docker tool.
3. Observe the returned evidence.
4. Repeat if more evidence is required.
5. Give a concise final incident summary.

Investigation rules:
- If the affected service/container is unknown, call list_containers first.
- Inspect the suspected container before claiming it is down/unhealthy.
- Read logs when useful to identify a failure reason.
- If a container or data is not found, explicitly say "Not found" and do not guess.
- Separate FACTS (tool evidence) from INFERENCE (your interpretation).
- Give safe troubleshooting steps. Do not restart, delete, or modify containers.
- Final response should contain:
  Incident
  Evidence
  Likely cause
  Recommended next steps
"""


def run_agent(user_prompt: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Export it before running the agent.")

    client = OpenAI(api_key=api_key)
    conversation = [{"role": "user", "content": user_prompt}]

    print("\n=== DEVOPS INCIDENT TRIAGE AGENT ===")
    print(f"Model: {MODEL}")
    print(f"Incident: {user_prompt}\n")

    for step in range(1, 7):
        print(f"[Agent Step {step}] Thinking / selecting evidence...")

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=conversation,
            tools=TOOLS,
        )

        # Preserve the model's tool-call/message items for the next turn.
        conversation.extend(response.output)

        function_calls = [item for item in response.output if item.type == "function_call"]

        if not function_calls:
            print("\n=== FINAL INVESTIGATION ===")
            print(response.output_text)
            return response.output_text

        for call in function_calls:
            print(f"[Tool Action] {call.name}({call.arguments})")
            try:
                args = json.loads(call.arguments)
                function_to_call = AVAILABLE_FUNCTIONS.get(call.name)
                if not function_to_call:
                    result = json.dumps({"error": f"Unknown tool: {call.name}"})
                else:
                    result = function_to_call(**args)
            except Exception as exc:
                result = json.dumps({"error": "Tool execution failed", "details": str(exc)})

            print(f"[Observation] {result[:1000]}")
            if len(result) > 1000:
                print("[Observation] ...truncated on screen; full result was sent to the model.")

            conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                }
            )

    raise RuntimeError("Agent stopped after 6 investigation steps. Try a narrower incident prompt.")


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        prompt = "Investigate why the orders API is unavailable. Find the affected Docker container, collect evidence, and recommend troubleshooting steps."
    run_agent(prompt)
