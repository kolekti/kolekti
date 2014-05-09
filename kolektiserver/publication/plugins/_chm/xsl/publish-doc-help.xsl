<?xml version="1.0" encoding="utf-8"?>

<!-- 
 * File   : publish-doc-help.xsl
 * Author : Stephane Bonhomme <s.bonhomme@wanadoo.fr>
 * Date   : 03/07/2004
 * Descr  : This file is part of the documentation system
            developped for ELA-medical
            This program scans the xhtml publication file
            and produce files to build the winhelp
 * Log    :

-->
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:html="http://www.w3.org/1999/xhtml" 
  xmlns:exsl="http://exslt.org/common"
  xmlns:k="uri:kolekti"
  xmlns:kepf="kolekti:extensions:plugin:functions"
  xmlns:kef="kolekti:extensions:publication"
  extension-element-prefixes="exsl"  
  exclude-result-prefixes="html k kepf kef"
  version="1.0">

  <xsl:param name="langfile" />
  <xsl:param name="publang"/>
  <xsl:param name="pubdocdir"/>
  <xsl:param name="pubdoccode"/>
  <xsl:param name="sheetspath"/>
  <xsl:param name="profilename"/>
  <k:bindings>
    <k:bind lang="cs" encoding="WINDOWS-1250" />
    <k:bind lang="pl" encoding="WINDOWS-1250" />
    <k:bind lang="sl" encoding="WINDOWS-1250" />
    <k:bind lang="hu" encoding="WINDOWS-1250" />
    <k:bind lang="ro" encoding="WINDOWS-1250" />
    <k:bind lang="yu" encoding="WINDOWS-1250" />
    <k:bind lang="hv" encoding="WINDOWS-1250" />
  </k:bindings>
	  
  <xsl:variable name="encoding">
    <xsl:choose>
	    <xsl:when test="$publang=document('')//k:bindings/k:bind/@lang">
	      <xsl:value-of select="document('')//k:bindings/k:bind[$publang=@lang]/@encoding"/>
      </xsl:when>
      <xsl:otherwise>WINDOWS-1252</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="pubdocname">
	  <xsl:value-of select="normalize-space(/html:html/html:head/html:title)"/>
  </xsl:variable>

  <xsl:key name="indexmarks" match="html:span[@rel='index']|html:ins[@class='index']" use="text()"/>

  <xsl:template match="/html:html"> 
    <xsl:variable name="urlchmproject">
      <xsl:value-of select="$pubdocdir"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$pubdoccode"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$pubdocname"/>
      <xsl:text>.hhp</xsl:text>
    </xsl:variable>

    <xsl:variable name="urlchmindex">
      <xsl:value-of select="$pubdocdir"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$pubdoccode"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$pubdocname"/>
      <xsl:text>.hhk</xsl:text>
    </xsl:variable>

    <xsl:variable name="urlchmmap">
      <xsl:value-of select="$pubdocdir"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$pubdoccode"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$pubdocname"/>
      <xsl:text>.hhc</xsl:text>
    </xsl:variable>

    <xsl:variable name="urlchmheader">
      <xsl:value-of select="$pubdocdir"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$pubdoccode"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="translate($pubdocname, ' ', '_')"/>
      <xsl:text>.h</xsl:text>
    </xsl:variable>

    <xsl:variable name="defaulttopic">
      <xsl:apply-templates select="(html:body//html:div[@class='module'])[1]" mode="topiclink" />
    </xsl:variable>

    <out>
        <!-- generate project file -->
        <exsl:document href="{$urlchmproject}" method="text">
          <xsl:text>[OPTIONS]&#10;</xsl:text>
          <xsl:text>Auto Index=Yes&#10;</xsl:text>
          <xsl:text>Compatibility=1.1 or later&#10;</xsl:text>
          <xsl:text>Full-text search=Yes&#10;</xsl:text>
          <xsl:text>Default Window=chmwin&#10;</xsl:text>
          <xsl:text>Compiled file=</xsl:text>
          <xsl:value-of select="$profilename"/>
          <xsl:text>.chm&#10;</xsl:text>
          <xsl:text>Contents file=</xsl:text>
          <xsl:value-of select="$pubdocname"/>
          <xsl:text>.hhc&#10;</xsl:text>
          <xsl:text>Index file=</xsl:text>
          <xsl:value-of select="$pubdocname"/>
          <xsl:text>.hhk&#10;</xsl:text>
          <xsl:text>Default topic=</xsl:text>
          <xsl:value-of select="$defaulttopic" />
          <xsl:text>&#10;</xsl:text>
          <xsl:text>Language=</xsl:text>
          <xsl:value-of select="document($langfile)/languages/language[@code=$publang]/@value" />
          <xsl:text>&#10;</xsl:text>
          <xsl:text>Title=</xsl:text>
          <xsl:value-of select="$pubdocname" />
          <xsl:text>&#10;&#10;</xsl:text>

          <xsl:text>[WINDOWS]&#10;</xsl:text>
          <xsl:text>chmwin="</xsl:text>
          <xsl:value-of select="$pubdocname"/>
          <xsl:text>","</xsl:text>
          <xsl:value-of select="$pubdocname"/>
          <xsl:text>.hhc","</xsl:text>
          <xsl:value-of select="$pubdocname"/>
          <xsl:text>.hhk","</xsl:text>
          <xsl:value-of select="$defaulttopic"/>
          <xsl:text>","</xsl:text>
          <xsl:value-of select="$defaulttopic"/>
          <xsl:text>",,,,,0x20521,250,0x306e,,,,,,1,,0&#10;</xsl:text>
          <xsl:text>&#10;</xsl:text>

          <xsl:text>[FILES]&#10;</xsl:text>
          <xsl:apply-templates select="html:body//html:div[@class='module']" mode="chm_listtopicfiles"/>
	  <xsl:value-of select="translate($pubdocname, ' ', '_')"/>
          <xsl:text>.h&#10;</xsl:text>
	  <xsl:text>&#10;[ALIAS]&#10;</xsl:text>
	  <xsl:apply-templates select="html:body//html:div[@class='module']" mode="chm_aliastopics"/>
          <xsl:text>&#10;[MAP]&#10;</xsl:text>
	  <xsl:text>#include </xsl:text>
	  <xsl:value-of select="translate($pubdocname, ' ', '_')"/>
	  <xsl:text>.h&#10;</xsl:text>
        </exsl:document>

        <!-- generate project contents -->
        <exsl:document href="{$urlchmindex}" method="html">
          <html>
             <head>
                <meta name="GENERATOR" content="kolekti" />
             </head>
             <body>
                <ul>
                   <xsl:apply-templates select="html:body//html:span[@rel='index']|html:body//html:ins[@class='index']" mode="generate_index"/>
                </ul>
             </body>
          </html>
        </exsl:document>

        <!-- generate id map file -->
	<exsl:document href="{$urlchmmap}" encoding="{$encoding}" method="html">
          <html>
             <head>
                <meta name="GENERATOR" content="kolekti" />
             </head>
             <body>
                <ul>
                  <xsl:apply-templates select="html:body/html:div[@class='module' or @class='section']" mode="generate_map"/>
                </ul>
             </body>
          </html> 
        </exsl:document>

        <!-- Header file for contextual mapping-->
	<exsl:document href="{$urlchmheader}" method="text">
          <xsl:apply-templates select="html:body//html:div[@class='module']" mode="chm_mappings"/>
	</exsl:document>
    </out>
  </xsl:template>

  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="topiclink">
   <xsl:call-template name="topicid" />
  </xsl:template>

  <xsl:template match="html:div[@class='module']" mode="chm_listtopicfiles"> </xsl:template>

  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="chm_listtopicfiles">
    <xsl:variable name="filename">
      <xsl:call-template name="topicid" />
    </xsl:variable>

    <xsl:variable name="firsttopicfile">
      <xsl:call-template name="firsttopicfile">
         <xsl:with-param name="topicid" select="$filename" />
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="not(contains($firsttopicfile, '0'))">
        <xsl:value-of select="$filename" />
        <xsl:text>&#10;</xsl:text>
    </xsl:if>
  </xsl:template>
  
  <!-- mapping header file for contextual help-->
  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="chm_mappings">
    <xsl:variable name="filename">
      <xsl:call-template name="topicid" />
    </xsl:variable>

    <xsl:variable name="firsttopicfile">
      <xsl:call-template name="firsttopicfile">
         <xsl:with-param name="topicid" select="$filename" />
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="not(contains($firsttopicfile, '0'))">
      <xsl:text>#define IDH_</xsl:text>
      <xsl:value-of select="kepf:upper_case(substring-before($filename, '.html'))"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="substring-before(substring-after($filename, 'mod_'), '_')"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="chm_aliastopics">
    <xsl:variable name="filename">
      <xsl:call-template name="topicid" />
    </xsl:variable>

    <xsl:variable name="firsttopicfile">
      <xsl:call-template name="firsttopicfile">
         <xsl:with-param name="topicid" select="$filename" />
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="not(contains($firsttopicfile, '0'))">
        <xsl:text>IDH_</xsl:text>
        <xsl:value-of select="kepf:upper_case(substring-before($filename, '.html'))" />
	<xsl:text>=</xsl:text>
	<xsl:value-of select="$filename"/>
        <xsl:text>&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="html:span[@rel='index']|html:ins[@class='index']" mode="generate_index">
    <xsl:if test="generate-id() = generate-id(key('indexmarks', text())[1])">
        <li>
           <object type="text/sitemap">
              <param name="Name" value="{text()}" />
              <xsl:for-each select="key('indexmarks', text())">
                <xsl:variable name="localfile">
                   <xsl:apply-templates select="ancestor::html:div[@class='module'][1]" mode="topiclink" />
                </xsl:variable>
                <param name="Name" value="{substring-before($localfile, '.html')} Topic" />
                <param name="Local" value="{$localfile}" />
              </xsl:for-each>
           </object>
        </li>
    </xsl:if>
  </xsl:template>

  <xsl:template match="html:div[@class='section']" mode="generate_map">
    <xsl:variable name="name">
      <xsl:call-template name="normalizetext">
         <xsl:with-param name="text" select="child::html:*[1]/text()" />
      </xsl:call-template>
    </xsl:variable>
     <li>
        <object type="text/sitemap">
          <param name="Name" value="{$name}" />
          <param name="ImageNumber" value="5" />
        </object>
    </li>
     <ul>
      <xsl:apply-templates mode="generate_map" />
     </ul>
  </xsl:template>

  <xsl:template match="html:div[@class='module']" mode="generate_map"> </xsl:template>

  <xsl:template match="html:div[@class='module'][html:div[@class='moduleinfo']/following-sibling::html:*]" mode="generate_map">
    <xsl:variable name="localfile">
       <xsl:call-template name="topicid" />
    </xsl:variable>

    <xsl:variable name="name">
      <xsl:choose>
        <xsl:when test="html:*[starts-with(local-name(), 'h')][1]">
          <xsl:value-of select="html:*[starts-with(local-name(), 'h')][1]/text()" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="html:div[@class='moduleinfo']//html:p[html:span[@class='infolabel' and text()='topic_file']]/html:span[@class='infovalue']/text()" />            
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="normalizename">
      <xsl:call-template name="normalizetext">
         <xsl:with-param name="text" select="$name" />
      </xsl:call-template>
    </xsl:variable>

     <li>
      <object type="text/sitemap">
        <param name="Name" value="{$normalizename}" />
        <param name="Local" value="{$localfile}" />
        <param name="ImageNumber" value="11" />
      </object>
     </li>
  </xsl:template>
  
  <xsl:template match="text()" mode="generate_map"> </xsl:template>
  
  <xsl:template name="firsttopicfile">
    <xsl:param name="topicid" />
    
    <xsl:for-each select="preceding::html:div[@class='module']">
       <xsl:variable name="filename">
         <xsl:call-template name="topicid" />
       </xsl:variable>
       <xsl:choose>
         <xsl:when test="$filename = $topicid">
            <xsl:value-of select="0" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="1" />
         </xsl:otherwise>
       </xsl:choose>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="normalizetext">
   <xsl:param name="text" />
   <xsl:value-of select="normalize-space(translate($text, '&#xA0;', ''))" />
  </xsl:template> 

  <xsl:template name="topicid">
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

  <xsl:template name="gethelptitle">
    <xsl:value-of select="/html:html/html:head/html:title"/>
  </xsl:template>
</xsl:stylesheet>
