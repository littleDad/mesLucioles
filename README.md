Appli de gestion de lucioles.
Permet de gérer les calendriers, anniversaires,
comptes et autres joyeusetés avec ses amis :-)

Ce module est codé en python avec le framework Flask.

Note : j'ai relancé ce projet pour ma nouvelle coloc, la psycholoc.


Done :
- le module d'authentification
- la base de données en sqlite
- le module de gestion des comptes (money!)


ToDo :
- gestion des balances.

- formulaire de modification de dépense (avec précision de qui a ajouté la dépense à l'origine)
- page "effectuer un remboursement"

-------------------------
- garder en mémoire Catégorie, Payer_id et users_id en cas de réactualisation de la page en as de mauvais formulaire pour la page ajoutDépense
- ajouter les répartitions variables dans les dépenses (actuellement c'est fixe = divisé par le nombre de personnes)
- check la police (localhost/polices.html) > doit centraliser plein de polices que je puisse choisir :) page WIKI
- introduire mon module de messagerie theWall
- introduire un module de gestion des anniversaires et cadeaux
- introduire un module de calendrier et de gestion des évènements
- netooyer (reprendre les imports de chaque page. les doublons sont signe de mauvais cloisonnement dans mon code)

DOC : voir mon wiki page "python:flask" pour plus d'infos
