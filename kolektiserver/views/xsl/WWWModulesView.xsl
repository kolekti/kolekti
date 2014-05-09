<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kf ke kcd kd">

  <xsl:import href="WWWProjectView.xsl"/>

  <xsl:output method="xml" indent="yes"/>
  <xsl:variable name="currenttab">modules</xsl:variable>

  <xsl:template name="tabtitle"> - <i:text>[0022]Modules</i:text></xsl:template>

  <xsl:template name="sidebar">
    <kd:sidebar class="modulesidebar">
      <p class="heading">
         <span><a href="#usecase"><i:text>[0175]Cas d'emploi</i:text></a></span>
         <span class="case"><a href="#filterview"><i:text>[0179]Vue filtrée</i:text></a></span>
         <span class="case"><a href="#versions"><i:text>[0176]Versions</i:text></a></span>
         <span class="case"><a href="#diagnostic"><i:text>[0180]Diagnostic</i:text></a></span>
         <span class="case"><a href="#notes"><i:text>[0181]Notes de modification</i:text></a></span>
      </p>  
  <!-- a déplacer dans view 
      <h3>Actions (V)</h3>
      <p>-> Supprimer</p>
      <p>-> Dupliquer</p>
      <p>-> Renommer</p>
      <p>-> Déplacer</p>
      <p>-> Editer</p>
      <hr/>
  -->    
    </kd:sidebar>
  </xsl:template>

  <xsl:template name="mainleft">
   <kd:ajaxbrowser id="modulesbrowser" showtab="true">
<!--      <kd:layout>
        <kd:files />
         properties to display in browser 
        <kd:property ns="DAV:" propname="getcontentlength" />
        <kd:property ns="DAV:" propname="getlastmodified" />
        <kd:property ns="DAV:" propname="creationdate" />
        <kd:property ns="DAV:" propname="lockdiscovery" />
      </kd:layout>
-->
      <kd:behavior>
        <kd:click id="displaymodule" action="notify" event="resource-display-open" />
      </kd:behavior>

      <kd:actions>
        <kd:action ref="newdir" />
        <kd:action ref="newmodule" />
        <kd:action ref="browsereditmodule" />
        <kd:action ref="delete" />
      </kd:actions>

      <kd:tab i:label="[0152]Explorateur" dir="{$projectdir}/modules" id="modules" />
<!--      <kd:tab i:label="[0165]Recherche" class="search" id="search" /> -->
      <!-- Nom du fichier / contenu -> deux champs (et) 
	   Affichage dans l'explorateur : liste avec ascenseur 
	   - tri par plus récent (par défaut) / par nom
	   
      -->
      <!--
      <kd:tab i:label="[0077]Index" class="index" id="index" />
      Quand les meta données seront implémentées -->
    </kd:ajaxbrowser>
  </xsl:template>

  <xsl:template name="mainright">
    <kd:resourceview id="modulesviewer" class="projectresview">
      <kd:use class="moduleviewer">
        <kd:action ref="deleteresource"/>
        <kd:action ref="editmodule"/>
        <kd:action ref="duplicatemodule"/>
        <kd:action ref="renamemodule"/>
        <kd:action ref="movemodule"/>
        <kd:sidebar class="modulesidebar"> 
          <kd:property ns="kolekti:modules" propname="usage" />
          <kd:property ns="kolekti:modules" propname="filterview" />
          <kd:property ns="kolekti:modules" propname="versions" />
          <kd:property ns="kolekti:modules" propname="diagnostic" />
        </kd:sidebar>
      </kd:use>

      <kd:use class="moduleeditor">
         <kd:require>
            <xsl:attribute name="href">
               <xsl:choose>
                  <xsl:when test="kf:kolekticonf('debug') = true()">
                     <xsl:text>/_lib/kolekti/scripts/ckeditor/ckeditor_source.js</xsl:text>                  
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:text>/_lib/kolekti/scripts/ckeditor/ckeditor.js</xsl:text>
                  </xsl:otherwise>
               </xsl:choose>
            </xsl:attribute>
         </kd:require>
         <kd:action ref="displaymodule"/>
         <kd:action ref="save_as" />
         <kd:sidebar class="modulesidebar"> 
<!--
           <kd:property ns="kolekti:modules" propname="usage" />
-->
           <kd:property ns="kolekti:modules" propname="versions" />
           <kd:property ns="kolekti:modules" propname="notes" />
         </kd:sidebar>
      </kd:use>
    </kd:resourceview>
  </xsl:template>
</xsl:stylesheet>
