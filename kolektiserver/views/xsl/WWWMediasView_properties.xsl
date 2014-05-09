<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:d="DAV:"
                xmlns:kme="kolekti:medias"

                exclude-result-prefixes="i d kme">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="kolekti://utils/ui/xsl/properties.xsl"/>

  <xsl:template match="kme:heading">
   <kme:heading>
     <p class="heading">
       <span><a href="#usecase"><i:text>[0175]Cas d'emploi</i:text></a></span>
       <span class="case"><a href="#versions"><i:text>[0176]Versions</i:text></a></span>
     </p>  
   </kme:heading>
  </xsl:template>

  <xsl:template match="kme:usage">
   <kme:usage>
     <div class="usecase">
        <a name="usecase" />
        <h3><i:text>[0175]Cas d'emploi</i:text></h3>
        <div class="sidebar_section">
          <h4>Modules</h4>
          <xsl:choose>
           <xsl:when test="kme:module">
             <ul><xsl:apply-templates /></ul>
           </xsl:when>
           <xsl:otherwise>
             <p><i:text>[0177]Aucun module</i:text></p>
           </xsl:otherwise>
          </xsl:choose>
        </div>
     </div>
   </kme:usage>
  </xsl:template>

  <xsl:template match="kme:usage/kme:module">
   <li>
      <span style="display: none;">
         <span class="resid"><xsl:value-of select="@resid" /></span>
         <span class="urlid"><xsl:value-of select="@urlid" /></span>
         <span class="url"><xsl:value-of select="@url" /></span>
      </span>
      <span>
         <xsl:apply-templates />
      </span>
   </li>
  </xsl:template>
</xsl:stylesheet>
