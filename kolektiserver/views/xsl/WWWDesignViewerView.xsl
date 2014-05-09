<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"
                xmlns:kt="kolekti:trames"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kf ke kcd kd kt">  

  <xsl:variable name="mime"><xsl:value-of select="kf:get_http_data('http', 'mime')" /></xsl:variable>

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <xsl:choose>
      <xsl:when test="starts-with($mime, 'application/vnd.oasis.opendocument')">
        <html>
          <head>
             <link type="text/css" rel="stylesheet" media="all" href="/_lib/app/css/viewers/kolekti-sheetsviewer.css" />
          </head>
          <body>
            <div class="sheetsviewer">
              <a href="{/kcd:view/kcd:http/@path}">
                <img src="/_lib/kolekti/mimetypes/{$mime}.png" i:alt="[0166]Cliquez ici pour ouvrir la ressource"
                  i:title="[0167]Ouvrir la ressource" />
              </a>
            </div>
          </body>
        </html> 
      </xsl:when> 
      <xsl:when test="starts-with(substring-after(/kcd:view/kcd:http/@path, 'design/edition/'),'trames_templates/')">
        <html>
          <head>
             <link type="text/css" rel="stylesheet" media="all" href="/_lib/kolekti/css/kolekti.css" />
             <link type="text/css" rel="stylesheet" media="all" href="/_lib/app/css/viewers/kolekti-sheetsviewer.css" />
             <link type="text/css" rel="stylesheet" media="all" href="/_lib/app/css/viewers/kolekti-trameeditor.css" />
          </head>
          <body>
            <div class="tramesheetsviewer">
               <xsl:apply-templates select="/kcd:view/kcd:data/kcd:namespace[@id='http']/kcd:value[@key='body']" />
            </div>
          </body>
        </html>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="kcd:data/kcd:namespace[@id='http']/kcd:value[@key='body']">
   <div class="tramesview">
     <p><i:text>[0168]Modèle de trame</i:text></p>
     <ul class="trame">
       <xsl:apply-templates select="kt:trame/kt:body" mode="trame" />
     </ul>
   </div>
  </xsl:template>

  <xsl:template match="kt:section" mode="trame">
   <li>
     <ul class="section">
        <li class="title"><xsl:value-of select="kt:title" /></li>
        <xsl:apply-templates select="kt:module|kt:section" mode="trame" />
     </ul>
   </li>
  </xsl:template>

  <xsl:template match="kt:module" mode="trame">
   <xsl:variable name="resid">
    <xsl:choose>
      <xsl:when test="starts-with(@resid, '@')">
         <xsl:value-of select="substring(@resid, 2)" />
       </xsl:when>
       <xsl:otherwise><xsl:value-of select="@resid" /></xsl:otherwise>
    </xsl:choose>
   </xsl:variable>
   <li class="module" title="{$resid}">
     <xsl:call-template name="modname">
       <xsl:with-param name="modpath" select="$resid" />
     </xsl:call-template>
   </li>
   <xsl:apply-templates select="kt:*" mode="trame" />
  </xsl:template>

  <xsl:template name="modname">
   <xsl:param name="modpath" />
   <xsl:choose>
      <xsl:when test="contains($modpath, '/')">
         <xsl:call-template name="modname">
            <xsl:with-param name="modpath" select="substring-after($modpath, '/')" />
         </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="$modpath" />
      </xsl:otherwise>
   </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
