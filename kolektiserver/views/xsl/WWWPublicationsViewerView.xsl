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
        <link href="/_lib/app/css/viewers/kolekti-publicationviewer.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/kolekti/scripts/jquery/css/ui-lightness/jquery-ui-1.8.14.custom.css" media="all" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="/_lib/kolekti/scripts/jquery/js/jquery-1.6.1.min.js">
         <xsl:text>&#x0D;</xsl:text>
        </script>
        <script type="text/javascript" src="/_lib/kolekti/scripts/jquery/js/jquery-ui-1.8.14.custom.min.js">
         <xsl:text>&#x0D;</xsl:text>
        </script>
        <script src="/_lib/kolekti/scripts/kolekti-resourceview.js" type="text/javascript">
         <xsl:text>&#x0D;</xsl:text>
        </script>
        <script src="/_lib/app/scripts/viewers/kolekti-publicationviewer.js" type="text/javascript">
         <xsl:text>&#x0D;</xsl:text>
        </script>
        <script type="text/javascript">
         var kpublication = new publicationviewer();
        </script>
      </head>
      <body style="min-width: 0;" onload="kpublication.init_view(window.document);">
        <div id="content">
          <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='publication']/kcd:value[@key='infos']" />
          <div id="links">
            <p><span class="label"><i:text>[0230]Télécharger</i:text></span></p>
            <ul><xsl:text>&#x0D;</xsl:text></ul>
           </div>
          <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='publication']/kcd:value[@key='logs']" />
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='publication']/kcd:value[@key='infos']">
   <xsl:variable name="lang" select="/kcd:view/kcd:data/kcd:namespace[@id='publication']/kcd:value[@key='lang']" />
   <xsl:variable name="pubpath" select="concat(/kcd:view/kcd:http/@path, '/', $lang, '/', publication/@time)" />
   <div id="infos">
      <p><span class="label"><i:text>[0231]Date de publication</i:text>:</span><xsl:value-of select="kf:format_time(string(publication/@time))" /></p>
      <p><span class="label"><i:text>[0170]Langue</i:text>:</span><xsl:value-of select="$lang" /></p>
      <p><span class="label"><i:text>[0171]Trame</i:text>:</span><xsl:value-of select="substring-after(kf:normalize_id(string(publication/@trame)), '/trames/')" /></p>
      <p><span class="label"><i:text>[0172]Auteur</i:text>:</span><xsl:value-of select="publication/@author" /></p>
      <p><span class="label"><i:text>[0224]Pivot</i:text>:</span><a href="{concat($pubpath, '/', '_pivots', '/', publication/@pivname, '?viewer=publicationspivotviewer')}}"><xsl:comment>pivname</xsl:comment><xsl:value-of select="publication/@pivname" /></a></p>
      <p><span class="label"><i:text>[0341]CSV des révisions</i:text>:</span><a href="{concat($pubpath, '/modules-history.csv')}}">modules-history.csv</a></p>
   </div>
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='publication']/kcd:value[@key='logs']">
   <div id="logs">
      <div class="section">
         <span class="ui-icon ui-icon-plusthick"><xsl:text>&#x0D;</xsl:text></span>
         <span class="title"><i:text>[0232]Détails de la publication</i:text></span>
      </div>
      <div style="display: none;">
         <xsl:copy-of select="logs/div[@class='profile']/div[@class='result']" />
      </div>
   </div>
  </xsl:template>
</xsl:stylesheet>
