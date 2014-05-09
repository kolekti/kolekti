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

  <xsl:variable name="currenttab">publications</xsl:variable>
  <xsl:template name="tabtitle"> - <i:text>[0025]Publications</i:text></xsl:template>

  <xsl:template name="mainleft">
   <kd:ajaxbrowser id="publicationsbrowser" showtab="true">
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
        <kd:click id="displaypublication" action="notify" event="resource-display-open" />
      </kd:behavior>

      <kd:actions>
        <kd:action ref="delete" />
      </kd:actions>

      <kd:tab i:label="[0152]Explorateur" dir="{$projectdir}/publications" id="publications" />
    </kd:ajaxbrowser>
  </xsl:template>

  <xsl:template name="mainright">
    <kd:resourceview id="publicationsviewer" class="projectresview">
      <kd:use class="publicationviewer">
      <kd:sidebar  class="publicationsidebar"> 
         <kd:property ns="kolekti:publication" propname="languages" />
         <kd:property ns="kolekti:publication" propname="versions" />
      </kd:sidebar>
      </kd:use>
    </kd:resourceview>
  </xsl:template>
</xsl:stylesheet>
