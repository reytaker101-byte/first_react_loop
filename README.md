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



admin@NewLearning#git clone https://github.com/reytaker101-byte/first_react_loop.git
Cloning into 'first_react_loop'...
remote: Enumerating objects: 34, done.
remote: Counting objects: 100% (34/34), done.
remote: Compressing objects: 100% (28/28), done.
remote: Total 34 (delta 7), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (34/34), 16.67 KiB | 656.00 KiB/s, done.
Resolving deltas: 100% (7/7), done.
admin@NewLearning#ls
first_react_loop
admin@NewLearning#cd first_react_loop 
admin@NewLearning#ls
README.md               agent.py                docker-compose.yml      nginx                   requirements.txt        tools.py
admin@NewLearning#docker compose config
name: first_react_loop
services:
  orders-nginx:
    container_name: orders-nginx
    image: nginx:alpine
    networks:
      default: null
    ports:
      - mode: ingress
        target: 80
        published: "8081"
        protocol: tcp
    volumes:
      - type: bind
        source: /Users/dollyd/react/first_react_loop/nginx/orders.html
        target: /usr/share/nginx/html/index.html
        read_only: true
        bind:
          create_host_path: true
  payments-nginx:
    container_name: payments-nginx
    image: nginx:alpine
    networks:
      default: null
    ports:
      - mode: ingress
        target: 80
        published: "8082"
        protocol: tcp
    volumes:
      - type: bind
        source: /Users/dollyd/react/first_react_loop/nginx/payments.html
        target: /usr/share/nginx/html/index.html
        read_only: true
        bind:
          create_host_path: true
networks:
  default:
    name: first_react_loop_default
admin@NewLearning#docker compose up -d
[+] Running 10/10
 ✔ orders-nginx Pulled                                                                                                                                                13.3s 
   ✔ c3ee22b57f6b Pull complete                                                                                                                                        7.1s 
   ✔ 3be296cd3c97 Pull complete                                                                                                                                        3.9s 
   ✔ 5de55e5ef9c0 Pull complete                                                                                                                                        5.7s 
   ✔ 1b000889fffe Pull complete                                                                                                                                        4.5s 
   ✔ e6cb77a8803a Pull complete                                                                                                                                        6.1s 
   ✔ ed0e37fc3a99 Pull complete                                                                                                                                        3.9s 
   ✔ 7feeb37758e4 Pull complete                                                                                                                                        4.2s 
   ✔ aca9e7c5ccc1 Pull complete                                                                                                                                        6.2s 
 ✔ payments-nginx Pulled                                                                                                                                              13.5s 
[+] Running 3/3
 ✔ Network first_react_loop_default  Created                                                                                                                           0.0s 
 ✔ Container orders-nginx            Started                                                                                                                           0.6s 
 ✔ Container payments-nginx          Started                                                                                                                           0.6s 
admin@NewLearning#docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                                     NAMES
c38aaf66b518   nginx:alpine   "/docker-entrypoint.…"   4 seconds ago   Up 4 seconds   0.0.0.0:8082->80/tcp, [::]:8082->80/tcp   payments-nginx
72b0e07cb081   nginx:alpine   "/docker-entrypoint.…"   4 seconds ago   Up 4 seconds   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp   orders-nginx


<img width="522" height="238" alt="image" src="https://github.com/user-attachments/assets/01f40e94-ca76-4b2a-8a7b-b9890a80df95" />

<img width="530" height="264" alt="image" src="https://github.com/user-attachments/assets/25231697-c042-499e-88cc-9352f0e30044" />


