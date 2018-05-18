<!--
    Cette feuille de style permet d'évacuer les informations parasites pour la comparaison des assemblages

    usage : xsltproc filter-assembly-compare.xsl [chemin du fichier assemblage] > [chemin du fichier traité]
-->

<xsl:stylesheet version="1.0"
                xmlns:xsl="https://www.w3.org/1999/XSL/Transform"
                xmlns:html="https://www.w3.org/1999/xhtml">

  <xsl:template match="html:div[@class='topic'][@id]"/>
  <xsl:template match="html:div[@class='topicinfo']"/>

</xsl:stylesheet>
