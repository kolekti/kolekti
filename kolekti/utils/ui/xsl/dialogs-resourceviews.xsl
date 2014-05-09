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
<?doc UI generation for resource viewers?>
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

  <xsl:template match="kd:resourceview" mode="include">
    <xsl:if test="@class">
      <xsl:if test="not(preceding::kd:resourceview[@class=current()/@class])">
        <script type="text/javascript" src="/_lib/app/scripts/viewers/kolekti-{@class}.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/app/css/viewers/{@class}.css" media="all" rel="stylesheet" type="text/css" />
      </xsl:if>
    </xsl:if>
    <xsl:apply-templates select="kd:use|kd:import" mode="include"/>
    <xsl:apply-templates select=".//kd:action" mode="include"/>
    <xsl:apply-templates select="." mode="head"/>
  </xsl:template>

  <xsl:template match="kd:resourceview/kd:use|kd:resourceview/kd:import" mode="include">
    <xsl:if test="not(preceding::kd:resourceview/kd:use[@class=current()/@class] or preceding::kd:resourceview/kd:import[@class=current()/@class])">
      <script type="text/javascript" src="/_lib/app/scripts/viewers/kolekti-{@class}.js">
        <xsl:text>&#x0D;</xsl:text>
      </script>
      <link href="/_lib/app/css/viewers/kolekti-{@class}.css" media="all" rel="stylesheet" type="text/css" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="kd:resourceview//kd:sidebar" mode="include">
    <xsl:if test="@class">
      <xsl:if test="not(preceding::kd:sidebar[@class=current()/@class])">
        <script type="text/javascript" src="/_lib/app/scripts/sidebars/kolekti-{@class}.js">
           <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/app/css/sidebars/kolekti-{@class}.css" media="all" rel="stylesheet" type="text/css" />
      </xsl:if>
    </xsl:if>
  </xsl:template>


  <!--  **********************  -->
  <!--  component resourceview  -->
  <!--  **********************  -->
  <!--  **********************  -->
  <!--  resourceview head part  -->
  <!--  **********************  -->

  <xsl:template match="kd:resourceview" mode="head">
    <xsl:variable name="id" select="@id"/>
    <xsl:variable name="class">
      <xsl:choose>
        <xsl:when test="@class"><xsl:value-of select="@class"/></xsl:when>
        <xsl:otherwise>kolekti_resview</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <script type="text/javascript">
      var resview_<xsl:value-of select="@id"/>= new <xsl:value-of select="$class"/>('<xsl:value-of select="@id"/>');
      if(typeof(resview_<xsl:value-of select="@id"/>.initevent) == "function")
        resview_<xsl:value-of select="@id"/>.initevent();

      resview_<xsl:value-of select="@id"/>.base='<xsl:value-of select="concat(.,'/')"/>';

      var initf=resview_<xsl:value-of select="@id"/>.init();
      addEventListener('load',initf,false);

      <xsl:variable name="tabs" select="kf:get_session_value(concat('/',@id))"/>

      <xsl:for-each select="e:node-set($tabs)">
         <xsl:variable name="taburl" select="substring-before(text(),'?')"/>
         <xsl:if test="starts-with($taburl, concat('/projects/',kf:get_http_data('kolekti', 'project')/@directory,'/'))">
            <xsl:variable name="tab" select="@id"/>
            <xsl:variable name="tabversion" select="substring-after(text(), 'version=')"/>
            resview_<xsl:value-of select="$id"/>.addinitopen('<xsl:value-of select="$taburl"/>','<xsl:value-of select="$tab"/>','<xsl:value-of select="$tabversion"/>');
         </xsl:if>
      </xsl:for-each>
   <xsl:for-each select="kd:init">
      resview_<xsl:value-of select="$id"/>.addinitopen('<xsl:value-of select="@uri"/>','<xsl:value-of select="@uri_hash"/>','<xsl:value-of select="@version"/>');
   </xsl:for-each>

      <xsl:variable name="open" select="kf:get_params_value('open')"/>
      <xsl:if test="$open">
         <xsl:variable name="taburl" select="kf:urlquote(concat(kf:selfpath(), '/', $open))"/>
         <xsl:if test="starts-with($taburl, kf:urlquote(concat('/projects/',kf:get_http_data('kolekti', 'project')/@directory,'/')))">
            <xsl:variable name="tab" select="kf:selfhashuri($taburl)"/>
            <xsl:variable name="tabversion" select="0"/>
            resview_<xsl:value-of select="$id"/>.addinitopen('<xsl:value-of select="$taburl"/>','<xsl:value-of select="$tab"/>','<xsl:value-of select="$tabversion"/>');
         </xsl:if>
      </xsl:if>

      <xsl:value-of select="$class"/>.prototype.getViewer = function(viewer, id) {
      var v,tmpobj;
      <xsl:for-each select="kd:use">
        if (viewer=='<xsl:value-of select="@class"/>') {
          v = new <xsl:value-of select="@class"/>();
          v.actions=new Array();
          <xsl:for-each select="kd:action">
            tmpobj=new Object();
            <xsl:if test="@shortname">
              tmpobj.shortname='<xsl:apply-template select="@shortname|@i:shortname" mode="i18n"/>';
            </xsl:if>
            v.actions['<xsl:value-of select="@ref"/>']=tmpobj;
            <xsl:apply-templates select="document(concat($kolektiapp,'/ui/actions/',@ref,'.xml'))" mode="resviewaction"/> 
       </xsl:for-each>
    <xsl:if test="kd:sidebar">
     <xsl:call-template name="initsidebar">
       <xsl:with-param name="sidebar" select="kd:sidebar" />
       <xsl:with-param name="obj">resview_<xsl:value-of select="$id"/></xsl:with-param>
     </xsl:call-template>
    </xsl:if>
        return v;
        }
      </xsl:for-each>
      }
    </script>
  </xsl:template>

  <xsl:template match="/kd:action" mode="resviewaction">
    <xsl:if test="kd:icon">
      tmpobj.icon='<xsl:value-of select="kd:icon"/>';
    </xsl:if>
    <xsl:apply-templates select="@*|@i:*" mode="resviewaction"/>
  </xsl:template>

  <xsl:template match="/kd:action/@*|/kd:action/@i:*" mode="resviewaction">
    tmpobj.<xsl:value-of select="local-name()"/>='<xsl:apply-templates select="." mode="i18n" />';
  </xsl:template>

  <!--  **********************  -->
  <!--  resourceview body part  -->
  <!--  **********************  -->

  <xsl:template match="kd:resourceview">
    <div class="resourceview {@class}" id="resourceview_{@id}">
      <ul class="resourceview_tabs" id="resourceview_tabs_{@id}">
        <xsl:comment>O</xsl:comment>
      </ul>
       <ul class="resourceview_menu" id="resourceview_menu_{@id}">
         <xsl:comment>O</xsl:comment>
      </ul>
     <div id="resourceview_view_{@id}" class="resourceview">&#xA0;</div>
    </div>
      <div id="dialogs_{@id}" class="resourceview_view">&#xA0;
         <xsl:apply-templates select="./kd:use/kd:action"/>
      </div>
  </xsl:template>

  <!--  **********************  -->
  <!--  component sidebar       -->
  <!--  **********************  -->

  <xsl:template name="initsidebar">
    <xsl:param name="sidebar" />
    <xsl:param name="obj" />
      <xsl:choose>
        <xsl:when test="$sidebar/@class">
          v.sidebar = new kolekti_<xsl:value-of select="$sidebar/@class"/>(id, <xsl:value-of select="$obj" />);
        </xsl:when>
        <xsl:otherwise>
          v.sidebar = new kolekti_sidebar(id, <xsl:value-of select="$obj" />);</xsl:otherwise>
      </xsl:choose>
      v.sidebar.properties = new Array();
      <xsl:for-each select="$sidebar/kd:property">
        v.sidebar.properties.push({ns:'<xsl:value-of select="@ns" />',propname:'<xsl:value-of select="@propname" />'});
      </xsl:for-each>
      v.sidebar.initevent();
  </xsl:template>
</xsl:stylesheet>
