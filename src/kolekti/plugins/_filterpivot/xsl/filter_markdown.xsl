<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:h="http://www.w3.org/1999/xhtml"
  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="h"
  version="1.0">
  
  <xsl:template match="node()|@*" name="id">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="@id"/>
  <xsl:template match="/h:html/h:head/h:meta"/>
  <xsl:template match="h:div[@class='topicinfo']"/>
  <xsl:template match="h:div[@class='TOC']"/>
  <xsl:template match="h:div[@class='INDEX']"/>
  <xsl:template match="h:div[@class='topic']">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="h:a[@class='indexmq']"/>
  <xsl:template match="h:ins[@class='index']">
    <span>
      <xsl:text> ((</xsl:text>
      <xsl:apply-templates/>
      <xsl:text>))</xsl:text>
    </span>
  </xsl:template>
  <xsl:template match="h:span[ancestor-or-self::h:span[@class='title_num']]">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="h:a[starts-with(@href, '#topicidm')]">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text>
        <xsl:value-of select="substring-after(@href, '_')"/>
      </xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="h:h1/@class"/>  
  <xsl:template match="h:h2/@class"/>  
  <xsl:template match="h:h3/@class"/>  
  <xsl:template match="h:h4/@class"/>  
  <xsl:template match="h:h5/@class"/>  
  <xsl:template match="h:h6/@class"/>  

  <xsl:template match="comment()"/>
  
</xsl:stylesheet>
