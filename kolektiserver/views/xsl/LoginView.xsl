<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"
                extension-element-prefixes="ke"
                exclude-result-prefixes="kf ke kcd kd">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <html>
      <head>
        <title>Kolekti</title>
        <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='auth']/kcd:value[@key='login']" />
      </head>
      <body>
        <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='auth']/kcd:value[@key='logout']" />
      </body>
    </html>
  </xsl:template>

  <xsl:template match="kcd:data"></xsl:template>

  <xsl:template match="kcd:value[@key='logout']">
    <kd:logout/>
  </xsl:template>

  <xsl:template match="kcd:value[@key='login']">
    <!-- Redirect user to either first project, or previous page if no mroject for this user   -->
   <meta http-equiv="refresh" content="0;url={/kcd:view/kcd:http/kcd:headers/kcd:header[@name='Referer']/@content}"/>
  </xsl:template>

</xsl:stylesheet>
