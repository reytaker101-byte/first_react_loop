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

- ReAct loop: Reason -> Tool Action -> Observation -> Repeat
- OpenAI Function Calling
- Tool schema
- Docker inspection from Python
- Service-to-container discovery using Docker labels
- Container status and health
- HTTP reachability
- Recent logs
- Missing-service handling without guessing

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
