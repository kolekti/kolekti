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

  <xsl:variable name="currenttab">trames</xsl:variable>

  <xsl:template name="tabtitle"> - <i:text>[0029]Trames</i:text></xsl:template>

  <xsl:template name="mainleft">
   <kd:ajaxbrowser id="tramesbrowser">
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
        <kd:drag id="addtotrame" target="modules"/>
        <!-- <kd:click id="displaymodule" action="notify" event="resource-display-open" />-->
        <kd:click id="displaytrame" action="notify" event="resource-display-open" />
      </kd:behavior>

      <kd:actions>
        <kd:action ref="newtrame" />
        <kd:action ref="newtramedir" />
        <kd:action ref="delete" />
      </kd:actions>

      <kd:tab i:label="[0152]Explorateur" dir="{$projectdir}/trames" id="trames" />
      <kd:tab i:label="[0022]Modules" dir="{$projectdir}/modules" id="modules" />
    </kd:ajaxbrowser>
  </xsl:template>

  <xsl:template name="mainright">
    <kd:resourceview id="tramesviewer" class="projectresview">
      <kd:import class="trameeditor"/>
      <kd:use class="trameeditor">
         <kd:action ref="trame_add_section" />
         <kd:action ref="trame_add_tdm" />
         <kd:action ref="trame_add_index" />
         <kd:action ref="trame_add_revnotes" />
         <kd:action ref="trame_rename_section" />
         <kd:action ref="save_as" />
         <kd:action ref="publishtrame" />
         <kd:sidebar class="tramesidebar">
           <kd:property ns="kolekti:trames" propname="usage" />
           <kd:property ns="kolekti:trames" propname="diagnostic" />
           <kd:property ns="kolekti:trames" propname="notes" />
         </kd:sidebar>
      </kd:use>
    </kd:resourceview>
  </xsl:template>
</xsl:stylesheet>
