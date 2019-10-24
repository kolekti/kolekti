Kolekti
=======

Kolekti est un logiciel créé par des professionnels de la rédaction, pour
des professionnels de la rédaction, dans le domaine de la documentation
technique (aides en ligne, notices d'instructions).
 
Il permet de publier automatiquement, à partir des mêmes fichiers
sources, plusieurs versions personnalisées en différents formats
(WebHelp, PDF, HTML5).
 
Kolekti est un logiciel libre qui utilise des formats ouverts : le fonds
documentaire est au format HTML.

Il s'installe en local sur les postes et offre la possibilité de
sauvegarde sur un serveur externe avec le protocole SVN (traçabilité et
sécurité).

Plus d'informations en nous contactant : <contact@kolekti.org>


Installation avec docker
========================

Prérequis
---------

* docker https://docs.docker.com/engine/installation/
* docker-compose https://docs.docker.com/compose/install/#alternative-install-options

> Kolekti a été développé, testé et est déployé avec docker-comopse 1.7.1
> Cette version est installée en utilisant le méthode pip.

Récupérer le code de Kolekti depuis github

    git clone https://github.com/kolekti/kolekti.git

    cd kolekti

Configuration
-------------

Editer le fichier `.env` pour configurer l'environnement dans lequel est lancé Kolekti.

### Parametres pour l'envoi d'emails

    KOLEKTI_EMAIL_HOST=mail.yourdomain.name
    KOLEKTI_EMAIL_PORT=465
    KOLEKTI_EMAIL_USER=kolekti@yourdomain.name
    KOLEKTI_EMAIL_PASSWORD=
    KOLEKTI_EMAIL_FROM=kolekti@.yourdomain.name

### Mode deboggage

    KOLEKTI_DEBUG=True

*Il est conseillé de laisser le mode debug pour un installation locale*

### Configuration reseau

    EXTERNAL_PORT=8800
    VIRTUAL_HOST=localhost

### Utilisateur

    UID=1000
    GID=1000

Données utilisateur
-------------------

Les données *utilisateur* de Kolekti : projets, dépôts svn, logs, base de données pour la gestion des utilisateurs, sont présentes dans le sous-dossier *run* du dossier Kolekti.

Il convient de crééer ces dossiers, avant de démarrer kolekti :

    mkdir -p run/db run/logs run/fonts run/prince run/projects run/svn run/log/kolekti


Lancement du serveur
--------------------

    docker-compose up -d

Vous pouvez vous connecter a l'url http://localhost:8800/ pour acceder à l'interface de Kolekti

Arret du serveur
----------------

    docker-compose down

Affichage de la sortie standard du serveur
------------------------------------------

    docker-compose log

Aliases
-------

le fichier .aliases contient des alias utiles pour administrer et utiliser kolekti en ligne de commande.

pour installer les alias dans votre shell:

    source .aliases

vous pouvez alors utiliser les alias:

* `kolekti` : pour lancer kolekti en CLI
* `kolekti-manage` : pour acceder aux commande de gestion de django
