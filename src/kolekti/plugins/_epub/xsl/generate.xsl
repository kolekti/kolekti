<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
   <!ENTITY mark "normalize-space(translate(@LIBEL,'abcdefghijklmnopqrstuvwxyzÉÀÇÈÙËÊÎÏÔÖÛÜÂÄéàçèùëêïîöôüûäâ','ABCDEFGHIJKLMNOPQRSTUVWXYZEACEUEEIIOOUUAAACEUEEIIOOUUAA'))">
  ]>
<xsl:stylesheet version="1.0"
      xmlns:html="http://www.w3.org/1999/xhtml"
      xmlns="http://www.w3.org/1999/xhtml"
      xmlns:exsl="http://exslt.org/common"
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      
      extension-element-prefixes="exsl"
      exclude-result-prefixes="html cont">

  <xsl:output method="xml"
         doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
         doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
         encoding="utf-8"
         indent="yes"/>

  <!-- this key contains all index marks -->
  <!--
  <xsl:key name="indexmarks" match="indx" use="''"/>
  <xsl:key name="indexmarkslibel" match="indx" use="string(@LIBEL)"/>
  -->

  <xsl:param name="pubdir"/>
  <xsl:param name="css"/>

  <xsl:template match="node()|@*">
   <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
   </xsl:copy>
  </xsl:template>
  
  <xsl:template match="/">
    <xsl:call-template name="container" />
    <xsl:apply-templates select="//html:div[@class='module' or @class='INDEX']"/>
<!--     <xsl:call-template name="buildindex"/> -->
  </xsl:template>
  
  <xsl:template name="container">
   <exsl:document 
      href="file://{$pubdir}/META-INF/container.xml"
      method="xml"
      omit-xml-declaration="no"
      encoding="utf-8">
      <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
          <rootfile media-type="application/oebps-package+xml" full-path="OEBPS/content.opf"/>
        </rootfiles>
      </container>
   </exsl:document>
  </xsl:template>
  
  <xsl:template match="html:div[@class='INDEX']">
    <xsl:variable name="chapnum" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
    <xsl:variable name="fileref">
      <xsl:value-of select="concat('file://', $pubdir, '/OEBPS/chapters/')" />
      <xsl:choose>
         <xsl:when test="$chapnum = 0">
            <xsl:text>index</xsl:text>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="concat('ch', $chapnum, '_index')" />
         </xsl:otherwise>
      </xsl:choose>
      <xsl:text>.html</xsl:text>
    </xsl:variable>

    <exsl:document href="{$fileref}"
         method="xml"
         doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
         doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
         encoding="utf-8">
       <html>
          <head>
             <title><xsl:value-of select="html:p[@class='INDEX_titre']" /></title>
             <link href="../css/base.css" type="text/css" rel="stylesheet" />
             <link href="../usercss/{$css}" type="text/css" rel="stylesheet" />
          </head>
          <body id="index{$chapnum}">
             <xsl:apply-templates />
          </body>
       </html>
    </exsl:document>
  </xsl:template>

  <xsl:template match="html:div[@class='module']">
    <xsl:variable name="chapnum" select="count(preceding::html:div[@class='module' or @class='INDEX'])" />
    <xsl:variable name="fileref">
      <xsl:value-of select="concat('file://', $pubdir, '/OEBPS/chapters/')" />
      <xsl:choose>
         <xsl:when test="$chapnum = 0">
            <xsl:text>index</xsl:text>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="concat('ch', $chapnum, '_', @id)" />
         </xsl:otherwise>
      </xsl:choose>
      <xsl:text>.html</xsl:text>
    </xsl:variable>
    <exsl:document href="{$fileref}"
         method="xml"
         doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
         doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
         encoding="utf-8">
      <html>
   <head>
     <title><xsl:value-of select="html:*[starts-with(local-name(), 'h')][1]" /></title>
     <link href="../css/base.css" type="text/css" rel="stylesheet" />
     <link href="../usercss/{$css}" type="text/css" rel="stylesheet" />
   </head>
   <body id="{@id}">
     <xsl:apply-templates />
   </body>
      </html>
    </exsl:document>
  </xsl:template>

  <xsl:template match="html:img">
   <img src="../{@src}" alt="{@alt}" title="{@title}" />
  </xsl:template>

  <xsl:template match="html:a[starts-with(@href, '#')]">
    <xsl:variable name="modlink" select="//html:div[@class='module' and @id=substring-after(current()/@href, '#')]" />
    <xsl:variable name="chapnum" select="count($modlink/preceding::html:div[@class='module' or @class='INDEX'])" />
    <xsl:variable name="fileref">
       <xsl:choose>
         <xsl:when test="$chapnum = 0">
           <xsl:text>index</xsl:text>
         </xsl:when>
         <xsl:otherwise>
           <xsl:value-of select="concat('ch', $chapnum, '_', $modlink/@id)" />
         </xsl:otherwise>
       </xsl:choose>
       <xsl:text>.html</xsl:text>
    </xsl:variable>
    <a>
       <xsl:copy-of select="@*" />
       <xsl:attribute name="href">
        <xsl:value-of select="$fileref" />
       </xsl:attribute>
       <xsl:apply-templates />
    </a>
  </xsl:template>

  <xsl:template match="html:div[@class='moduleinfo']"> </xsl:template>

</xsl:stylesheet>
