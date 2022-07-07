#!env python

import requests
import json
import sys
import os

FE_IAM_URL="https://iam.eu-west-0.prod-cloud-ocb.orange-business.com"
FE_ECS_URL="https://ecs.eu-west-0.prod-cloud-ocb.orange-business.com"

USAGE="""Usage : flexeng <action> [<tagname>=<tagvalue>]
actions : help list start stop
exemple : "flexeng list groupe=sul"
exemple : "start" équivalent à "start startup yes"
exemple : "stop" équivalent à "stop shutdown yes"
"""

def get_auth_token(domain:str, project:str, username:str, password:str):
    api_url = FE_IAM_URL + "/v3/auth/tokens"
    body="""
    {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": "%s",
                        "password": "%s",
                        "domain": {
                            "name": "%s"
                        }
                    }
                }
            },
            "scope": {
                "project": {
                    "name": "%s"
                }
            }
        }
    }"""%(username,password,domain,project)

    body_json = json.loads(body)
    response = requests.post(api_url, json=body_json)
    if response.status_code == 201:
        fe_tok = response.headers["X-Subject-Token"]
        return fe_tok
    else:
        print("get_auth_token:" + response.text)
        return False


def list_all_ecs(project_id):
    api_url = FE_ECS_URL + f"/v2.1/{project_id}/servers"

    response = requests.get(api_url, headers = {"X-Auth-Token": FE_TOKEN})
    servers = {}
    if response.status_code == 200:
        ecs_json = response.json()
        for s in (ecs_json["servers"]):
            servers[s["name"]]=s["id"]
    else:
        print(response.text)
    return servers


def list_ecs(project_id, tag, value):
    api_url = FE_ECS_URL + f"/v1/{project_id}/servers/resource_instances/action"
    body="""{
        "limit": "20", 
        "action": "filter",  
        "tags": [
        {
            "key": "%s", 
            "values": [ "%s"]
        }]
    }"""%(tag, value)

    body_json = json.loads(body)
    response = requests.post(api_url, json=body_json, headers = {"X-Auth-Token": FE_TOKEN})
    servers = {}
    if response.status_code == 200:
        ecs_json = response.json()
        for s in (ecs_json["resources"]):
            servers[s["resource_name"]]=s["resource_id"]
    else:
        print(response.text)
    return servers


def do_ecs(action,project_id, servers):
    api_url = FE_ECS_URL + f"/v1/{project_id}/cloudservers/action"
    serv_frag_list = []
    for s in servers.values():
        serv_frag_list.append({"id": s})
    serv_frag = { "servers": serv_frag_list }
    body_json = { f"os-{action}": serv_frag }

    response = requests.post(api_url, json=body_json, headers = {"X-Auth-Token": FE_TOKEN})
    if response.status_code == 200:
        print(response.text)
        return True
    else:
        print(response.text)
        return False

def get_environ():
    global FE_DOMAIN_NAME
    global FE_PROJECT_NAME
    global FE_PROJECT_ID
    global FE_USER_NAME
    global FE_USER_PASSWORD

    if "FE_DOMAIN_NAME" not in os.environ or "FE_PROJECT_NAME" not in os.environ or "FE_PROJECT_ID" not in os.environ \
    or "FE_USER_NAME" not in os.environ or "FE_USER_PASSWORD" not in os.environ:
        print("Erreur: Vous devez initialiser les variables d'environnement FE_DOMAIN_NAME FE_PROJECT_NAME FE_PROJECT_ID FE_USER_NAME")
        exit(-2)

    FE_DOMAIN_NAME=os.getenv("FE_DOMAIN_NAME")
    FE_PROJECT_NAME=os.getenv("FE_PROJECT_NAME")
    FE_PROJECT_ID=os.getenv("FE_PROJECT_ID")
    FE_USER_NAME=os.getenv("FE_USER_NAME")
    FE_USER_PASSWORD=os.getenv("FE_USER_PASSWORD")


def get_args():
    nbargs = len(sys.argv)
    if  nbargs == 2:
        action = sys.argv[1]
        if action == "stop":
            tagname,tagvalue="shutdown","yes"
        elif action == "start":
            tagname,tagvalue="startup","yes"
        else:
            tagname,tagvalue=False,False
    elif nbargs == 3:
        action = sys.argv[1]
        tagname,tagvalue = sys.argv[2].split("=")
    else:
        print(USAGE)
        exit(-1)
    return nbargs,action,tagname,tagvalue

def main():
    get_environ()
    
    nbargs,action,tagname,tagvalue=get_args()

    global FE_TOKEN
    FE_TOKEN=get_auth_token(FE_DOMAIN_NAME,FE_PROJECT_NAME,FE_USER_NAME,FE_USER_PASSWORD)
    if FE_TOKEN is False:
        print('Erreur à la récupération du token')
        exit(1)

    if action == "start" or action == "stop":
        servers = list_ecs(FE_PROJECT_ID,tagname,tagvalue)
        #print("list_ecs : " + str(servers))
        if do_ecs(action,FE_PROJECT_ID,servers):
            servers_names = [s for s in servers.keys()]
            print(f"{action} machines (" + str(len(servers_names)) + "):"+ str(servers_names))
    elif action == "list":
        if nbargs == 2:
            servers = list_all_ecs(FE_PROJECT_ID)
            servers_names = [s for s in servers.keys()]
            print(f"Machines (" + str(len(servers_names)) + "):"+ str(servers_names))
        else:
            servers = list_ecs(FE_PROJECT_ID,tagname,tagvalue)
            servers_names = [s for s in servers.keys()]
            print(f"Machines pour {tagname}={tagvalue} (" + str(len(servers_names)) + "):"+ str(servers_names))
    else:
        print(USAGE)
        exit(-1)

if __name__ == "__main__":
    main()