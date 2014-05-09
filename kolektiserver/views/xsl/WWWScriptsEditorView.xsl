<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"

                exclude-result-prefixes="i">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="scripts">
   <div id="scripts">
     <xsl:apply-templates select="script"/>
     <p id="btn_addcriterias"><i:text>[0236]Ajouter un script</i:text></p>
   </div>
  </xsl:template>

  <xsl:template match="script"> </xsl:template>
</xsl:stylesheet>