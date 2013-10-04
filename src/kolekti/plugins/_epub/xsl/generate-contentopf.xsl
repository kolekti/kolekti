<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:html="http://www.w3.org/1999/xhtml"
      xmlns="http://www.idpf.org/2007/opf"
      xmlns:opf="http://www.idpf.org/2007/opf"
      xmlns:dc="http://purl.org/dc/elements/1.1/"
      xmlns:dcterms="http://purl.org/dc/terms/"
      xmlns:kfe="kolekti:extensions:epub:functions"
      xmlns:exsl="http://exslt.org/common"
      
      extension-element-prefixes="exsl"
      exclude-result-prefixes="html">

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:include href="../../../xsl/pivot-utils.xsl"/>

  <xsl:param name="lang"/>
  <xsl:param name="author"/>
  <xsl:param name="css"/>
  
  <xsl:template match="text()" mode="item"> </xsl:template>
  <xsl:template match="text()" mode="itemref"> </xsl:template>

  <xsl:template match="/">
   <xsl:variable name="countnbpage" select="count(//html:div[@class='module'])" />
   <package version="2.0" unique-identifier="BookId">
      <metadata>
        <dc:title><xsl:value-of select="normalize-space(/html:html/html:head/html:title)" /></dc:title>
        <dc:language><xsl:value-of select="$lang" /></dc:language>
        <dc:identifier id="BookId" opf:scheme="EAN"><xsl:value-of select="generate-id()" /></dc:identifier>
        <dc:creator><xsl:value-of select="$author" /></dc:creator>
        <meta name="DTD" content="-//W3C//DTD XHTML 1.0 Strict//EN"/>
        <meta name="cover" content="cover-id"/>
        <meta name="dtb:totalPageCount" content="{$countnbpage}"/>
      </metadata>
      <manifest>
        <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
        <item href="css/base.css" id="basestylesheet" media-type="text/css"/>
        <item href="usercss/{$css}" id="userstylesheet" media-type="text/css"/>
        <item id="cover" href="coverpage.html" media-type="application/xhtml+xml"/>
        <item id="indexalpha" href="chapters/index.html" media-type="application/xhtml+xml"/>
        <xsl:apply-templates mode="item" />
      </manifest>
      <spine toc="ncx">
        <itemref idref="cover" linear="no"/>
        <itemref idref="indexalpha"/>
        <xsl:apply-templates mode="itemref" />
      </spine>
    </package>
  </xsl:template>
  
  <xsl:key name="medias" match="html:img" use="@src" />
  
  <xsl:template match="html:img" mode="item">
   <xsl:if test="generate-id() = generate-id(key('medias', @src)[1])">
     <xsl:variable name="mediatype" select="kfe:mimetype(string(@src))" />
     <item media-type="{$mediatype}" href="{@src}" id="{generate-id()}"/> 
   </xsl:if> 
  </xsl:template>
  
  <xsl:template match="html:div[@class='INDEX']" mode="item">
    <xsl:variable name="nbmod" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
    <xsl:if test="$nbmod &gt; 0">
      <item media-type="application/xhtml+xml" href="chapters/ch{$nbmod}_index.html" id="index{$nbmod}"/>
    </xsl:if>
    <xsl:apply-templates mode="item" />
  </xsl:template>
  
  <xsl:template match="html:div[@class='module']" mode="item">
    <xsl:variable name="nbmod" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
    <xsl:if test="$nbmod &gt; 0">
      <item media-type="application/xhtml+xml" href="chapters/ch{$nbmod}_{@id}.html" id="{@id}"/>
    </xsl:if>
    <xsl:apply-templates mode="item" />
  </xsl:template>

  <xsl:template match="html:div[@class='INDEX' and count(preceding::html:div[@class='module' or @class='INDEX']) &gt; 0]" mode="itemref">
    <xsl:variable name="nbmod" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
    <itemref idref="index{$nbmod}" />
    <xsl:apply-templates mode="itemref" />
  </xsl:template>

  <xsl:template match="html:div[@class='module' and count(preceding::html:div[@class='module' or @class='INDEX']) &gt; 0]" mode="itemref">
    <itemref idref="{@id}" />
    <xsl:apply-templates mode="itemref" />
  </xsl:template>
</xsl:stylesheet>
