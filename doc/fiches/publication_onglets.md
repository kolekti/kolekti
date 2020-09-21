# Gestion des onglets de langue dans la publication des releases

Cet élément des scripts de publication permet de générer des onglets latéraux verticaux à partir d'une définition structurée au format xml. Les structures et règles de style permettant la présence des onglets sont générés dans l'assemblage en amont de la création de l'épreuve sde sortie.

Pour créer des onglets dans un publication :

* Créer un fichier de configuration dans la version 
* Modifier les paramètres de publication

Le script de publication doit se termier par l'utilisation d'un outil de mise enpage supportant css3 et les modèles de page.

## Fichier de configuration

La configuration des onglets s'effectue dans un fichier `tabs.xml` placé, par convention, dans le dossier `sources/share` de la version. Ce fichier définit les onglets à faire figurer dans chaque volume de la publication finale d'une version. 

Ainsi si l'on veut générer les onglets pour deux volumes comprenant respectivement chacu 3 onglets, le fichier _tabs.xml_ comprendra :

    <tabs>
        <volume>
            <tab lang="en" label="English"/>
            <tab lang="fr" label="Français"/>
            <tab lang="it" label="Italiano"/>
        </volume>
        <volume>
            <tab lang="tr" label="Türkçe"/>
            <tab lang="he" label="עִבְרִית"/>
            <tab lang="ar" label="اَلْعَرَبِيَّةُ‎"/>
        </volume>
    </tabs>

Le filtre de pivot  *filter_tabs* génère le contenu à insérer dans les onglets latéraux, ainsi que les règles css nécessaires à leur insertion dans les bordures de page. Ce fichier doit être placé dans le dossier `kolekti/publication-templates/filterpivot/xsl/` du projet. 

Il est possible de surcharger les règles css dans le fichier `tabs.xml` pour adapter les couleurs, polices, tailles, marges... 

les balises `<style>` présentes respectivement dans les éléments <tabs>, <volume> et <tab> s'appliquent respectivement : au container des onglets présents dans les marges, au container d'un volume, à la boite de l'onglet lui même.

La création d'onglets processus de publication de kolekti qui consiste à enrichir l'assemblage à l'aide de filtres successif avant la génération du pdf.

Attention : La copie des  fichiers de définition d'onglets n'est pas automatique lors de la création d'une version, il faut les mettre à jour à la main dans les versions nouvellement créées.

## Paramètres de publication

Les paramètres de publication intègrent le script de type *filter_pivot* défini de la façon suivante :

    <script name="filterpivot">
        <parameters>
            <parameter name="filter" value="filter_tabs"/>
            <parameter name="filter_parameters" value="{'tabsfile':'source/share/tabs'}"/>
        </parameters>
    </script>

Si une version produit plusieurs formats de sortie alternatifs, il est possible de créer des fichiers de défintion pour chacun des formats. Il faut alors référencer ces définitions depuis l'élément `<parameters>` des parametres de chaque script de publication.

Exemple :

    <parameter name="filter_parameters" value="{'tabsfile':'source/share/A4_tabs'}"/>

