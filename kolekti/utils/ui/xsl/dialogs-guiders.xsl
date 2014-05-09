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
     xmlns:kf="kolekti:extensions:functions"
     xmlns:ke="kolekti:extensions:elements"
     xmlns:kd="kolekti:dialogs"
     xmlns:e="http://exslt.org/common"
     xmlns:d="DAV:"

     extension-element-prefixes="ke e"
     exclude-result-prefixes="kf kd h e d">

  <!--  *****************  -->
  <!--  component guiders  -->
  <!--  *****************  -->
  
  <xsl:template match="kd:guiders" mode="include">
    <xsl:if test="not(preceding::kd:guiders)">
      <script type="text/javascript" src="/_lib/kolekti/scripts/jquery/js/jquery.ba-dotimeout.min.js">     
        <xsl:text>&#x0D;</xsl:text>
      </script>
      <script type="text/javascript" src="/_lib/kolekti/scripts/guiders/guider.js">
        <xsl:text>&#x0D;</xsl:text>
      </script>
      <link href="/_lib/kolekti/scripts/guiders/guider.css" media="all" rel="stylesheet" type="text/css" />
    </xsl:if>
    <xsl:apply-templates select="." mode="head"/>
  </xsl:template>


  <!--  *****************  -->
  <!--  guiders head part  -->
  <!--  *****************  -->

  <xsl:template match="kd:guiders" mode="head">
      <script type="text/javascript">
        guider._defaultSettings.buttons=[];
        <xsl:if test="@file">
          $.doTimeout('guiderinit',20,function(){
          <xsl:apply-templates select="document(concat($kolektiapp,'/ui/guiders/',@file))/map//node[attribute/@NAME='selector']"/>
          <xsl:text>kolekti.update_guiders('body');</xsl:text>
         });
        </xsl:if>
      </script>
  </xsl:template>

  <!--  *****************  -->
  <!--  guiders body part  -->
  <!--  *****************  -->
  
  <xsl:template match="/map//node[attribute/@NAME='selector']">
    <!-- guiders definition for elements -->
    <xsl:variable name="selector" select="attribute[@NAME='selector']/@VALUE"/>
    <!--<xsl:for-each select="node">-->
      <xsl:text>guider.createGuider({</xsl:text>
      <xsl:text>attachTo: "</xsl:text>
      <xsl:value-of select="$selector"/>
      <xsl:text>",</xsl:text>
      <xsl:text>buttons: [],</xsl:text> 
     <!-- no buttons  
           <xsl:text>buttons: [{name: "Close"}</xsl:text> 
           <xsl:if test="following-sibling::node">
             <xsl:text>,{name:"Next"}</xsl:text>
           </xsl:if>
           <xsl:text>],</xsl:text>
      -->
      <xsl:text>description: "</xsl:text>
      <xsl:apply-templates select="richcontent[@TYPE='NOTE']/html/body/*" mode="guidersescapehtml"/>
      <xsl:text>",</xsl:text>
      <xsl:text>id: "</xsl:text><xsl:value-of select="@ID"/><xsl:text>",</xsl:text>
      <!--
           <xsl:if test="following-sibling::node">
             <xsl:text>next: "</xsl:text><xsl:value-of select="following-sibling::node[1]/@ID"/><xsl:text>",</xsl:text>
           </xsl:if>
      -->
      <xsl:text>overlay: false,</xsl:text>
      <xsl:text>title: "</xsl:text><xsl:value-of select="@TEXT"/><xsl:text>"</xsl:text>
      <xsl:if test="attribute[@NAME='position']">
        <xsl:text>,position:</xsl:text><xsl:value-of select="attribute[@NAME='position']/@VALUE"/><xsl:text></xsl:text>
      </xsl:if>
      <xsl:text>});</xsl:text>
      <!--
           <xsl:if test="following-sibling::node">
             <xsl:text>,</xsl:text>
           </xsl:if>
      -->
      <!--</xsl:for-each>-->
      <!--<xsl:text>];</xsl:text>-->
      <xsl:text>&#x0A;</xsl:text>
      <xsl:text>kolekti.add_guider("</xsl:text>
      <xsl:value-of select="@ID"/>
      <xsl:text>",'</xsl:text>
      <xsl:value-of select="$selector"/>
      <xsl:text>');</xsl:text>
  </xsl:template>

  <xsl:template match="richcontent[@TYPE='NOTE']/html/body//*" mode="guidersescapehtml">
    <xsl:text disable-output-escaping="yes">&lt;</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:apply-templates select="@*" mode="guidersescapehtml"/>
    <xsl:text disable-output-escaping="yes">&gt;</xsl:text>
    <xsl:apply-templates mode="guidersescapehtml"/>
    <xsl:text disable-output-escaping="yes">&lt;/</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text disable-output-escaping="yes">&gt;</xsl:text>
  </xsl:template>

  <xsl:template match="richcontent[@TYPE='NOTE']/html/body//@*" mode="guidersescapehtml">
    <xsl:text> </xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text>=\"</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>\"</xsl:text>
  </xsl:template>

  <xsl:template match="richcontent[@TYPE='NOTE']/html/body//text()" mode="guidersescapehtml">
    <xsl:variable name="n" select="normalize-space(.)"/>
    <xsl:if test="substring(.,1,1)!=substring($n,1,1)">
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:value-of select="$n"/>
    <xsl:if test="substring(.,string-length(.)-1,1)!=substring(.,string-length($n)-1,1)">
      <xsl:text> </xsl:text>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>


