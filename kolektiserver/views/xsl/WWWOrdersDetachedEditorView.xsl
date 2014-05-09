<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kol="http://www.exselt.com/kolekti"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"
                xmlns:dav="DAV:"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kol kf ke kcd kd dav">

  <xsl:import href="WWWOrdersEditorView.xsl"/>

  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />

  <xsl:template name="pagetitle">
   <xsl:value-of select="$project/@name" />
   <xsl:text> - </xsl:text>
   <xsl:variable name="order" select="substring-after(/kcd:view/kcd:http/@path, '/configuration/orders/')"></xsl:variable>
   <xsl:choose>
      <xsl:when test="$order = '_'">
         <i:text>[0171]Trame</i:text><xsl:text> </xsl:text>
         <xsl:value-of select="/kcd:view/kcd:http/kcd:params/kcd:param[@name='trame']/@content" />
      </xsl:when>
      <xsl:otherwise>
         <i:text>[0196]Lancement</i:text><xsl:text> </xsl:text>
         <xsl:value-of select="$order" />
      </xsl:otherwise>
   </xsl:choose>
  </xsl:template>

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:call-template name="pagetitle" /></title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <script type="text/javascript" src="/_lib/kolekti/scripts/guiders/guider.js">
         <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/scripts/jquery/css/ui-lightness/jquery-ui-1.8.14.custom.css" media="all" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="/_lib/kolekti/scripts/jquery/js/jquery-1.6.1.min.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>

        <script type="text/javascript" src="/_lib/kolekti/scripts/jquery/js/jquery-ui-1.8.14.custom.min.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
      </head>
      <body>
        <kd:guiders />
        <kd:resourceview id="confdetachedviewer">
          <kd:init uri="{/kcd:view/kcd:http/@path}" uri_hash="{/kcd:view/kcd:http/@uri_hash}" />
          <kd:use class="orderseditor">
            <kd:action ref="save_as" />
            <kd:action ref="publish" />
            <kd:action ref="publishwithmaster" />
            <kd:sidebar class="ordersidebar">
               <kd:property ns="kolekti:configuration" propname="versions" />
               <kd:property ns="kolekti:configuration" propname="notes" />
            </kd:sidebar>
          </kd:use>
        </kd:resourceview>
        <div id="ajax-indicator" style="display:none;">
          <span><i:text>[0103]Chargement...</i:text></span>
        </div>
      </body>
   </html>
  </xsl:template>
</xsl:stylesheet>
