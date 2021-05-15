Appli de gestion de colocs.
Permet de gérer les comptes (et peut-être un jour les calendriers, anniversaires et autres joyeusetés) !

Ce module est codé en python 3, avec Flask.


###############################################################################
QUICKSTART :
  * modifier votre SECRET_KEY (config.py)

  * créer l'environnement virtuel :
        virtualenv env -p /usr/bin/python3 --no-site-packages

  * installer les dépendances dans cet environnement
        source env/bin/activate
        pip install -r requirements.txt

  * générer la base : ./db_create.py

  * l'initialiser avec un jeu de test : ./administration.py init

  * créer 2 var d'environnement (par exemple avec direnv et un .envrc) : SECRET_KEY et PORT (ce second est optionnel)

  * lancer l'appli : ./run.py

  * se connecter avec un navigateur web sur localhost:5000 avec les id b@t/coucou
  

Additionnel :
  * ajouter un user : ./administration 0 bob@laposte.net password1234
  * to mgirate:
    * change the model
    * run ./db_upgrade
    * run ./db_migrate
