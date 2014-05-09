<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:d="DAV:"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kf ke kcd d">

  <xsl:output method="xml" indent="yes"/>
  <xsl:variable name="url" select="/kcd:view/kcd:http/@url"/>
  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')/@directory" />

  <xsl:template name="pagetitle">kOLEKTi</xsl:template>

  <xsl:template match="/">
    <html>
      <head>
   <title><xsl:call-template name="pagetitle"/></title>
   <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
   <meta name="description" content="kOLEKTi" />
   <meta name="kolekti.project" content="{$project}" />
   <meta name="keywords" content="custom documents generator" />
   <link href="/_lib/kolekti/css/application.css" media="all" rel="stylesheet" type="text/css" />
   <link href="/_lib/app/css/browsers/kolekti-browser-amaya.css" media="all" rel="stylesheet" type="text/css" />
      </head>
      <body>
   <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='http']/kcd:value[@key='body']"/>
   <div id="footer">
      <i:text>[0133]Propulsé par</i:text> <a href="http://www.kolekti.org/">kOLEKTi </a> <!-- <ke:version/>--> © 2007-2009 Stéphane Bonhomme - Vincent Bidaux
   </div>
      </body>
    </html>
  </xsl:template>

  <!-- Display Collection content --> 
  <xsl:template match="kcd:collection">
    <div id="main-browser">
      <xsl:value-of select="$url" />
      <table border="0">
   <tbody>
     <tr class="browser title">
       <th class="name"><i:text>[0079]Nom</i:text></th>
       <th><i:text>[0134]Date de modification</i:text></th>
       <th><i:text>[0135]Date de création</i:text></th>
       <th><i:text>[0136]Taille</i:text></th>
       <th><i:text>[0137]Verrou</i:text></th>
     </tr>
     <xsl:if test="not($project = '')">
       <tr class="browser">
         <td>
      <a href="/projects">
        <img src="/_lib/kolekti/icons/dir.png" i:alt="[0138]dir" />
        <i:text>[0113]Projet</i:text> <xsl:value-of select="$project"/>
      </a>
         </td>
       </tr>
       <tr class="browser">
         <td>
      <a href="..">
        <img src="/_lib/kolekti/icons/dir.png" i:alt="[0138]dir" />
        <i:text>[0139]Répertoire parent</i:text>
      </a>
         </td>
       </tr>
     </xsl:if>
     <xsl:apply-templates select="kcd:element">
       <xsl:sort select=".//d:getcontenttype"/>
       <xsl:sort select=".//d:displayname"/>
     </xsl:apply-templates>
   </tbody>
      </table>
    </div>
  </xsl:template>
  
  <xsl:template match="kcd:element">
    <tr class="browser">
      <td class="name">
   <xsl:choose>
     <xsl:when test=".//d:getcontenttype = ''">
       <xsl:call-template name="dir">
         <xsl:with-param name="label" select=".//d:displayname" />
       </xsl:call-template>
     </xsl:when>
     <xsl:otherwise>
       <xsl:call-template name="file">
         <xsl:with-param name="label" select=".//d:displayname" />
         <xsl:with-param name="type" select=".//d:getcontenttype" />
       </xsl:call-template>
     </xsl:otherwise>
   </xsl:choose>
      </td>
      <td><xsl:value-of select=".//d:getlastmodified"/></td>
      <td><xsl:value-of select=".//d:creationdate"/></td>
      <td><xsl:value-of select=".//d:getcontentlength"/></td>
      <td><xsl:value-of select=".//d:lockdiscovery"/></td>
    </tr>
  </xsl:template>

  <xsl:template name="dir">
    <xsl:param name="label" />
    <a href="{@url}/">
      <img src="/_lib/kolekti/icons/dir.png" i:alt="[0138]dir" /><xsl:value-of select="$label"/>
    </a>
  </xsl:template>

  <xsl:template name="file">
    <xsl:param name="label" />
    <xsl:param name="type" />
    <a href="{@url}">
      <xsl:choose>
   <xsl:when test="starts-with($type,'image/')">
     <img src="/_lib/kolekti/icons/o_world.png" i:alt="[0140]file" />
   </xsl:when>
   <xsl:otherwise>
     <img src="/_lib/kolekti/icons/file.png" i:alt="[0140]file" />
   </xsl:otherwise>
      </xsl:choose>
      <xsl:value-of select="$label"/>
    </a>
  </xsl:template>
</xsl:stylesheet>
