#!env python

import requests
import json
import sys
import os


USAGE="""Usage : flexeng <action> [<tagname>=<tagvalue>]
actions : help list start stop
exemple : "flexeng list groupe=sul"
exemple : "start" équivalent à "start startup=yes"
exemple : "stop" équivalent à "stop shutdown=yes"
"""

HELP="""flexeng

- help : affiche cette aide.

- list : liste toutes les machines ECS du projet.
- list tag=val : liste toutes les machines ECS du projet qui portent le tag avec la valeur précisée.

- start : démarre toutes les machines ECS qui portent le tag startup=yes.
- start tag=val : démarre toutes les machines ECS qui portent le tag avec la valeur précisée.

- stop : arrête toutes les machines ECS qui portent le tag shutdown=yes.
- stop tag=val : arrête toutes les machines ECS qui portent le tag avec la valeur précisée.

Vous devez initialiser les variables d'environnement suivantes :
- FE_REGION : la région Flexible Engine
- FE_DOMAIN_NAME : le nom de votre domain Flexible Engine (page My Credential)
- FE_PROJECT_NAME : le nom de votre projet Flexible Engine (page My Credential)
- FE_PROJECT_ID : l'id de votre projet Flexible Engine (page My Credential)
- FE_USER_NAME : votre nom d'utilisateur (page My Credential)
- FE_USER_PASSWORD : le mot de passe API que vous avez initialisé depuis votre mail "Bienvenue sur la console Flexible Engine
"""

def get_auth_token():
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
    }"""%(FE_USER_NAME,FE_USER_PASSWORD,FE_DOMAIN_NAME,FE_PROJECT_NAME)
    
    global FE_TOKEN
    
    body_json = json.loads(body)
    response = requests.post(api_url, json=body_json)
    if response.status_code == 201:
        FE_TOKEN = response.headers["X-Subject-Token"]
    else:
        FE_TOKEN = False
        print("get_auth_token:" + response.text)
        print('Erreur à la récupération du token')
        exit(1)


def list_all_ecs():
    api_url = FE_ECS_URL + f"/v2.1/{FE_PROJECT_ID}/servers"

    response = requests.get(api_url, headers = {"X-Auth-Token": FE_TOKEN})
    servers = {}
    if response.status_code == 200:
        ecs_json = response.json()
        for s in (ecs_json["servers"]):
            servers[s["name"]]=s["id"]
    else:
        print(response.text)
    return servers


def list_ecs(tag:str, value:str):
    api_url = FE_ECS_URL + f"/v1/{FE_PROJECT_ID}/servers/resource_instances/action"
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


def do_ecs(action:str, servers:list):
    api_url = FE_ECS_URL + f"/v1/{FE_PROJECT_ID}/cloudservers/action"
    body_json = { f"os-{action}": { "servers": [{"id": s} for s in servers.values()] } }

    response = requests.post(api_url, json=body_json, headers = {"X-Auth-Token": FE_TOKEN})
    if response.status_code == 200:
        print(response.text)
        return True
    else:
        print(response.text)
        return False

def get_env_vars():
    global FE_REGION, FE_DOMAIN_NAME, FE_PROJECT_NAME,FE_PROJECT_ID,FE_USER_NAME,FE_USER_PASSWORD
    global FE_IAM_URL, FE_ECS_URL

    if "FE_REGION" not in os.environ or "FE_DOMAIN_NAME" not in os.environ or "FE_PROJECT_NAME" not in os.environ \
    or "FE_PROJECT_ID" not in os.environ or "FE_USER_NAME" not in os.environ or "FE_USER_PASSWORD" not in os.environ:
        print("Erreur: Vous devez initialiser les variables d'environnement FE_REGION FE_DOMAIN_NAME FE_PROJECT_NAME FE_PROJECT_ID FE_USER_NAME FE_USER_PASSWORD")
        exit(-2)

    FE_REGION=os.getenv("FE_REGION")
    FE_DOMAIN_NAME=os.getenv("FE_DOMAIN_NAME")
    FE_PROJECT_NAME=os.getenv("FE_PROJECT_NAME")
    FE_PROJECT_ID=os.getenv("FE_PROJECT_ID")
    FE_USER_NAME=os.getenv("FE_USER_NAME")
    FE_USER_PASSWORD=os.getenv("FE_USER_PASSWORD")

    FE_IAM_URL=f"https://iam.{FE_REGION}.prod-cloud-ocb.orange-business.com"
    FE_ECS_URL=f"https://ecs.{FE_REGION}.prod-cloud-ocb.orange-business.com"


def get_args():
    nbargs = len(sys.argv)
    action,tagname,tagvalue = sys.argv[1],False,False
    if  nbargs == 2:
        if action == "stop":
            tagname,tagvalue="shutdown","yes"
        elif action == "start":
            tagname,tagvalue="startup","yes"
    elif nbargs == 3:
        tagname,tagvalue = sys.argv[2].split("=")
    else:
        print(USAGE)
        exit(-1)
    return action,tagname,tagvalue

if __name__ == "__main__":
    action,tagname,tagvalue=get_args()

    if action == "start" or action == "stop":
        get_env_vars()
        get_auth_token()
        servers = list_ecs(tagname,tagvalue)
        if do_ecs(action,servers):
            servers_names = [s for s in servers.keys()]
            print(f"{action} machines (" + str(len(servers_names)) + "):"+ str(servers_names))
    elif action == "list":
        get_env_vars()
        get_auth_token()
        if tagname is False:
            servers = list_all_ecs()
            servers_names = [s for s in servers.keys()]
            print(str(len(servers_names)) + " machine(s) trouvées:"+ str(servers_names))
        else:
            servers = list_ecs(tagname,tagvalue)
            servers_names = [s for s in servers.keys()]
            print( str(len(servers_names)) + f" machine(s) trouvées pour {tagname}={tagvalue} (" + str(servers_names))
    elif action == "help":
        print(HELP)
    else:
        print(USAGE)
        exit(-1)
