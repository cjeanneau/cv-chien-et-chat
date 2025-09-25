### Créer un environnement virtuel et installer les dépendances

```bash
python -m venv baseenv
source baseenv/bin/activate
pip install --upgrade pip
pip install -r requirements/base.txt
```

ou executer directement dans un terminal
```bash
. setup.sh
```

### Démarrer le serveur fastAPI (à démarrer dans un terminal):
```bash
python scripts/run_api.py 
```
# Accès au serveur : http://127.0.0.1:8000

### Démarrage/arrêt des containers contenant le(s) Base(s) de données (à démarrer dans un terminal séparé)

# A voir car maintenant on peut ecrire docker compose ...
``` bash
docker-compose up       # pour créer et démarrer les containers
# docker-compose down     # pour arrêter les containers
```

# Création de la base de données
```bash
python scripts/init_db.py
```

