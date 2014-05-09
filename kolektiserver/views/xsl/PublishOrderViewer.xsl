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

  <xsl:template name="pagetitle">Kolekti</xsl:template>

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:call-template name="pagetitle" /></title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link type="text/css" rel="stylesheet" media="all" href="/_lib/app/css/viewers/kolekti-publishorderviewer.css" />
      </head>
      <body>
         <div class="publishorderviewer">
            <xsl:if test="kf:get_params_value('master') = '1'">
               <div class="masterpublishparams">
                  <p>
                     <label ref="mastername"><i:text>[0243]Nom de l'enveloppe</i:text></label>
                     <input type="text" name="mastername" id="mastername" />
                  </p>
                  <p>
                     <span class="formselect">
                        <input type="checkbox" name="enabled" id="enabled{generate-id()}"/>
                        <label ref="enabled{generate-id()}"><i:text>[0334]Filtre</i:text></label>
                     </span>
                     <span class="formvalue" style="display: none;">
                        <input type="text" name="filtermaster" id="filtermaster" />
                        <xsl:variable name="masterfilters" select="kf:getmasterfilters()" />
                        <xsl:if test="count($masterfilters) &gt; 0">
	                        <label ref="copyfilter"><i:text>[0195]Copier</i:text></label>
	                        <select name="copyfilter" id="copyfilter">
	                           <xsl:for-each select="$masterfilters">
	                              <option value="{@value}"><xsl:value-of select="@value" /></option>
	                           </xsl:for-each>
	                           <xsl:comment>list of possible conditions</xsl:comment>
	                        </select>
	                        <button class="copyfilter">ok</button>
                        </xsl:if>
                     </span>
                  </p>
                  <p class="submitform">
                     <button><i:text>[0335]Publier et créer l'enveloppe</i:text></button>
                  </p>
               </div>
               <hr />
            </xsl:if>
            <div class="publisher">
            <xsl:comment>list of logs</xsl:comment>
            </div>
         </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>