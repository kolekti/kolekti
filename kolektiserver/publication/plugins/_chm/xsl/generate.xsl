<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
		xmlns:html="http://www.w3.org/1999/xhtml"
		xmlns:exsl="http://exslt.org/common"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		extension-element-prefixes="exsl"
		exclude-result-prefixes="html"
		>
  <xsl:output method="html" indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"/>

  <xsl:param name="pubdir"/>
  <xsl:param name="label"/>
  <xsl:param name="css"/>

  <xsl:template match="node()|@*" mode="modcontent">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="modcontent"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:a[@class='indexmq']" mode="modcontent" />

  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]">
    <xsl:variable name="filename">
      <xsl:call-template name="modfile"/>
    </xsl:variable>
    <exsl:document href="file://{$upubdir}/{$label}/{$filename}" method='html' indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN">
      <html>
	<head>
	  <title><xsl:value-of select="normalize-space(html:*[starts-with(local-name(), 'h')])" /></title>
	  <link rel="stylesheet" type="text/css" href="css/topic.css"/>
	  <xsl:if test="$css">
	    <link rel="stylesheet" href="usercss/{$css}.css" type="text/css"/>
	  </xsl:if>
	  <xsl:copy-of select="/html:html/html:head/html:link[@rel='stylesheet']"/>
	</head>
	<body>
	  <xsl:apply-templates select="*[not(@class='moduleinfo')]" mode="modcontent"/>
	</body>
      </html>
    </exsl:document>
  </xsl:template>
  
  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="modlink">
   <xsl:call-template name="modfile" />
  </xsl:template>

  <xsl:template match="html:img" mode="modcontent">
   <xsl:variable name="src">
      <xsl:choose>
         <xsl:when test="starts-with(@src, 'http://')">
            <xsl:value-of select="@src" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>medias/</xsl:text>
            <xsl:value-of select="substring-after(@src, 'medias/')" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <img src="{$src}" alt="{@alt}" title="{@title}" />
  </xsl:template>
  
  <xsl:template match="html:embed" mode="modcontent">
   <xsl:variable name="src">
      <xsl:choose>
         <xsl:when test="starts-with(@src, 'http://')">
            <xsl:value-of select="@src" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>medias/</xsl:text>
            <xsl:value-of select="substring-after(@src, 'medias/')" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <embed width="{@width}" height="{@height}" type="{@type}" pluginspage="{@pluginspage}" src="{$src}" />
  </xsl:template>
  
  <xsl:template match="html:a[starts-with(@href, '#')]" mode="modcontent">   
   <xsl:variable name="localfile">
      <xsl:apply-templates select="//html:div[@class='module' and @id = substring(current()/@href, 2)]" mode="modlink"/>
   </xsl:variable>
   <a href="{$localfile}"><xsl:apply-templates mode="modcontent" /></a>
  </xsl:template>
  
  <xsl:template match="html:a[@href='#']" mode="modcontent">   
   <xsl:apply-templates select="node()" mode="modcontent"/>
  </xsl:template>

  <xsl:variable name="upubdir">
    <xsl:if test="not(starts-with($pubdir,'/'))">
      <xsl:text>/</xsl:text>
    </xsl:if>
    <xsl:call-template name="slashes">
      <xsl:with-param name="text" select="$pubdir"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:template name="slashes">
    <xsl:param name="text"/>
    <xsl:choose>
      <xsl:when test="contains($text,'\')">
   <xsl:value-of select="substring-before($text,'\')"/>
   <xsl:text>/</xsl:text>
   <xsl:call-template name="slashes">
     <xsl:with-param name="text" select="substring-after($text,'\')"/>
   </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
   <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="basesource">
    <xsl:param name="src"/>
    <xsl:choose>
      <xsl:when test="contains($src,'/')">
    <xsl:call-template name="basesource">
      <xsl:with-param name="src">
        <xsl:value-of select="substring-after($src,'/')"/>
      </xsl:with-param>
    </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($src,'.')">
    <xsl:value-of select="substring-before($src,'.')"/>
      </xsl:when>
      <xsl:otherwise>
    <xsl:value-of select="$src"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>  
  
  <xsl:template name="modfile">
    <xsl:choose>
      <xsl:when test="html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='hlptopic']">
    <xsl:value-of select="html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='hlptopic']/html:span[@class='infovalue']"/>
      </xsl:when>
      <xsl:otherwise>
    <xsl:call-template name="basesource">
      <xsl:with-param name="src">
        <xsl:value-of select="html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='source']/html:span[@class='infovalue']"/>
      </xsl:with-param>
    </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>    
    <xsl:text>.html</xsl:text>
  </xsl:template>

</xsl:stylesheet>
