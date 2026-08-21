======================================================================
        AI DEVOPS INCIDENT TRIAGE AGENT
        OpenAI Function Calling + ReAct + Docker
======================================================================

1. PROJECT PURPOSE
==================

This project demonstrates a simple AI-powered DevOps/SRE Incident
Triage Agent.

The purpose is NOT to automatically fix the incident.

The purpose is to:

    1. Receive a service incident from a user.
    2. Identify the affected Docker container.
    3. Collect real Docker evidence.
    4. Inspect the container state.
    5. Read recent container logs.
    6. Let the LLM analyze the evidence.
    7. Provide an evidence-based incident summary.
    8. Recommend safe next troubleshooting steps.

IMPORTANT:

The agent investigates only.

It does NOT:

    - restart containers
    - delete containers
    - modify containers
    - invent a root cause
    - guess when information is missing

This makes the project a DevOps/SRE INCIDENT TRIAGE AGENT.


======================================================================
2. REAL-WORLD USE CASE
======================================================================

Imagine a microservices environment.

There can be multiple services:

    orders service
    payments service
    checkout service
    etc.

Each service may have one or more infrastructure containers.

For this demo we have:

    orders-nginx
    payments-nginx

Suppose a user reports:

    "Investigate why the orders API is unavailable."

The user does NOT need to know:

    - Docker container name
    - Container ID
    - Exit code
    - Docker commands
    - Log commands

The AI agent performs the initial investigation.

Simple idea:

    USER
      |
      | "Orders API is unavailable"
      v
    LLM
      |
      | Selects appropriate tool
      v
    DOCKER
      |
      +--> Find containers
      +--> Inspect orders-nginx
      +--> Read logs
      |
      v
    Evidence
      |
      v
    LLM analyzes evidence
      |
      v
    Incident Summary + Next Steps


======================================================================
3. WHAT DOES "TRIAGE" MEAN?
======================================================================

Incident Triage means:

    "Initial investigation to understand what is wrong."

It does NOT necessarily mean fixing the problem.

Example:

    Problem:
    Orders API is unavailable.

Triage asks:

    Is the container running?
    Did the container exit?
    What is the exit code?
    Is there a health check?
    What do the logs say?
    Is there enough evidence to identify the cause?

Then the agent reports what it found.


======================================================================
4. WHAT IS THE AI ACTUALLY DOING?
======================================================================

The LLM itself cannot directly run Docker commands.

The LLM is the decision-making layer.

Python provides tools/functions that can execute Docker commands.

Therefore:

    LLM
      |
      | decides which tool is needed
      v
    Python Function
      |
      | executes Docker command
      v
    Docker
      |
      | returns real evidence
      v
    Python
      |
      | sends evidence back
      v
    LLM
      |
      v
    Final investigation


======================================================================
5. IMPORTANT TERMINOLOGIES
======================================================================

LLM
---
Large Language Model.

In this project, the LLM analyzes the incident and decides which
investigation tool should be used.

API
---
A way for one software system to communicate with another system.

Here:

    Python Agent -> OpenAI API -> LLM

Function Calling
----------------
A mechanism where the LLM can request that our Python program execute
a specific function.

Example:

    LLM says:
    "I need information about Docker containers."

    It selects:

    list_containers()

Python executes the function and returns the result.

ReAct
-----
ReAct means:

    Reason
      ->
    Act
      ->
    Observe
      ->
    Reason again
      ->
    Act
      ->
    Observe
      ->
    Final Answer

In simple words:

    Think what evidence is needed
          ->
    use a tool
          ->
    see the result
          ->
    decide what to check next

Tool
----
A Python function that the LLM is allowed to call.

This project has three tools:

    list_containers()
    inspect_container()
    get_container_logs()

Observation
-----------
The real output returned by a tool.

Example:

    orders-nginx
    status = exited
    running = false
    exit_code = 0

Evidence
--------
Information actually returned by Docker.

The agent must use evidence instead of guessing.


======================================================================
6. PROJECT ARCHITECTURE
======================================================================

    User
      |
      | Incident
      v
    agent.py
      |
      v
    OpenAI LLM
      |
      | Function Call
      v
    tools.py
      |
      +----------------------+
      |                      |
      v                      v
    Docker CLI          Docker Containers
      |                      |
      +----------+-----------+
                 |
                 v
              Evidence
                 |
                 v
              agent.py
                 |
                 v
              OpenAI LLM
                 |
                 v
        Final Investigation


Main files:

    agent.py
        -> Agent logic
        -> ReAct loop
        -> OpenAI API call
        -> Tool selection
        -> Final investigation response

    tools.py
        -> Actual Docker functions
        -> list_containers()
        -> inspect_container()
        -> get_container_logs()

    docker-compose.yml
        -> Creates the demo Docker environment

    nginx/
        -> Simple HTML files served by Nginx

    requirements.txt
        -> Python dependencies

    README.md
        -> Project documentation


======================================================================
7. STEP 1 - CLONE THE PROJECT
======================================================================

Command:

    git clone https://github.com/reytaker101-byte/first_react_loop.git

Output:

    Cloning into 'first_react_loop'...
    remote: Enumerating objects: 34, done.
    remote: Counting objects: 100% (34/34), done.
    remote: Compressing objects: 100% (28/28), done.
    remote: Total 34 (delta 7), reused 0 (delta 0), pack-reused 0
    Receiving objects: 100% (34/34), 16.67 KiB | 656.00 KiB/s, done.
    Resolving deltas: 100% (7/7), done.


Go inside project:

    cd first_react_loop

Check files:

    ls

Output:

    README.md
    agent.py
    docker-compose.yml
    nginx
    requirements.txt
    tools.py


======================================================================
8. STEP 2 - CHECK DOCKER COMPOSE CONFIGURATION
======================================================================

Command:

    docker compose config

Purpose:

This validates and displays the Docker Compose configuration.

Our demo creates two Nginx containers:

    orders-nginx
        localhost:8081 -> container port 80

    payments-nginx
        localhost:8082 -> container port 80

Important output:

    orders-nginx:
        container_name: orders-nginx
        image: nginx:alpine
        published: "8081"
        target: 80

    payments-nginx:
        container_name: payments-nginx
        image: nginx:alpine
        published: "8082"
        target: 80


Simple explanation:

    Browser/curl
         |
         v
    localhost:8081
         |
         v
    orders-nginx
         |
         v
    Nginx port 80


======================================================================
9. STEP 3 - START THE DEMO ENVIRONMENT
======================================================================

Command:

    docker compose up -d

Output:

    Network first_react_loop_default Created
    Container orders-nginx Started
    Container payments-nginx Started


Check running containers:

    docker ps

Actual output:

    CONTAINER ID   IMAGE          COMMAND                  CREATED
    STATUS         PORTS                                     NAMES

    c38aaf66b518   nginx:alpine   "/docker-entrypoint.…"
    Up 4 seconds   0.0.0.0:8082->80/tcp, [::]:8082->80/tcp
    payments-nginx

    72b0e07cb081   nginx:alpine   "/docker-entrypoint.…"
    Up 4 seconds   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
    orders-nginx


Meaning:

    orders-nginx       = RUNNING
    payments-nginx     = RUNNING


======================================================================
10. STEP 4 - CREATE THE INCIDENT
======================================================================

We intentionally stop the orders container.

Command:

    docker stop orders-nginx

Output:

    orders-nginx


Now check all containers:

    docker ps -a

Actual important output:

    payments-nginx
        Up 5 minutes

    orders-nginx
        Exited (0) 5 seconds ago

Meaning:

    orders-nginx is no longer running.

This creates our artificial DevOps incident.

We are intentionally creating the failure so that the AI agent can
investigate it.


======================================================================
11. STEP 5 - VERIFY THE INCIDENT MANUALLY
======================================================================

Command:

    docker inspect orders-nginx \
      --format '{{.State.Status}} | ExitCode={{.State.ExitCode}}'

Actual output:

    exited | ExitCode=0


Meaning:

    State:
        exited

    Running:
        No

    Exit code:
        0


IMPORTANT:

Exit code 0 normally means the process/container terminated
successfully.

Therefore we should NOT immediately claim:

    "Nginx crashed."

The evidence does not prove that.

The correct statement is:

    "The container is stopped/exited and the available evidence
     does not show why it was stopped."


======================================================================
12. STEP 6 - INSTALL OPENAI PYTHON SDK
======================================================================

First we checked whether OpenAI SDK was installed.

Command:

    python3 -c "import openai; print(openai.__version__)"

Output:

    ModuleNotFoundError: No module named 'openai'


Meaning:

    OpenAI Python SDK was not installed.


Install dependencies:

    pip3 install -r requirements.txt

Important output:

    Downloading openai-3.3.1-py3-none-any.whl
    ...
    Successfully installed ...
    openai-3.3.1


Verify again:

    python3 -c "import openai; print('OpenAI SDK:', openai.__version__)"

Output:

    OpenAI SDK: 3.3.1


Meaning:

    OpenAI Python SDK is now installed successfully.


======================================================================
13. STEP 7 - CONFIGURE OPENAI API KEY
======================================================================

Command:

    export OPENAI_API_KEY="OpenAI API Key"

Verify that the variable exists:

    python3 -c "import os; print('API key configured:',
    bool(os.getenv('OPENAI_API_KEY')))"

Actual output:

    API key configured: True


IMPORTANT:

The API key itself should NEVER be printed or committed to GitHub.

Only verify:

    True / False


======================================================================
14. STEP 8 - SELECT THE MODEL
======================================================================

Command:

    export OPENAI_MODEL="gpt-5.6-luna"

Verify:

    echo $OPENAI_MODEL

Output:

    gpt-5.6-luna


Meaning:

The agent will send its requests to the configured OpenAI model.


======================================================================
15. STEP 9 - RUN THE AI DEVOPS AGENT
======================================================================

Command:

    python3 agent.py

Default incident:

    Investigate why the orders API is unavailable.
    Find the affected Docker container,
    collect evidence,
    and recommend troubleshooting steps.


The agent starts:

    === DEVOPS INCIDENT TRIAGE AGENT ===
    Model: gpt-5.6-luna

    Incident:
    Investigate why the orders API is unavailable.
    Find the affected Docker container,
    collect evidence,
    and recommend troubleshooting steps.


======================================================================
16. REACT STEP 1 - REASON + ACTION
======================================================================

Output:

    [Agent Step 1] Thinking / selecting evidence...

The LLM decides:

    "I don't yet know which container is affected."

So it calls:

    [Tool Action] list_containers({})


Tool purpose:

    Find all Docker containers and their current status.


Tool result:

    {
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
        }
      ]
    }


Observation:

    orders-nginx = Exited

Now the LLM has real evidence.


======================================================================
17. REACT STEP 2 - INSPECT THE CONTAINER
======================================================================

Output:

    [Agent Step 2] Thinking / selecting evidence...

The LLM decides:

    "I found the affected container.
     Now I need more details."

Tool call:

    inspect_container({
        "container_name": "orders-nginx"
    })


Tool output:

    {
      "status": "FOUND",
      "container": "orders-nginx",
      "image": "nginx:alpine",
      "state": "exited",
      "running": false,
      "exit_code": 0,
      "restart_count": 0,
      "health": "not_configured"
    }


Important evidence:

    state:
        exited

    running:
        false

    exit_code:
        0

    restart_count:
        0

    health:
        not_configured


Observation:

    Container is definitely not running.


======================================================================
18. REACT STEP 3 - CHECK LOGS
======================================================================

The LLM decides that more evidence is required.

Tool call:

    get_container_logs({
        "container_name": "orders-nginx",
        "tail": 100
    })


Important log evidence:

    Configuration complete; ready for start up

And:

    "GET / HTTP/1.1" 200


Meaning:

    Nginx successfully started.

    HTTP request returned 200.

Therefore:

    The logs do NOT show an obvious startup failure.


======================================================================
19. REACT STEP 4 - FINAL REASONING
======================================================================

After collecting enough evidence, the agent stops calling tools.

It produces the final investigation.


======================================================================
20. ACTUAL FINAL INVESTIGATION OUTPUT
======================================================================

=== FINAL INVESTIGATION ===

Incident

The orders API is unavailable because its Docker container,
orders-nginx, is not running.


Evidence

- Container orders-nginx was found.
- Image: nginx:alpine
- State: exited
- Running: false
- Exit code: 0
- Restart count: 0
- Health: not_configured
- Container finished at:
  2026-08-21T07:27:57Z

Logs show:

    Configuration complete; ready for start up

And:

    GET / HTTP/1.1 200


Likely cause

The container terminated cleanly rather than crashing.

Evidence:

    exit_code = 0
    restart_count = 0

The available Docker evidence does NOT contain the exact reason
why the container stopped.


Recommended next steps

1. Check deployment or Compose configuration for something that
   stops orders-nginx.

2. Verify container port publishing and upstream routing.

3. Review deployment/orchestrator events around the termination time.

4. Confirm that Nginx is configured to proxy to the intended
   orders API backend.

5. Consider adding a health check and restart policy after validating
   the configuration.

6. Capture the current configuration before making any changes.


======================================================================
21. WHY THIS IS A GOOD AI DEVOPS USE CASE
======================================================================

Traditional approach:

    User reports problem
          |
          v
    DevOps Engineer
          |
          +--> docker ps
          +--> docker ps -a
          +--> docker inspect
          +--> docker logs
          +--> analyze evidence
          |
          v
    Diagnosis


Our approach:

    User reports problem
          |
          v
    AI DevOps Agent
          |
          +--> selects Docker tool
          +--> gets evidence
          +--> observes result
          +--> selects next tool
          +--> analyzes evidence
          |
          v
    Investigation summary


The AI is reducing the amount of manual initial investigation.


======================================================================
22. WHAT THE AGENT DOES NOT DO
======================================================================

The agent is READ-ONLY.

It can investigate:

    YES:
        docker ps
        docker inspect
        docker logs

It does NOT perform:

    NO:
        docker start
        docker restart
        docker stop
        docker rm
        configuration changes
        application changes


Why?

Because automatic remediation can be dangerous in a real production
environment.

For this learning project we intentionally keep the agent safe.


======================================================================
23. IMPORTANT: NO GUESSING
======================================================================

Suppose the user says:

    "Investigate orders service."

If the service/container does not exist, the agent should NOT say:

    "The orders container is down."

Instead:

    "The orders service/container was not found in the available
     Docker evidence."


This is important because LLMs can hallucinate.

Our system prompt explicitly says:

    "You must not invent container names, statuses, errors,
     log messages, or root causes."


Therefore:

    Evidence first
    Guessing never


======================================================================
24. THE COMPLETE REACT LOOP
======================================================================

    USER REPORT
         |
         v
    REASON
         |
         v
    ACTION -> list_containers()
         |
         v
    OBSERVE
         |
         v
    REASON
         |
         v
    ACTION -> inspect_container()
         |
         v
    OBSERVE
         |
         v
    REASON
         |
         v
    ACTION -> get_container_logs()
         |
         v
    OBSERVE
         |
         v
    FINAL ANSWER


Simple memory:

    REASON
       ->
    TOOL
       ->
    OBSERVE
       ->
    REASON
       ->
    TOOL
       ->
    OBSERVE
       ->
    ANSWER


======================================================================
25. HOW FUNCTION CALLING FITS HERE
======================================================================

LLM cannot directly execute:

    docker ps
    docker inspect
    docker logs

Instead, we expose Python functions as tools.

Available tools:

    list_containers()
        |
        +--> runs docker ps -a

    inspect_container(container_name)
        |
        +--> runs docker inspect

    get_container_logs(container_name, tail)
        |
        +--> runs docker logs


So:

    LLM
      |
      | "I need container information"
      v
    list_containers()
      |
      v
    Docker
      |
      v
    Evidence
      |
      v
    LLM


This is the bridge between:

    AI reasoning

and

    real DevOps actions/data.


======================================================================
26. ONE-LINE EXPLANATION OF EACH FILE
======================================================================

agent.py

    Brain/orchestrator of the project.

    It:
        - talks to OpenAI
        - provides tool definitions
        - runs the ReAct loop
        - sends observations back to the LLM
        - prints the final investigation


tools.py

    Hands/tools of the agent.

    It:
        - executes Docker commands
        - collects Docker evidence
        - converts results into structured JSON


docker-compose.yml

    Creates our local demo environment.

    It creates:

        orders-nginx
        payments-nginx


nginx/

    Contains simple HTML pages used by the Nginx containers.


requirements.txt

    Lists Python dependencies.


README.md

    Explains the project and how to run it.


======================================================================
27. MOST IMPORTANT DIFFERENCE
======================================================================

LLM alone:

    User
      |
      v
    LLM
      |
      v
    Text response


LLM + Function Calling:

    User
      |
      v
    LLM
      |
      | Tool request
      v
    Python function
      |
      v
    Docker
      |
      v
    Real evidence
      |
      v
    LLM
      |
      v
    Evidence-based answer


This is what makes the project move beyond a simple chatbot.


======================================================================
28. WHAT TO SAY IN THE INTERVIEW / SESSION
======================================================================

Short explanation:

"I built a minimal AI-powered DevOps Incident Triage Agent using
OpenAI Function Calling and a ReAct-style loop.

For the demo, I have multiple Docker-based Nginx services such as
orders-nginx and payments-nginx.

If someone reports that the orders API is unavailable, the user does
not need to know the Docker container name or run Docker commands.

The agent first discovers the containers, identifies that
orders-nginx is exited, inspects its state and exit code, and then
reads its recent logs.

The LLM analyzes the actual Docker evidence and provides an incident
summary and recommended next investigation steps.

The agent is read-only, so it does not restart or modify containers,
and it does not claim a root cause when the evidence is insufficient."


======================================================================
29. 30-SECOND VERSION
======================================================================

"My project is an AI DevOps Incident Triage Agent.

A user reports a service problem in natural language.

The LLM uses Function Calling to select Python tools that query Docker.
The agent follows a ReAct loop: Reason, Act, Observe, and repeat.

It checks the affected container, its state, exit code and logs, then
returns an evidence-based investigation.

For example, when orders-nginx was stopped, the agent discovered that
the container was exited with code 0 and that Nginx had previously
started successfully. Instead of guessing why it stopped, the agent
clearly stated that the exact cause was not available in the evidence
and recommended the next troubleshooting steps."


======================================================================
30. RESUME BULLET
======================================================================

Built a ReAct-based AI DevOps Incident Triage Agent using OpenAI
Function Calling and Docker to investigate microservice incidents,
collect container state and log evidence, and generate
evidence-based troubleshooting recommendations with explicit
no-guessing and read-only safety controls.


======================================================================
31. FINAL PROJECT FLOW - REMEMBER THIS
======================================================================

    USER
      |
      | "Orders API is unavailable"
      v
    OPENAI LLM
      |
      | Function Call
      v
    list_containers()
      |
      v
    orders-nginx = Exited
      |
      v
    inspect_container()
      |
      v
    running = false
    exit_code = 0
      |
      v
    get_container_logs()
      |
      v
    Nginx started successfully
      |
      v
    LLM ANALYSIS
      |
      v
    FINAL INVESTIGATION
      |
      +--> What happened?
      +--> What evidence exists?
      +--> What is likely?
      +--> What is NOT known?
      +--> What should DevOps check next?


FINAL MEMORY LINE:

    "LLM decides WHAT to investigate.
     Python tools collect REAL evidence.
     Docker provides the evidence.
     LLM analyzes the evidence.
     Agent recommends the next steps.

     It investigates.
     It does not blindly guess or automatically fix."


======================================================================
