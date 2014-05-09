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

  <xsl:variable name="modulestate"><xsl:value-of select="kf:get_http_data('kolekti', 'module')" /></xsl:variable>

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
   <html>
      <head>
         <script src="/_lib/kolekti/scripts/locale/{kf:getlocale()}/kolekti.js" type="text/javascript">
            <xsl:text>&#x0D;</xsl:text>
         </script>
         <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti.js">
            <xsl:text>&#x0D;</xsl:text>
         </script>
         <script type="text/javascript" src="/_lib/kolekti/scripts/ajax.js">
            <xsl:text>&#x0D;</xsl:text>
         </script>
         <script type="text/javascript" src="/_lib/kolekti/scripts/ajax-dav.js">
            <xsl:text>&#x0D;</xsl:text>
         </script>
         <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-resourceview.js">
            <xsl:text>&#x0D;</xsl:text>
         </script>
         <script type="text/javascript" src="/_lib/app/scripts/viewers/kolekti-moduleviewer.js">
            <xsl:text>&#x0D;</xsl:text>
         </script>
         <script type="text/javascript">
            var kviewer = new moduleviewer();
         </script>
         <link type="text/css" rel="stylesheet" media="all" href="/_lib/kolekti/css/kolekti-resourceview.css" />
         <link type="text/css" rel="stylesheet" media="all" href="/_lib/app/css/viewers/kolekti-moduleviewer.css" />
      </head>
      <body onload="kviewer.init_fixed();">
       <div class="modulesviewer">
         <xsl:choose>
            <xsl:when test="$modulestate = 'html'">
               <p><i:text>[0348]Le module contient des erreurs réparables</i:text></p>
               <p><i:text>[0349]Souhaitez-vous les corriger automatiquement?</i:text> <button id="fixed_btn"><i:text>[0350]Corriger</i:text></button></p>
            </xsl:when>
            <xsl:otherwise>
               <p><i:text>[0351]Le module contient des erreurs non réparables</i:text></p>
               <p><i:text>[0352]Veuillez les corriger manuellement</i:text></p>
            </xsl:otherwise>
         </xsl:choose>
         <textarea id="modcontent" style="display:none;">
            <xsl:copy-of select="." />
         </textarea>
       </div>
      </body>
   </html>
  </xsl:template>
</xsl:stylesheet>
