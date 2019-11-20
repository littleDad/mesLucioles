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

  * lancer l'appli : ./run.py

  * se connecter avec un navigateur web sur localhost:5000 avec les id b@t/coucou
  

Additionnel :
  * ajouter un user : ./administration 0 bob@laposte.net password1234


###############################################################################




Done :
- le module d'authentification
- la base de données en sqlite
- le module de gestion des comptes (money!)
- addBill(gérer l'initialisation des balances)
- edit password
- delBill

ToDo :
- editBill 
- remboursements
- gérer les exceptions (vérification de l'ajout de dépenses négatives, des centimes en trop, etc.)
- ajouter une calculatrice sur la page d'ajoutDepense
- "tous" pour cocher les cases de 'pour qui cette dépense ?' dans ajoutDépense


- champ de recherche pour les factures
- centraliser (encapsuler dans une méthode de User) l'ajout et la suppression de dépense actuellement contrôlés à l'arrache dans models.Spending (c'est vraiment très sale, sorte de trigger manuel sur une classe étrangère ("Users" et son attribut "depense")...) 
- rembourrer les logs, c'est toujours pratique

- formulaire de modification de dépense (avec précision de qui a ajouté la dépense à l'origine + gérer minutieusement le rétablissement des balances des users)
- page "effectuer un remboursement"

- ce serait bien de nettoyer models.py, notamment l'imbrication des classes et l'héritage (par exemple Balance devrait être une classe de User, soit User.Balance ; ce n'est pas fait actuellement car cela pose un problème au moment de la génération automatique de la base sql par l'ORM SQLalchemy essaye alors de créer la table 'balance' à  l'intérieur de la table 'user' ce qui est évidemment ridicule.)

-------------------------
- gestion de la cohérence des sous : AjoutDépenses et balances. triggers ? vérifications à chaque lancements de l'appli ? actuellement y a du duplicat d'info (notamment : duplicat des montants qui sont à la fois dans Spending(parts) et dans User(balance). noramelement y a pas de souci, mais dans le fond c'est MAL !)
- garder en mémoire Catégorie, Payer_id et users_id en cas de réactualisation de la page en as de mauvais formulaire pour la page ajoutDépense
- ajouter les répartitions variables dans les dépenses (actuellement c'est fixe = divisé par le nombre de personnes)
- check la police (localhost/polices.html) > doit centraliser plein de polices que je puisse choisir :) page WIKI
- introduire un module de messagerie (type theWall)
- introduire un module de gestion des anniversaires et cadeaux
- introduire un module de calendrier et de gestion des évènements
- nettoyer (notamment, reprendre et checker les imports de chaque page. certains doublons sont signe de mauvais cloisonnement dans mon code)

DOC : voir mon wiki page "python:flask" pour plus d'infos
