# first_react_loop
DevOps Incident Triage ReAct Agent - AI agent which will do health checks on Docker service/container. If any problem then it will gather evidences and LLM do investigation and provide steps. 

This is not an auto-remediation agent. It will investigate and recommend, not blindly restart/delete/change anything.

                 USER
                   |
                   v
             +-----------+
             |    LLM    |
             +-----------+
                   |
                   | Tool Call
                   v
       +-------------------------+
       | check_docker_service()  |
       +-------------------------+
                   |
                   v
             DOCKER DESKTOP
                   |
                   v
             nginx-demo
                   |
                   v
        status / logs / evidence
                   |
                   v
             +-----------+
             |    LLM    |
             +-----------+
                   |
                   v
        INVESTIGATION STEPS
        + CONCLUSION


* Normally, if someone says: “The Nginx service is down.”

A DevOps/SRE engineer might manually do:
docker ps
docker ps -a
docker inspect <container>
docker logs <container>

** Our agent will demonstrate the first part of that workflow: So the project demonstrates how an LLM can become useful in a DevOps/SRE workflow by using tools, instead of just answering from its training knowledge.
User reports issue
       |
       v
AI Agent
       |
       v
Calls Docker health-check tool
       |
       v
Gets actual Docker evidence
       |
       v
LLM observes evidence
       |
       v
Suggests investigation steps

