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
<?doc UI generation for svnrevision components
?>
<?author Stéphane Bonhomme <stephane@exselt.com>?>

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kd="kolekti:dialogs"
                xmlns:e="http://exslt.org/common"
                xmlns:d="DAV:"

                extension-element-prefixes="ke e"
                exclude-result-prefixes="i kf kd h e d">

  <!--  **********************  -->
  <!--  component svnrevision   -->
  <!--  **********************  -->

  <!-- Include personalize script and stylesheet -->
  <xsl:template match="kd:svnrevision" mode="include">
    <xsl:if test="@class">
      <xsl:if test="not(preceding::kd:svnrevision[@class=current()/@class])">
        <script type="text/javascript" src="/_lib/app/scripts/svnrevision/kolekti-{@class}.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/app/css/svnrevision/kolekti-{@class}.css" media="all" rel="stylesheet" type="text/css" />
      </xsl:if>
    </xsl:if>
    <xsl:apply-templates select="." mode="head"/>
  </xsl:template>

  <!--  **********************  -->
  <!--  svnrevision head part   -->
  <!--  **********************  -->

  <xsl:template match="kd:svnrevision" mode="head">
    <script type="text/javascript">
      <xsl:choose>
        <xsl:when test="@class">
          kolekti.svnrevision = new kolekti_<xsl:value-of select="@class"/>('svnrevision<xsl:value-of select="generate-id()" />');
        </xsl:when>
        <xsl:otherwise>
          kolekti.svnrevision = new kolekti_svnrevision('svnrevision<xsl:value-of select="generate-id()" />');
        </xsl:otherwise>
      </xsl:choose>
      kolekti.svnrevision.initevent();
    </script>
  </xsl:template>

  <!--  **********************  -->
  <!--  svnrevision body part   -->
  <!--  **********************  -->

  <xsl:template match="kd:svnrevision">
   <p id="svnrevision{generate-id()}" class="svnrevision">
      <i:text>[0342]Révision actuelle</i:text>
      <span class="revision">
         <xsl:value-of select="kf:get_svn_revision('', '1')/@number" />
      </span>
    </p>
  </xsl:template>
</xsl:stylesheet>
