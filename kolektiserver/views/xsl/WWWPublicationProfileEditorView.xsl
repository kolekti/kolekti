<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kol="http://www.exselt.com/kolekti"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"
                xmlns:dav="DAV:"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kol kf ke kcd kd dav">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="WWWConfigurationView_properties.xsl"/>
  
  <xsl:variable name="projectdir">/projects/<xsl:value-of select="kf:get_http_data('kolekti', 'project')/@directory" /></xsl:variable>

  <xsl:template match="node()|@*">
      <xsl:apply-templates select="node()|@*" />
  </xsl:template>

  <xsl:template match="kcd:data">
   <xsl:apply-templates select="kcd:namespace[@id='http']/kcd:value[@key='body']" />
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='http']/kcd:value[@key='body']">
   <div class="publicationprofileeditor">
      <xsl:apply-templates select="publicationprofile" />
   </div>
  </xsl:template>

  <xsl:template match="publicationprofile">
   <div class="publicationprofile">
      <p class="label">
         <label for="label{generate-id()}"><i:text>[0150]Label</i:text></label>
         <span class="formvalue">
            <input id="label{generate-id()}" type="text" name="label" value="{label/text()}"/>
         </span>
      </p>
      <xsl:apply-templates select="kf:getcriterias()" mode="profile">
         <xsl:with-param name="pcriterias" select="criterias" />
      </xsl:apply-templates>
   </div>
  </xsl:template>
</xsl:stylesheet>