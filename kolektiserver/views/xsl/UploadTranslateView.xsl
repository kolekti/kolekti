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

  <xsl:variable name="file" select="kcd:view/kcd:http/kcd:params/kcd:param[@name='file']/@content" />
  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />

  <xsl:template match="/">
    <html>
      <head>
        <title>upload form</title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/kolekti/css/kolekti-admin.css" media="all" rel="stylesheet" type="text/css" />
        <xsl:if test="$file">
          <link href="/_lib/app/css/forms/kolekti-uploadtranslateform.css" media="all" rel="stylesheet" type="text/css"/>
          <script type="text/javascript" src="/_lib/kolekti/scripts/locale/{kf:getlocale()}/kolekti.js">
            <xsl:text>&#x0D;</xsl:text>
          </script>
          <script type="text/javascript" src="/_lib/kolekti/scripts/ajax.js">
            <xsl:text>&#x0D;</xsl:text>
          </script>
          <script type="text/javascript" src="/_lib/kolekti/scripts/ajax-dav.js">
            <xsl:text>&#x0D;</xsl:text>
          </script>
          <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-uploadform.js">
            <xsl:text>&#x0D;</xsl:text>
          </script>
          <script type="text/javascript" src="/_lib/app/scripts/forms/kolekti-uploadtranslateform.js">
            <xsl:text>&#x0D;</xsl:text>
          </script>
          <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti.js">
            <xsl:text>&#x0D;</xsl:text>
          </script>
          <script type="text/javascript">
            var uploadform_translateform= new kolekti_uploadtranslateform('<xsl:value-of select="kcd:view/kcd:http/@path" />','translateform', '<xsl:value-of select="$project/@directory" />');
          </script>
        </xsl:if>
      </head>
      <body style="min-width: 0;">
        <xsl:attribute name="onload">
          <xsl:choose>
            <xsl:when test="$file">javascript:uploadform_translateform.publish('<xsl:value-of select="$file" />');</xsl:when>
            <xsl:otherwise>javascript:kolekti.notify('load', null, null);</xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="$file">
            <div id="publish_dialog"><xsl:comment>publish results</xsl:comment></div>
          </xsl:when>
          <xsl:otherwise>
            <kd:upload-form action="{kcd:view/kcd:http/@path}" id="translateform" class="uploadtranslateform">
              <kd:upload i:label="[0301]Enveloppe"/>
            </kd:upload-form>
          </xsl:otherwise>
        </xsl:choose>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
