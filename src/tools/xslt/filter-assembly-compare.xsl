<!--
    Cette feuille de style permet d'évacuer les informations parasites pour la comparaison des assemblages

    usage : xsltproc filter-assembly-compare.xsl [chemin du fichier assemblage] > [chemin du fichier traité]
-->

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml">

  <xsl:output method="xml" indent="yes"/>
  
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:body//@id"/>
  <xsl:template match="html:div[@class='topicinfo']"/>

</xsl:stylesheet>
