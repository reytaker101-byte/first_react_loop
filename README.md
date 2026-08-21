# AI DevOps Incident Triage Agent

A minimal ReAct-style AI agent that investigates Docker-based microservices
using OpenAI Function Calling.

## Use case

In a microservices environment there can be multiple nginx containers:

- checkout-nginx
- payment-nginx
- orders-nginx

The user does NOT need to say "nginx is down". The user can simply say:

> Investigate the checkout service.

The agent uses the service name to discover the matching nginx container,
collects real Docker evidence, observes the result, and recommends the
next investigation steps.

## What it demonstrates

User
 |
 | "Investigate checkout service"
 v
LLM
 |
 | Tool call
 v
check_service("checkout")
 |
 v
Docker
 |
 +--> checkout-nginx
 |
 +--> Is it running?
 +--> Health status?
 +--> HTTP responding?
 +--> Recent logs?
 |
 v
Evidence
 |
 v
LLM
 |
 v
Investigation result



REASON
  ↓
ACT → Tool
  ↓
OBSERVE
  ↓
REASON
  ↓
ACT → Another Tool
  ↓
OBSERVE
  ↓
FINAL ANSWER

## Architecture

User -> OpenAI LLM -> check_service() -> Docker Desktop
     -> container evidence -> LLM observation -> investigation steps

## Why labels?

The logical service is `checkout`, while the infrastructure container may be
named `checkout-nginx`. The tool searches for:

`devops.service=checkout`
`devops.role=nginx`

This avoids asking the user for an infrastructure container name.

## Setup on Mac

Start Docker Desktop first.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_KEY="your_api_key"
export OPENAI_MODEL="gpt-4.1-mini"

docker compose up -d
docker ps
```

Run:

```bash
python agent.py
```

Ask:

```text
Investigate the checkout service.
```

## Test 1: Healthy

```bash
docker start checkout-nginx
python agent.py
```

The tool should find the checkout nginx container and report its state,
health and HTTP check.

## Test 2: Incident

```bash
docker stop checkout-nginx
python agent.py
```

Ask:

```text
Investigate the checkout service.
```

The agent should discover that the container is stopped and recommend
evidence-based next checks. It should not invent a root cause.

## Test 3: Missing service

Ask:

```text
Investigate the orders service.
```

There is no orders container in this demo. The tool returns `found=false`
and the agent should clearly say that the service was not found.

## Useful commands

```bash
docker ps
docker ps -a
docker logs checkout-nginx --tail 30
docker inspect checkout-nginx
docker stop checkout-nginx
docker start checkout-nginx
docker compose down
```

## ReAct flow

```text
REASON
  |
  v
ACTION -> check_service("checkout")
  |
  v
OBSERVATION -> status + health + HTTP + logs
  |
  v
REASON
  |
  v
FINAL RESPONSE
```

## Resume bullet

> Built a ReAct-based AI DevOps Incident Triage Agent using OpenAI Function
> Calling and Docker to investigate microservice health, container status,
> HTTP reachability and logs, with explicit missing-service handling.

## Safety / scope

This is a learning/demo project. It investigates only; it does not restart,
delete, or modify containers and does not claim a root cause without evidence.




<img width="522" height="238" alt="image" src="https://github.com/user-attachments/assets/01f40e94-ca76-4b2a-8a7b-b9890a80df95" />

<img width="530" height="264" alt="image" src="https://github.com/user-attachments/assets/25231697-c042-499e-88cc-9352f0e30044" />


