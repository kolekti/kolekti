<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kf ke kcd kd">

  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />
  <xsl:template name="pagetitle"><xsl:value-of select="$project/@name" /></xsl:template>

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:call-template name="pagetitle" /></title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="kolekti.project" content="{$project/@directory}" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/viewers/kolekti-masterviewer.css" media="all" rel="stylesheet" type="text/css" />
      </head>
      <body style="min-width: 0;">
        <div id="content">
         <h3><i:text>[0169]Détails de l'enveloppe</i:text></h3>
         <div class="details">
           <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='master']/kcd:value[@key='lang']" />
           <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='master']/kcd:value[@key='config']" />
         </div>
         <div id="dialog_{/kcd:view/kcd:http/@uri_hash}">
            <div class="publication_log"><xsl:text>&#x0D;</xsl:text></div>
            <div class="publication_result"><xsl:text>&#x0D;</xsl:text></div>
         </div>
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='master']/kcd:value[@key='lang']">
   <div class="lang">
      <p><span class="label"><i:text>[0170]Langue</i:text>:</span><xsl:value-of select="lang/@value" /></p>
   </div>
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='master']/kcd:value[@key='config']">
   <div class="config">
      <p><span class="label"><i:text>[0171]Trame</i:text>:</span><xsl:value-of select="substring-after(data/field[@name='trame']/@value, 'trames/')" /></p>
      <p><span class="label"><i:text>[0144]Répertoire de publication</i:text>:</span><xsl:value-of select="data/field[@name='pubdir']/@value" /></p>
      <p><span class="label"><i:text>[0172]Auteur</i:text>:</span><xsl:value-of select="data/field[@name='author']/@value" /></p>
      <p><span class="label"><i:text>[0135]Date de création</i:text>:</span><xsl:value-of select="kf:format_time(string(data/field[@name='creation_date']/@value))" /></p>
      <xsl:if test="not(data/field[@name='filtermaster']/@value = '0' or data/field[@name='filtermaster']/@value = '')">
         <p><span class="label"><i:text>[0334]Filtre</i:text>:</span><xsl:value-of select="data/field[@name='filtermaster']/@value" /></p>
      </xsl:if>
      <div class="listprofiles">
         <p class="label"><i:text>[0173]Liste des profiles</i:text></p>
         <ul>
            <xsl:apply-templates select="data/profiles/profile" />
         </ul>
      </div>
      <div class="listscripts">
         <p class="label"><i:text>[0336]Liste des sorties</i:text></p>
         <ul>
            <xsl:apply-templates select="data/scripts/script" />
         </ul>
      </div>
   </div>
  </xsl:template>

  <xsl:template match="data/profiles/profile">
   <li>
      <p><xsl:value-of select="label" /></p>
      <ul>
         <xsl:apply-templates select="criterias/criteria[@checked='1']" />
      </ul>
   </li>
  </xsl:template>

  <xsl:template match="data/profiles/profile/criterias/criteria[@checked='1']">
   <li><xsl:value-of select="@code" /><xsl:text> = </xsl:text><xsl:value-of select="@value" /></li>
  </xsl:template>

  <xsl:template match="data/scripts/script">
   <li>
      <p><xsl:value-of select="@name" /></p>
      <ul>
         <xsl:if test="suffix/@enabled = '1'">
            <li><i:text>[0332]Suffixe</i:text><xsl:text> = </xsl:text><xsl:value-of select="suffix" /></li>
         </xsl:if>
         <xsl:apply-templates select="parameters/parameter" />
      </ul>
   </li>
  </xsl:template>

  <xsl:template match="data/scripts/script/parameters/parameter">
   <li><xsl:value-of select="@name" /><xsl:text> = </xsl:text><xsl:value-of select="@value" /></li>
  </xsl:template>
</xsl:stylesheet>
