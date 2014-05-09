<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i h kf ke kcd kd">

  <xsl:variable name="mime"><xsl:value-of select="kf:get_http_data('http', 'mime')" /></xsl:variable>

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <xsl:choose>
      <xsl:when test="starts-with($mime, 'application/vnd.oasis.opendocument')">
        <xsl:variable name="mimeicon" select="concat('gnome-mime-application-',substring-after($mime, 'application/'))" />
        <html>
          <head>
             <link type="text/css" rel="stylesheet" media="all" href="/_lib/app/css/viewers/kolekti-sheetsviewer.css" />
          </head>
          <body>
            <div class="sheetsviewer">
              <a href="{/kcd:view/kcd:http/@path}">
                <img src="/_lib/kolekti/icons/mimetypes/{$mimeicon}.png" alt="" i:title="[0237]Cliquez ici pour télécharger la ressource" />
                <span><i:text>[0238]Télécharger la ressource</i:text></span>
              </a>
            </div>
          </body>
        </html>
      </xsl:when>
      <xsl:when test="substring-after($mime, '/') = 'xml'">
        <html>
          <head>
             <link type="text/css" rel="stylesheet" media="all" href="/_lib/app/css/viewers/kolekti-sheetsviewer.css" />
          </head>
          <body>
            <div class="sheetsviewer">
              <xsl:apply-templates select="/kcd:view/kcd:data/kcd:namespace['http']/kcd:value[@key='body']"/>
            </div>
          </body>
        </html>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="kcd:data/kcd:namespace['http']/kcd:value[@key='body']">
   <table>
     <tbody>
      <xsl:apply-templates select="h:variables/h:critlist" />
      <xsl:apply-templates select="h:variables/h:variable" />
     </tbody>
   </table>
  </xsl:template>

  <xsl:template match="h:critlist">
   <xsl:choose>
      <xsl:when test="h:crit">
         <xsl:apply-templates select="h:crit" mode="header"/> 
      </xsl:when>
      <xsl:otherwise>
       <xsl:call-template name="crit">
         <xsl:with-param name="val" select="substring-after(.,':')" />
       </xsl:call-template>
      </xsl:otherwise>   
   </xsl:choose>
  </xsl:template>

  <xsl:template name="crit">
   <xsl:param name="val" />
   <tr class="tabheader">
   <xsl:choose>
     <xsl:when test="contains($val, ':')">     
       <xsl:call-template name="valcrit">
         <xsl:with-param name="val" select="substring-before($val, ':')" />
       </xsl:call-template>
       <xsl:call-template name="crit">
         <xsl:with-param name="val" select="substring-after($val, ':')" />
       </xsl:call-template>
     </xsl:when>
     <xsl:otherwise>
       <xsl:call-template name="valcrit">
         <xsl:with-param name="val" select="$val" />
       </xsl:call-template>
     </xsl:otherwise>
   </xsl:choose>
   </tr>
  </xsl:template>

  <xsl:template name="valcrit">
   <xsl:param name="val" />
   <td><xsl:text>:</xsl:text><xsl:value-of select="$val" /></td>
   <xsl:for-each select="../h:variable[1]/h:value/h:crit[@name=$val]">
      <td><xsl:value-of select="@value" /></td>
   </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="h:crit" mode="header">
   <tr class="tabheader">
     <td><xsl:text>:</xsl:text><xsl:value-of select="@name" /></td>
     <xsl:for-each select="../../h:variable[1]/h:value/h:crit[@name=current()/@name]">
       <td><xsl:value-of select="@value" /></td>
     </xsl:for-each>
   </tr>
  </xsl:template>

  <xsl:template match="h:variable">
   <tr>
      <td><xsl:text>&#38;</xsl:text><xsl:value-of select="@code" /></td>
      <xsl:apply-templates />
   </tr>
  </xsl:template>

  <xsl:template match="h:value">
   <td><xsl:apply-templates select="h:content" /></td>
  </xsl:template>

</xsl:stylesheet>
