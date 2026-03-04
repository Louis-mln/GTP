# Countdown (Flask)

Petit site de compte à rebours (Flask + page statique) avec un thème sakura.
Le front lit la configuration via une API, et (optionnellement) permet de modifier la config via un panneau admin.

## Fonctionnement

- Le serveur Flask sert :
  - la page `static/index.html`
  - une API JSON :
    - `GET /api/config` : récupère la configuration
    - `POST /api/config` : met à jour la configuration (protégé par mot de passe)

- La configuration est stockée dans `config.json` à la racine du projet.

## Prérequis

- Python 3
- (Recommandé) environnement virtuel `venv`

## Installation (local)

```bash
cd /opt/countdown   # ou le dossier du projet
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt