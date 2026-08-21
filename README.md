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


admin@NewLearning#docker stop orders-nginx
orders-nginx
admin@NewLearning#docker ps -a            
CONTAINER ID   IMAGE                           COMMAND                  CREATED         STATUS                      PORTS                                     NAMES
c38aaf66b518   nginx:alpine                    "/docker-entrypoint.…"   5 minutes ago   Up 5 minutes                0.0.0.0:8082->80/tcp, [::]:8082->80/tcp   payments-nginx
72b0e07cb081   nginx:alpine                    "/docker-entrypoint.…"   5 minutes ago   Exited (0) 5 seconds ago  orders-nginx
8ccc835c9400   moby/buildkit:buildx-stable-1   "/usr/bin/buildkitd-…"   4 months ago    Exited (137) 4 months ago                                             buildx_buildkit_serene_euler0
admin@NewLearning#docker inspect orders-nginx --format '{{.State.Status}} | ExitCode={{.State.ExitCode}}'
exited | ExitCode=0

admin@NewLearning#python3 -c "import openai; print(openai.__version__)"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import openai; print(openai.__version__)
    ^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'openai'
admin@NewLearning#pip3 install -r requirements.txt
Collecting openai>=1.0.0 (from -r requirements.txt (line 1))
  Downloading openai-3.3.1-py3-none-any.whl.metadata (41 kB)
Collecting anyio<5,>=4.10.0 (from openai>=1.0.0->-r requirements.txt (line 1))
  Downloading anyio-4.14.2-py3-none-any.whl.metadata (4.6 kB)
Collecting httpx2<3,>=2.7.0 (from openai>=1.0.0->-r requirements.txt (line 1))
  Downloading httpx2-2.12.0-py3-none-any.whl.metadata (9.5 kB)
Collecting jiter<1,>=0.16.0 (from openai>=1.0.0->-r requirements.txt (line 1))
  Downloading jiter-0.16.0-cp314-cp314-macosx_11_0_arm64.whl.metadata (5.2 kB)
Collecting pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13 (from openai>=1.0.0->-r requirements.txt (line 1))
  Downloading pydantic-2.13.4-py3-none-any.whl.metadata (109 kB)
Collecting sniffio (from openai>=1.0.0->-r requirements.txt (line 1))
  Downloading sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting typing-extensions<5,>=4.14 (from openai>=1.0.0->-r requirements.txt (line 1))
  Downloading typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting idna>=2.8 (from anyio<5,>=4.10.0->openai>=1.0.0->-r requirements.txt (line 1))
  Downloading idna-3.19-py3-none-any.whl.metadata (9.2 kB)
Collecting httpcore2==2.12.0 (from httpx2<3,>=2.7.0->openai>=1.0.0->-r requirements.txt (line 1))
  Downloading httpcore2-2.12.0-py3-none-any.whl.metadata (25 kB)
Collecting truststore>=0.10 (from httpx2<3,>=2.7.0->openai>=1.0.0->-r requirements.txt (line 1))
  Downloading truststore-0.10.4-py3-none-any.whl.metadata (4.4 kB)
Collecting h11>=0.16 (from httpcore2==2.12.0->httpx2<3,>=2.7.0->openai>=1.0.0->-r requirements.txt (line 1))
  Downloading h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting annotated-types>=0.6.0 (from pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13->openai>=1.0.0->-r requirements.txt (line 1))
  Downloading annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.46.4 (from pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13->openai>=1.0.0->-r requirements.txt (line 1))
  Downloading pydantic_core-2.46.4-cp314-cp314-macosx_11_0_arm64.whl.metadata (6.6 kB)
Collecting typing-inspection>=0.4.2 (from pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13->openai>=1.0.0->-r requirements.txt (line 1))
  Downloading typing_inspection-0.4.4-py3-none-any.whl.metadata (2.6 kB)
Downloading openai-3.3.1-py3-none-any.whl (1.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.7/1.7 MB 2.0 MB/s  0:00:00
Downloading anyio-4.14.2-py3-none-any.whl (125 kB)
Downloading httpx2-2.12.0-py3-none-any.whl (95 kB)
Downloading httpcore2-2.12.0-py3-none-any.whl (83 kB)
Downloading jiter-0.16.0-cp314-cp314-macosx_11_0_arm64.whl (308 kB)
Downloading pydantic-2.13.4-py3-none-any.whl (472 kB)
Downloading pydantic_core-2.46.4-cp314-cp314-macosx_11_0_arm64.whl (2.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 891.1 kB/s  0:00:02
Downloading typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Downloading annotated_types-0.8.0-py3-none-any.whl (13 kB)
Downloading h11-0.16.0-py3-none-any.whl (37 kB)
Downloading idna-3.19-py3-none-any.whl (68 kB)
Downloading truststore-0.10.4-py3-none-any.whl (18 kB)
Downloading typing_inspection-0.4.4-py3-none-any.whl (14 kB)
Downloading sniffio-1.3.1-py3-none-any.whl (10 kB)
Installing collected packages: typing-extensions, truststore, sniffio, jiter, idna, h11, annotated-types, typing-inspection, pydantic-core, httpcore2, anyio, pydantic, httpx2, openai
Successfully installed annotated-types-0.8.0 anyio-4.14.2 h11-0.16.0 httpcore2-2.12.0 httpx2-2.12.0 idna-3.19 jiter-0.16.0 openai-3.3.1 pydantic-2.13.4 pydantic-core-2.46.4 sniffio-1.3.1 truststore-0.10.4 typing-extensions-4.16.0 typing-inspection-0.4.4

[notice] A new release of pip is available: 25.2 -> 26.2.1
[notice] To update, run: pip3 install --upgrade pip
admin@NewLearning#

admin@NewLearning#python3 -c "import openai; print('OpenAI SDK:', openai.__version__)"
OpenAI SDK: 3.3.1
admin@NewLearning#export OPENAI_API_KEY="OpenAI API Key"
admin@NewLearning#python3 -c "import os; print('API key configured:', bool(os.getenv('OPENAI_API_KEY')))"
API key configured: True
admin@NewLearning#

admin@NewLearning#export OPENAI_MODEL="gpt-5.6-luna"
admin@NewLearning#echo $OPENAI_MODEL
gpt-5.6-luna
admin@NewLearning#python3 agent.py

=== DEVOPS INCIDENT TRIAGE AGENT ===
Model: gpt-5.6-luna
Incident: Investigate why the orders API is unavailable. Find the affected Docker container, collect evidence, and recommend troubleshooting steps.

[Agent Step 1] Thinking / selecting evidence...
[Tool Action] list_containers({})
[Observation] {
  "containers": [
    {
      "name": "payments-nginx",
      "status": "Up 24 minutes",
      "image": "nginx:alpine"
    },
    {
      "name": "orders-nginx",
      "status": "Exited (0) 19 minutes ago",
      "image": "nginx:alpine"
    },
    {
      "name": "buildx_buildkit_serene_euler0",
      "status": "Exited (137) 4 months ago",
      "image": "moby/buildkit:buildx-stable-1"
    }
  ]
}
[Agent Step 2] Thinking / selecting evidence...
[Tool Action] inspect_container({"container_name":"orders-nginx"})
[Observation] {
  "status": "FOUND",
  "container": "orders-nginx",
  "image": "nginx:alpine",
  "state": "exited",
  "running": false,
  "exit_code": 0,
  "restart_count": 0,
  "health": "not_configured",
  "started_at": "2026-08-21T07:23:02.586953094Z",
  "finished_at": "2026-08-21T07:27:57.211375466Z"
}
[Agent Step 3] Thinking / selecting evidence...
[Tool Action] get_container_logs({"container_name":"orders-nginx","tail":100})
[Observation] {
  "status": "OK",
  "container": "orders-nginx",
  "tail": 100,
  "logs": "/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration\n/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh\n10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf\n10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf\n/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh\n/docker-entrypoint.sh: Configuration complete; ready for start up\n192.168.65.1 - - [21/Aug/2026:07:23:21 +0000] \"GET / HTTP/1.1\" 200 27 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like
[Observation] ...truncated on screen; full result was sent to the model.
[Agent Step 4] Thinking / selecting evidence...

=== FINAL INVESTIGATION ===
## Incident

The orders API is unavailable because its Docker container, `orders-nginx`, is not running.

## Evidence

**Facts from Docker:**

- A container named `orders-nginx` was found.
- Image: `nginx:alpine`
- State: `exited`
- Running: `false`
- Exit code: `0`
- Restart count: `0`
- Health: `not_configured`
- It finished at `2026-08-21T07:27:57Z`.
- Logs show successful Nginx initialization and:
  - `Configuration complete; ready for start up`
  - A successful `GET /` request with HTTP `200`
  - A `GET /favicon.ico` request returning HTTP `404`

## Likely cause

The container terminated cleanly rather than crashing: exit code `0`, no restart attempts, and no failure messages in the available logs. The exact reason for termination is not present in the Docker evidence. The container also has no configured health check, so Docker cannot independently report application health.

## Recommended next steps

1. Check the deployment or compose/orchestrator configuration for a command, lifecycle setting, or scheduled action that stops `orders-nginx`.
2. Verify the container’s port publishing and upstream routing configuration.
3. Review host, orchestrator, or deployment events around `2026-08-21T07:27:57Z`.
4. Confirm that the Nginx configuration proxies to the intended orders API backend.
5. Add an appropriate health check and restart policy after validating the configuration.
6. Before any restart, capture the current container configuration and deployment state for comparison.
admin@NewLearning#
