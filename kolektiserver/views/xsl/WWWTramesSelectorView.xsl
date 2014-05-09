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

  <xsl:output method="xml" indent="yes" />

  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />
  <xsl:variable name="projectdir">/projects/<xsl:value-of select="$project/@directory" /></xsl:variable>

  <xsl:template name="pagetitle"><xsl:value-of select="$project/@name" /></xsl:template>

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:call-template name="pagetitle" /></title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="kolekti.project" content="{$project}" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/kolekti/css/kolekti-browser.css" media="all" rel="stylesheet" type="text/css" />
      </head>
      <body>
        <xsl:apply-templates />
        <div id="ajax-indicator" style="display:none;"><span><i:text>[0103]Chargement...</i:text></span></div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="kcd:view">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="kcd:data">
    <div class="trameselector_dialog" id="main">
      <div class="splitcontentleft">
        <kd:ajaxbrowser id="tramesbrowser" class="selecttramesbrowser" keep_active_items="false">
          <kd:behavior>
            <kd:click id="selectitem" action="notify" event="select-item" />
          </kd:behavior>
          <kd:tab i:label="[0152]Explorateur" dir="{$projectdir}/trames" id="trames" />
        </kd:ajaxbrowser>
      </div>
    </div>
  </xsl:template>
</xsl:stylesheet>
