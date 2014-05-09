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
<?doc UI generation for panelcontrol components
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
  <!--  component panelcontrol  -->
  <!--  **********************  -->

  <!-- Include personalize script and stylesheet -->
  <xsl:template match="kd:panelcontrol" mode="include">
    <xsl:if test="@class">
      <xsl:if test="not(preceding::kd:sidebar[@class=current()/@class])">
        <script type="text/javascript" src="/_lib/app/scripts/panels/kolekti-{@class}.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/app/css/panels/kolekti-{@class}.css" media="all" rel="stylesheet" type="text/css" />
      </xsl:if>
    </xsl:if>
    <xsl:apply-templates select="." mode="head"/>
  </xsl:template>

  <!--  **********************  -->
  <!--  panelcontrol head part  -->
  <!--  **********************  -->

  <xsl:template match="kd:panelcontrol" mode="head">
    <script type="text/javascript">
      <xsl:choose>
        <xsl:when test="@class">
          kolekti.panelcontrol = new kolekti_<xsl:value-of select="@class"/>();
        </xsl:when>
        <xsl:otherwise>
          kolekti.panelcontrol = new kolekti_panelcontrol();</xsl:otherwise>
      </xsl:choose>
      kolekti.panelcontrol.initevent();
    </script>
  </xsl:template>

  <!--  **********************  -->
  <!--  panelcontrol body part       -->
  <!--  **********************  -->

  <xsl:template match="kd:panelcontrol">
    <div id="panelcontrol">
      <ul>
         <xsl:apply-templates select="kd:panel" />
      </ul>
    </div>
  </xsl:template>

  <!--Add panel control -->
  <xsl:template match="kd:panelcontrol/kd:panel">
   <xsl:variable name="args">
      <xsl:text>{target:'</xsl:text><xsl:value-of select="@target" />
      <xsl:text>',id:'</xsl:text><xsl:value-of select="@id" /><xsl:text>'}</xsl:text>
   </xsl:variable>
   <li id="{@id}" onclick="kolekti.notify('panelcontrol-change',{$args})">
      <xsl:choose>
         <xsl:when test="kd:icons">
            <xsl:apply-templates />
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="." />
         </xsl:otherwise>
      </xsl:choose>
   </li>
  </xsl:template>

  <!-- Add icons -->
  <xsl:template match="kd:panelcontrol/kd:panel/kd:icons">
    <span class="activepanel">
      <img src="{kd:icon-on}" alt="{kd:icon-on}">
         <xsl:if test="kd:icon-on/@title or kd:icon-on/@i:title">
            <xsl:attribute name="title">
               <xsl:apply-templates select="kd:icon-on/@title|kd:icon-on/@i:title" mode="i18n" />
            </xsl:attribute>
         </xsl:if>
      </img>
    </span>
    <span>
      <img src="{kd:icon-off}" alt="{kd:icon-off}">
         <xsl:if test="kd:icon-off/@title or kd:icon-off/@i:title">
            <xsl:attribute name="title">
               <xsl:apply-templates select="kd:icon-off/@title|kd:icon-off/@i:title" mode="i18n" />
            </xsl:attribute>
         </xsl:if>
      </img>
    </span>
  </xsl:template>
</xsl:stylesheet>

