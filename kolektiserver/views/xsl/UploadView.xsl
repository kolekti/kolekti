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

  <xsl:template name="pagetitle"><xsl:value-of select="kf:get_http_data('kolekti', 'project')/@name" /></xsl:template>

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:call-template name="pagetitle" /></title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
      </head>
      <body style="min-width: 0;">
        <xsl:copy-of select="kcd:view/kcd:data/kcd:namespace[@id='http']/kcd:value[@key='body']/*"/>
        <div id="ajax-indicator" style="display:none;">
          <span><i:text>[0103]Chargement...</i:text></span>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
