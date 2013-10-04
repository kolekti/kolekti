<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:html="http://www.w3.org/1999/xhtml"
      xmlns="http://www.daisy.org/z3986/2005/ncx/"
      xmlns:exsl="http://exslt.org/common"

      extension-element-prefixes="exsl"
      exclude-result-prefixes="html">

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>

  <xsl:template match="text()" mode="navmap"> </xsl:template>
  <xsl:template match="text()" mode="pagelist"> </xsl:template>

  <xsl:template match="/">
   <xsl:variable name="countnbpage" select="count(//html:div[@class='module' or @class='INDEX'])" />
   <ncx version="2005-1">
      <head>
        <meta name="dtb:uid" content="{generate-id()}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="{$countnbpage}"/>
        <meta name="dtb:maxPageNumber" content="{$countnbpage}"/>
      </head>
      <docTitle>
        <text><xsl:value-of select="normalize-space(following::html:h1[1])" /></text>
      </docTitle>
      <navMap>
        <xsl:apply-templates mode="navmap" />
      </navMap>
    </ncx>
  </xsl:template>

  <xsl:template match="html:div[@class='INDEX']" mode="navmap">
    <xsl:variable name="playorder" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
     <xsl:if test="$playorder &gt; 0">
       <navPoint id="{generate-id()}" playOrder="{$playorder}">
         <navLabel>
           <text><xsl:value-of select="normalize-space(html:p[@class='INDEX_titre'])" /></text>
         </navLabel>
         <content src="chapters/ch{$playorder}_index.html"/>
         <xsl:variable name="follow" select="following-sibling::html:*[1][@class='section']" />
         <xsl:if test="$follow">
           <xsl:apply-templates select="$follow" mode="navmap" />
         </xsl:if>
       </navPoint>
     </xsl:if>
  </xsl:template>

  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="navmap">
    <xsl:variable name="playorder" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
     <xsl:if test="$playorder &gt; 0">
       <navPoint id="{generate-id()}" playOrder="{$playorder}">
         <navLabel>
           <text><xsl:value-of select="normalize-space(.//html:*[starts-with(local-name(), 'h') and string-length(local-name()) = 2])" /></text>
         </navLabel>
         <content src="chapters/ch{$playorder}_{@id}.html"/>
         <xsl:variable name="follow" select="following-sibling::html:*[1][@class='section']" />
         <xsl:if test="$follow">
           <xsl:apply-templates select="$follow" mode="navmap" />
         </xsl:if>
       </navPoint>
     </xsl:if>
  </xsl:template>

  <xsl:template match="html:div[@class='INDEX']|html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="pagelist">
     <xsl:variable name="value" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
      <xsl:if test="$value &gt; 0">
        <xsl:variable name="playorder" select="count(//html:div[@class='module' or @class='INDEX'])-1+$value" />
        <pageTarget type="normal" value="{$value}" playOrder="{$playorder}" id="p{$value}">
          <navLabel>
              <text>Page <xsl:value-of select="$value" /></text>
           </navLabel>
           <content src="chapters/ch{$value}_{generate-id()}.html#page_{$value}"/>
        </pageTarget>
      </xsl:if>
      <xsl:apply-templates mode="pagelist" />
  </xsl:template>
</xsl:stylesheet>
