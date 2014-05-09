<?xml version="1.0" encoding="utf-8"?>
<!--

     kOLEKTi : a structural documentation generator
     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

-->
<?doc UI generation for upload dialogs in action components?>
<?author Guillaume Faucheur <guillaume@exselt.com>?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kd="kolekti:dialogs"
                xmlns:e="http://exslt.org/common"
                extension-element-prefixes="ke e"
                exclude-result-prefixes="i kf kd h e">

  <!--  **********************  -->
  <!--  upload dialog component -->
  <!--  **********************  -->

  <xsl:template match="kd:upload-form" mode="include">
    <xsl:if test="@class">
      <xsl:if test="not(preceding::kd:upload-form[@class=current()/@class])">
   <script type="text/javascript" src="/_lib/app/scripts/forms/kolekti-{@class}.js">
     <xsl:text>&#x0D;</xsl:text>
   </script>
   <link href="/_lib/app/css/forms/kolekti-{@class}.css" media="all" rel="stylesheet" type="text/css" />
      </xsl:if>
    </xsl:if>
    <xsl:apply-templates select="." mode="head"/>
  </xsl:template>

  <xsl:template match="kd:upload-form" mode="head">
    <xsl:variable name="id" select="@id"/>
    <xsl:variable name="class">
      <xsl:choose>
   <xsl:when test="@class">kolekti_<xsl:value-of select="@class"/></xsl:when>
   <xsl:otherwise>kolekti_uploadform</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <script type="text/javascript">
      var uploadform_<xsl:value-of select="@id"/>= new <xsl:value-of select="$class"/>('<xsl:value-of select="kf:selfpath()" />','<xsl:value-of select="@id"/>');
      <xsl:if test="kd:upload[@multiple='1' or @multiple='yes']">
        uploadform_<xsl:value-of select="@id"/>.multiple=1;
      </xsl:if>
      uploadform_<xsl:value-of select="@id"/>.initevent();
    </script>
  </xsl:template>

  <xsl:template match="/kd:action/kd:dialog//kd:upload-form">
      <xsl:variable name="params"><xsl:apply-templates select="kd:param" /></xsl:variable>
      <xsl:variable name="srcform">
         <xsl:choose>
            <xsl:when test="@form"><xsl:value-of select="@form" /></xsl:when>
            <xsl:otherwise><xsl:value-of select="kf:selfpath()" /></xsl:otherwise>
         </xsl:choose>
         <xsl:text>?uploadform=1</xsl:text>
         <xsl:if test="kd:param">
            <xsl:text>&#38;</xsl:text><xsl:value-of select="substring($params, 1, string-length($params)-1)" />
         </xsl:if>
      </xsl:variable>

      <iframe id="iframeupload_{../../@id}" src="{$srcform}" style="border: 0; width: 100%;">
        <xsl:text>&#xA0;</xsl:text>
      </iframe>
  </xsl:template>

  <xsl:template match="kd:upload-form/kd:param">
   <xsl:value-of select="@name" />=<xsl:value-of select="@content" /><xsl:text>&#38;</xsl:text>
  </xsl:template>

  <xsl:template match="kd:upload-select-dialog">
    <div class="uploadform">
      <xsl:apply-templates select="kd:upload-form" />
    </div>
    <div class="uploadbrowser">
      <xsl:apply-templates select="kd:ajaxbrowser" />
    </div>
  </xsl:template>

  <xsl:template match="kd:upload-form">
    <form id="{@id}" action="{@action}" enctype="multipart/form-data" method="post">
      <xsl:apply-templates/>
      <p class="btn_submit"><input type="submit" name="upload" i:value="[0141]Transférer" /></p>
    </form>
  </xsl:template>

  <xsl:template match="kd:upload-form/kd:upload">
    <div id="filelines">
      <p>
        <label ref="file" class="fieldtitle">
         <xsl:comment>Label value</xsl:comment>
         <xsl:apply-templates select="@label|@i:label" mode="i18n" />
        </label>
        <input type="file" value="" name="file"/>
      </p>
    </div>
  </xsl:template>

  <xsl:template match="kd:upload-form/kd:input">
   <xsl:variable name="id">
      <xsl:choose>
         <xsl:when test="@id"><xsl:value-of select="@id" /></xsl:when>
         <xsl:otherwise><xsl:value-of select="@name" /></xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <p>
      <label ref="{@name}" class="fieldtitle">
         <xsl:comment>Label value</xsl:comment>
         <xsl:apply-templates select="@label|@i:label" mode="i18n" />
      </label>
      <input type="text" value="" name="{@name}" id="{$id}"/>
    </p>
  </xsl:template>
</xsl:stylesheet>
