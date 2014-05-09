<?xml version="1.0" encoding="utf-8"?>
<!--

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

-->
<?doc UI generation main stylesheet
This stylesheet generates :
- javascript inclusions
- css inclusions
- js objects instanciation and initialisation,
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
                xmlns:kcd="kolekti:ctrdata"
                xmlns:e="http://exslt.org/common"
                xmlns:d="DAV:"
                extension-element-prefixes="ke e"
                exclude-result-prefixes="i kf kd kcd h e d">

  <xsl:param name="kolektifmk" />
  <xsl:param name="kolektiapp" />
  <xsl:include href="dialogs-actions.xsl"/>
  <xsl:include href="dialogs-browsers.xsl"/>
  <xsl:include href="dialogs-resourceviews.xsl"/>
  <xsl:include href="dialogs-guiders.xsl"/>
  <xsl:include href="dialogs-upload.xsl"/>
  <xsl:include href="dialogs-panelcontrol.xsl"/>
  <xsl:include href="dialogs-svnrevision.xsl"/>

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="kd:*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="h:head">
    <xsl:copy>
      <xsl:apply-templates select="h:*|@*"/>

      <!-- include ajax lib if some dialogs components in the page -->
      <xsl:if test="/h:html//kd:*">
        <script type="text/javascript" src="/_lib/kolekti/scripts/ajax.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <script type="text/javascript" src="/_lib/kolekti/scripts/ajax-dav.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>

        <!-- include kolekti lib & jquery + ui if some dialog components in the page -->
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        
        <script type="text/javascript" src="/_lib/kolekti/scripts/locale/{kf:getlocale()}/kolekti.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>

        <script type="text/javascript">
          kolekti.uid='<xsl:value-of select="kf:userid()"/>';
          kolekti.project='<xsl:value-of select="kf:get_http_data('kolekti', 'project')/@directory"/>';
          kolekti.locale='<xsl:value-of select="kf:get_http_data('user', 'locale')" />';
        </script>
      </xsl:if>

      <link href="/_lib/kolekti/scripts/jquery/css/ui-lightness/jquery-ui-1.8.14.custom.css" media="all" rel="stylesheet" type="text/css" />
      <script type="text/javascript" src="/_lib/kolekti/scripts/jquery/js/jquery-1.6.1.min.js">
        <xsl:text>&#x0D;</xsl:text>
      </script>

      <script type="text/javascript" src="/_lib/kolekti/scripts/jquery/js/jquery-ui-1.8.14.custom.min.js">
        <xsl:text>&#x0D;</xsl:text>
      </script>

      <!-- loads required scripts -->
      <xsl:for-each select="//kd:require">
        <xsl:if test="not(preceding::kd:require[@href=current()/@href])">
          <script type="text/javascript" src="{@href}">
            <xsl:text>&#x0D;</xsl:text>
          </script>
        </xsl:if>
      </xsl:for-each>

      <!-- admin panel -->
      <xsl:if test="//kd:kolektiadmin">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-admin.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-admin.css" media="all" rel="stylesheet" type="text/css" />
      </xsl:if>

      <!-- actions -->
      <xsl:if test="/h:html/h:body//kd:action">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-actions.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-actions.css" media="all" rel="stylesheet" type="text/css" />

        <!-- objects for specific actions management -->
        <xsl:apply-templates select="/h:html/h:body//kd:action[@id]" mode="include"/>
      </xsl:if>
      <!-- /actions -->

      <xsl:if test="//kd:ajaxbrowser|//kd:resourceview">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-sessions.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
      </xsl:if>

      <!-- ajax browser  -->
      <xsl:if test="//kd:ajaxbrowser">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-browser.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-browser.css" media="all" rel="stylesheet" type="text/css" />
        <!-- objects for tab management -->
        <xsl:apply-templates select="//kd:ajaxbrowser" mode="include"/>
      </xsl:if>
      <!-- /ajax browser -->


      <!-- resourceview component -->
      <xsl:if test="//kd:resourceview">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-resourceview.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-resourceview.css" media="all" rel="stylesheet" type="text/css" />

        <xsl:apply-templates select="//kd:resourceview" mode="include"/>

      </xsl:if>
      <!-- /resourceview component -->


      <!-- sidebar component -->
      <xsl:if test="//kd:resourceview//kd:sidebar">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-sidebar.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-sidebar.css" media="all" rel="stylesheet" type="text/css" />

        <xsl:apply-templates select="//kd:resourceview//kd:sidebar" mode="include"/>
      </xsl:if>
      <!-- /sidebar component -->

      <!-- upload-form component -->
      <xsl:if test="//kd:upload-form">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-uploadform.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-uploadform.css" media="all" rel="stylesheet" type="text/css" />

        <xsl:apply-templates select="//kd:upload-form" mode="include"/>
      </xsl:if>
      <!-- /upload-form component -->

      <!-- panelcontrol component -->
      <xsl:if test="//kd:panelcontrol">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-panelcontrol.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-panelcontrol.css" media="all" rel="stylesheet" type="text/css" />

        <xsl:apply-templates select="//kd:panelcontrol" mode="include"/>
      </xsl:if>
      <!-- /panelcontrol component -->

      <!-- svnrevision component -->
      <xsl:if test="//kd:svnrevision">
        <script type="text/javascript" src="/_lib/kolekti/scripts/kolekti-svnrevision.js">
          <xsl:text>&#x0D;</xsl:text>
        </script>
        <link href="/_lib/kolekti/css/kolekti-svnrevision.css" media="all" rel="stylesheet" type="text/css" />

        <xsl:apply-templates select="//kd:svnrevision" mode="include"/>
      </xsl:if>
      <!-- /svnrevision component -->

      <!-- guiders component -->
      <xsl:if test="//kd:guiders">
        <xsl:apply-templates select="//kd:guiders" mode="include"/>
      </xsl:if>
      <!-- /guiders component -->
    </xsl:copy>
  </xsl:template>

  <!--  **********************  -->
  <!--  ui content              -->
  <!--  **********************  -->

  <xsl:template match="h:div[contains(@class,'shrinkable')]">
    <div class="splitcontentleft" id="shrinkable">
      <xsl:apply-templates select="node()"/>
    </div>
    <div id="shrinkablehandle" onclick="kolekti.shrink()"><br/></div>
  </xsl:template>

  <xsl:template match="h:div[@class='splitcontentright']">
    <div class="splitcontentright" id="shrinkablespacer">
      <xsl:apply-templates select="node()"/>
    </div>
  </xsl:template>


  <!--  **********************  -->
  <!--  list template           -->
  <!--  **********************  -->

  <xsl:template match="kd:listtemplates">
   <select name="{@name}">
      <xsl:apply-templates select="kf:listtemplates(string(@dir))" />
   </select>
  </xsl:template>

  <xsl:template match="kcd:option">
   <option value="{@value}"><xsl:value-of select="substring-before(@value, '.')" /></option>
  </xsl:template>

  <!--  **********************  -->
  <!--  logout script           -->
  <!--  **********************  -->

  <xsl:template match="kd:logout">
    <script type="text/javascript">
      var deco=new ajax('/');
      deco.auth('logout','');
      window.location.href="/";
    </script>
    <div id="logout">
      <p>deconnexion</p>
    </div>
  </xsl:template>

  <!-- i18n templates -->
  <xsl:template match="@*" mode="i18n">
   <xsl:value-of select="." />
  </xsl:template>

  <xsl:template match="@i:*" mode="i18n">
   <i:text><xsl:value-of select="." /></i:text>
  </xsl:template>
</xsl:stylesheet>
