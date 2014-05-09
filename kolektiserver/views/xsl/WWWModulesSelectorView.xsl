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

  <xsl:import href="WWWModulesView.xsl"/>

  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="currenttab">modules</xsl:variable>

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
      <body>
        <xsl:apply-templates />
        <div id="ajax-indicator" style="display:none;">
          <span><i:text>[0103]Chargement...</i:text></span>
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="kcd:view">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="kcd:data">
    <div class="" id="main" style="top: 0;">
      <div id="content">
        <div id="splitcontentleft">
          <xsl:call-template name="mainleft" />
        </div>
        <div id="splitcontentright">
          <xsl:call-template name="mainright" />
        </div>
      </div>
    </div>
  </xsl:template>

  <xsl:template name="mainleft">
   <kd:ajaxbrowser id="modulesbrowser" class="selectmodulesbrowser">
      <kd:behavior>
        <kd:click id="previewmodule" action="notify" event="module-preview" />
      </kd:behavior>
      <kd:tab i:label="[0152]Explorateur" dir="{$projectdir}/modules" id="modules" />
    </kd:ajaxbrowser>
  </xsl:template>
  
  <xsl:template name="mainright">
   <div id="module-preview" style="display: none;">
      <p id="module-preview-content"><xsl:comment>preview content</xsl:comment></p>
      <p id="module-preview-content-select">
         <button onclick="kolekti.notify('module-select',null,null)"><i:text>[0174]Sélectionner</i:text></button>
      </p>
   </div>
  </xsl:template>
</xsl:stylesheet>
