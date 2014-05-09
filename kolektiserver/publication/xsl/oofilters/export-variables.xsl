<?xml version="1.0" encoding="utf-8"?>
<!--
    kOLEKTi : a structural documentation generator
    Copyright (C) 2007 Stéphane Bonhomme (stephane@exselt.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


-->
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  xmlns:office="http://openoffice.org/2000/office"
  xmlns:style="http://openoffice.org/2000/style" 
  xmlns:text="http://openoffice.org/2000/text" 
  xmlns:table="http://openoffice.org/2000/table" 
  xmlns:draw="http://openoffice.org/2000/drawing"
  xmlns:fo="http://www.w3.org/1999/XSL/Format"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:number="http://openoffice.org/2000/datastyle"
  xmlns:svg="http://www.w3.org/2000/svg"
  xmlns:chart="http://openoffice.org/2000/chart"
  xmlns:dr3d="http://openoffice.org/2000/dr3d" 
  xmlns:math="http://www.w3.org/1998/Math/MathML" 
  xmlns:form="http://openoffice.org/2000/form"
  xmlns:script="http://openoffice.org/2000/script" 
  xmlns:exsl="http://exslt.org/common"
  xmlns="http://www.w3.org/1999/xhtml"
  extension-element-prefixes="exsl"
  exclude-result-prefixes="office style text table draw fo xlink number svg chart dr3d math form script"

  version="1.0">

  <xsl:template match="office:document-content">
    <xsl:apply-templates select=".//table:table"/>
  </xsl:template>
  <xsl:template match="office:document-content">
    <xsl:apply-templates select=".//table:table"/>
  </xsl:template>

  <xsl:template match="table:table"/>
  <xsl:template match="table:table[1]">
    <variables>
      <xsl:text>&#10;</xsl:text>
      <xsl:apply-templates select="table:table-row[starts-with(./table:table-cell/text:p/text(),'&amp;')]" mode="varout"/>
    </variables>
  </xsl:template>

  <xsl:template match="table:table-row[starts-with(./table:table-cell/text:p/text(),'&amp;')]" mode="varout">
    <variable>
      <xsl:attribute name="code">
        <xsl:value-of select="substring-after(./table:table-cell/text:p/text(),'&amp;')"/>
      </xsl:attribute>
      <xsl:text>&#10;</xsl:text>
      <xsl:apply-templates select="table:table-cell" mode="varout"/>
    </variable>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="table:table-cell" mode="varout">
    <xsl:variable name="cells">
      <xsl:value-of select="count(preceding-sibling::table:table-cell[not(@table:number-columns-repeated)])"/>
    </xsl:variable>
    <xsl:variable name="posmin">
      <xsl:value-of select="sum(preceding-sibling::table:table-cell/@table:number-columns-repeated)+$cells"/>
    </xsl:variable>
    <xsl:variable name="spancell">
      <xsl:choose>
        <xsl:when test="@table:number-columns-repeated">
          <xsl:value-of select="number(@table:number-columns-repeated)-1"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="number(0)"/>          
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="posmax">
      <xsl:value-of select="$posmin+$spancell"/>
    </xsl:variable>
    <xsl:if test="number($posmin)&lt;=2 and number($posmax)&gt;=2">
      <text lang="fr"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=3 and number($posmax)&gt;=3">
      <text lang="en" zone="europe"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=4 and number($posmax)&gt;=4">
      <text lang="en" zone="usa"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=5 and number($posmax)&gt;=5">
      <text lang="it"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=6 and number($posmax)&gt;=6">
      <text lang="de"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=7 and number($posmax)&gt;=7">
      <text lang="es"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=8 and number($posmax)&gt;=8">
      <text lang="nl"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=9 and number($posmax)&gt;=9">
      <text lang="sv"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=10 and number($posmax)&gt;=10">
      <text lang="pt"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=11 and number($posmax)&gt;=11">
      <text lang="el"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=12 and number($posmax)&gt;=12">
      <text lang="cs"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
    <xsl:if test="number($posmin)&lt;=13 and number($posmax)&gt;=13">
      <text lang="da"><xsl:apply-templates select="text:p"/></text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="table:table-row" mode="varout"/>


  <xsl:template match="text:p">
     <xsl:if test="preceding-sibling::text:p">
       <br/>
     </xsl:if>
     <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text:span[@text:style-name]">
    <xsl:call-template name="checksup">
      <xsl:with-param name="stylename" select="@text:style-name"/>
      <xsl:with-param name="content">
        <xsl:apply-templates/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="checksup">
    <xsl:param name="stylename"/>
    <xsl:param name="content"/>
        <xsl:message><xsl:value-of select="$stylename"/></xsl:message>

    <xsl:choose>
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:properties[starts-with(@style:text-position,'super ')]">
        <sup>
          <xsl:call-template name="checksub">
            <xsl:with-param name="stylename" select="$stylename"/>
            <xsl:with-param name="content" select="$content"/>
          </xsl:call-template>
        </sup>
       </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="checksub">
          <xsl:with-param name="stylename" select="$stylename"/>
          <xsl:with-param name="content" select="$content"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="checksub">    
    <xsl:param name="stylename"/>
    <xsl:param name="content"/>
    <xsl:choose>
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:properties[starts-with(@style:text-position,'sub ')]">
        <sub>
          <xsl:call-template name="checkbold">
            <xsl:with-param name="stylename" select="$stylename"/>
            <xsl:with-param name="content" select="$content"/>
          </xsl:call-template>
        </sub>
       </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="checkbold">
          <xsl:with-param name="stylename" select="$stylename"/>
          <xsl:with-param name="content" select="$content"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="checkbold">    
    <xsl:param name="stylename"/>
    <xsl:param name="content"/>
    <xsl:choose>
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:properties[@fo:font-weight='bold']">
        <strong>
          <xsl:call-template name="checkitalic">
            <xsl:with-param name="stylename" select="$stylename"/>
            <xsl:with-param name="content" select="$content"/>
          </xsl:call-template>
        </strong>
       </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="checkitalic">
          <xsl:with-param name="stylename" select="$stylename"/>
          <xsl:with-param name="content" select="$content"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="checkitalic">    
    <xsl:param name="stylename"/>
    <xsl:param name="content"/>
    <xsl:choose>
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:properties[@fo:font-style='italic']">
        <em>
          <xsl:call-template name="checkunderline">
            <xsl:with-param name="stylename" select="$stylename"/>
            <xsl:with-param name="content" select="$content"/>
          </xsl:call-template>
        </em>
       </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="checkunderline">
          <xsl:with-param name="stylename" select="$stylename"/>
          <xsl:with-param name="content" select="$content"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="checkunderline">    
    <xsl:param name="stylename"/>
    <xsl:param name="content"/>
    <xsl:choose>
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:properties[@style:text-underline='single']">
        <span style="text-decoration: underline">
          <xsl:value-of select="$content"/>
        </span>
       </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$content"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


</xsl:stylesheet>
