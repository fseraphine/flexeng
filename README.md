# Flexeng

Script d'administration des machines sur Orange Business Cloud Flexible Engine

Fonctionne via les appels API: https://docs.prod-cloud-ocb.orange-business.com/en-us/index.html

## Usage
Usage : `flexeng <action> [<tagname>=<tagvalue>]`  
actions : help list start stop  
exemple : "flexeng list groupe=sul"  
exemple : "start" équivalent à "start startup yes"  
exemple : "stop" équivalent à "stop shutdown yes"  

## Aide

help : affiche cette aide.

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
- FE_USER_PASSWORD : le mot de passe API que vous avez initialisé depuis votre mail "Bienvenue sur la console Flexible Engine"