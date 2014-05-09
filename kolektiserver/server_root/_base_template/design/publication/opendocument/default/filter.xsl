<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
		xmlns:html="http://www.w3.org/1999/xhtml"
		xmlns="http://www.w3.org/1999/xhtml"
		exclude-result-prefixes="html"
>
		
  <xsl:template match="node()|@*">
    <xsl:copy>
	<xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:h2">
    <h1><xsl:apply-templates /></h1>
  </xsl:template>
  
  <xsl:template match="html:h3">
    <h2><xsl:apply-templates /></h2>
  </xsl:template>
  
  <xsl:template match="html:h4">
    <h3><xsl:apply-templates /></h3>
  </xsl:template>
  
  <xsl:template match="html:h5">
    <h4><xsl:apply-templates /></h4>
  </xsl:template>
  
  <xsl:template match="html:h6">
    <h5><xsl:apply-templates /></h5>
  </xsl:template>
  
  <xsl:template match="html:div[@class='illustration']/html:p[not(@class)]">
    <xsl:copy>
      <xsl:attribute name="class">figimg</xsl:attribute>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='c2i-attention']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <p class="cadre-titre">Attention</p>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='c2i-remarque']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <p class="cadre-titre">Remarque</p>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
 
  <xsl:template match="html:div[@class='c2i-rappel']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <p class="cadre-titre">Rappel</p>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='c2i-exemple']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <p class="cadre-titre">Exemple</p>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='c2i-objectifs']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <p class="cadre-titre">Dans cette partie, vous aller apprendre...</p>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='c2i-synthese']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <p class="cadre-titre">Qu'avez vous retenu ?</p>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>
