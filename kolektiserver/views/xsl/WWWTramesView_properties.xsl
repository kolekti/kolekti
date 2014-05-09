<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:d="DAV:"
                xmlns:kt="kolekti:trames"

                exclude-result-prefixes="i d kt">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="kolekti://utils/ui/xsl/properties.xsl"/>

  <xsl:template match="kt:heading">
   <kt:heading>
     <p class="heading">
      <span><a href="#usecase"><i:text>[0175]Cas d'emploi</i:text></a></span>
      <span class="case"><a href="#diagnostic"><i:text>[0180]Diagnostic</i:text></a></span>
     </p>
   </kt:heading>
  </xsl:template>

  <xsl:template match="kt:usage">
   <kt:usage>
     <div class="usecase">
        <a name="usecase" />
        <h3><i:text>[0175]Cas d'emploi</i:text></h3>
        <div class="sidebar_section">
          <h4><i:text>[0217]Lancements</i:text></h4>
          <xsl:choose>
           <xsl:when test="kt:order">
             <ul><xsl:apply-templates /></ul>
           </xsl:when>
           <xsl:otherwise>
             <p><i:text>[0240]Aucun lancement</i:text></p>
           </xsl:otherwise>
          </xsl:choose>
        </div>
     </div>
   </kt:usage>
  </xsl:template>

  <xsl:template match="kt:usage/kt:order">
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

  <xsl:template match="kt:diagnostic">
   <kt:diagnostic>
      <div class="diagnostic">
        <a name="diagnostic" />
        <h3><i:text>[0180]Diagnostic</i:text></h3>
        <div class="sidebar_section">
          <xsl:apply-templates />
          <xsl:if test="count(error) = 0">
            <p><i:text>[0186]Aucune erreur trouvée</i:text></p>
          </xsl:if>
        </div>
      </div>
   </kt:diagnostic>
  </xsl:template>

  <xsl:template match="kt:diagnostic/success"> </xsl:template>

  <xsl:template match="kt:diagnostic/error">
   <p style="color:red;">
      <xsl:choose>
         <xsl:when test="@type = 'invalid'">
            <xsl:apply-templates /><xsl:text>: </xsl:text><i:text>[0346]Module mal formé</i:text>
         </xsl:when>
         <xsl:otherwise>
            <xsl:apply-templates /><xsl:text>: </xsl:text><i:text>[0188]Module inexistant</i:text>
         </xsl:otherwise>
      </xsl:choose>
   </p>
  </xsl:template>

  <xsl:template match="kt:notes">
   <kt:notes>
      <div class="notes">
        <a name="notes" />
        <h3><i:text>[0181]Notes de modification</i:text></h3>
        <div class="sidebar_section">
          <textarea>&#xA0;</textarea>
     <xsl:if test="normalize-space(.) != ''">
       <p>
         <em><i:text>[0194]Note précédente</i:text> : </em><br/>
         <xsl:value-of select="."/><br/>
         <button id="sidebarnotecopy"><i:text>[0195]Copier</i:text></button>
       </p>
     </xsl:if>
        </div>
      </div>
   </kt:notes>
  </xsl:template>
</xsl:stylesheet>
