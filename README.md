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

Plus d'informations en nous contactant : <contact@kolekti.org>


Installation avec docker
========================

Prérequis
---------

* docker https://docs.docker.com/engine/installation/
* docker-compose https://docs.docker.com/compose/install/#alternative-install-options

> Kolekti a été développé, testé et est déployé avec docker-comopse 1.11
> Cette version est installée en utilisant le méthode pip.

* Récupérez le code de Kolekti depuis github

    git clone https://github.com/kolekti/kolekti.git

    cd kolekti
    
    git checkout kolekti-cli
    
Initialisation
--------------

Pour initialiser l'image kolekti-cli, lancez la commande (toujours dans le dossier `kolekti`)

    docker-compose build
    
Note : plus de 1 Go sont téléchargés (patience)
    
Lancement
--------------

Pour lancer kolekti, lancez le conteneur en lui spécifiant le chemin d'accès à la base kolekti :

### En utilisant la commande docker

    docker run --rm  -ti -v /my/project:/project --entrypoint "kolekti" kolekti_cli -b /project ...
    
### En utilisant docker-compose 
Dans le dossier `kolekti`

    KOLEKTI_PROJECT=/my/project docker-compose run --rm kolekti -b /project ...

### En utilisant un alias 

Le fichier .aliases contient des alias utiles pour administrer et utiliser kolekti en ligne de commande.

Pour installer les alias dans votre shell (toujours dans le dossier `kolekti`) :

    source .aliases

Vous pouvez alors utiliser les alias :

    `kolekti /my/project ... ` : pour lancer kolekti en CLI
    
Pour que la commande kolekti soit toujours disponible dans les shells (lançable depuis n'importe quel emplacement), copiez le contenu de .aliases et ajoutez-le à la fin de ~/.bashrc

Cela peut être effectué à l'aide de la commande : 

     cat .aliases >> ~/.bashrc


Configuration
-------------
[TO BE DONE]
* Le dossier kolekti/fonts kolekti/princexml
