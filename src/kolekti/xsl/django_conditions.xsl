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
  xmlns:html="http://www.w3.org/1999/xhtml" 
  xmlns="http://www.w3.org/1999/xhtml" 
  exclude-result-prefixes="html"
  version="1.0">

  <xsl:template match="*[contains(@class,'=')]" priority="10">
    <div class="condition" data-condition="{translate(@class, ' ','')}">
      <xsl:copy>
        <xsl:apply-templates select="node()|@*"/>
      </xsl:copy>
    </div>    
  </xsl:template>

  <xsl:template match="html:span[contains(@class,'=')]|span[contains(@class,'=')]" priority="10">
    <span class="condition" data-condition="{translate(@class, ' ','')}">
      <xsl:copy>
        <xsl:apply-templates select="node()|@*"/>
      </xsl:copy>
    </span>    
  </xsl:template>

  <xsl:template match="html:td[contains(@class,'=')]|td[contains(@class,'=')]" priority="10">
      <xsl:copy>
        <xsl:apply-templates select="@*"/>
        <div class="condition" data-condition="{translate(@class, ' ','')}">
          <xsl:apply-templates select="node()"/>
        </div>    
    </xsl:copy>

  </xsl:template>


  <xsl:template match="node()|@*" mode="row-conditional">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="row-conditional"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:table[.//html:tr[contains(@class,'=')]]|table[.//tr[contains(@class,'=')]]" priority="10">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="class">table table-condensed table-row-conditional</xsl:attribute>
      <xsl:apply-templates mode="row-conditional"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:tr|tr" mode="row-conditional">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <td class="condition-placeholder">
        &#xA0;
      </td>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:tr[contains(@class,'=')]|tr[contains(@class,'=')]" mode="row-conditional">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <td class="condition-left" data-condition="{translate(@class, ' ','')}">
        &#xA0;
      </td>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
