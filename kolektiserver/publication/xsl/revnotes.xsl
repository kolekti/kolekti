<?xml version="1.0" encoding="ISO-8859-1"?>
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
  xmlns="http://www.w3.org/1999/xhtml" 
  xmlns:html="http://www.w3.org/1999/xhtml" 
  xmlns:kfp="kolekti:extensions:functions:publication"
  exclude-result-prefixes="html kfp"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <xsl:variable name="revisions" select="kfp:modules_history()" />

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='REVNOTES']">
    <xsl:variable name="modulespath" select="//html:div[@class='module']/html:div[@class='moduleinfo'][html:p/html:span[@class='infolabel']/text() = 'source']/html:p/html:span[@class='infovalue']/html:a" />
    <div class="REVNOTES">
      <xsl:apply-templates select="html:*[@class='REVNOTES_titre']" mode="revnotestitle" />
      <div class="REVNOTES_corps">
        <table>
         <thead>
            <th><xsl:value-of select="kfp:replace_strvar('[var kolektitext:NomMod]')" /></th>
            <th><xsl:value-of select="kfp:replace_strvar('[var kolektitext:Location]')" /></th>
            <th><xsl:value-of select="kfp:replace_strvar('[var kolektitext:RevInd]')" /></th>
            <th><xsl:value-of select="kfp:replace_strvar('[var kolektitext:Author]')" /></th>
            <th><xsl:value-of select="kfp:replace_strvar('[var kolektitext:Date]')" /></th>
            <th><xsl:value-of select="kfp:replace_strvar('[var kolektitext:Comments]')" /></th>
         </thead>
         <tbody>
            <xsl:apply-templates select="$revisions/revnotes[$modulespath/text() = @path]" mode="revnotes"/>
         </tbody>
        </table>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="html:*[@class='REVNOTES_titre']" mode="revnotestitle">
    <p class="REVNOTES_titre">
      <xsl:apply-templates />
    </p>
  </xsl:template>

  <xsl:template match="html:*[@class='REVNOTES_titre']" mode="revnotes" />

  <xsl:template match="moduleshistory/revnotes" mode="revnotes">
   <xsl:variable name="countlog" select="count(revnote)" />
   <xsl:variable name="modname">
      <xsl:call-template name="modname">
         <xsl:with-param name="path" select="@path" />
      </xsl:call-template>
   </xsl:variable>
   <xsl:variable name="revnotes" select="revnote" />
   <tr>
      <td rowspan="{$countlog}">
         <xsl:value-of select="$modname"/>
      </td>
      <td rowspan="{$countlog}">
         <xsl:value-of select="substring-before(substring-after(@path, 'project://'), concat('/', $modname))" />
      </td>
      <td>
         <xsl:value-of select="$revnotes[last()]/@rev"/>
      </td>
      <td>
         <xsl:value-of select="$revnotes[last()]/@user"/>
      </td>
      <td>
         <xsl:value-of select="$revnotes[last()]/@date"/>
      </td>
      <td>
         <xsl:value-of select="$revnotes[last()]"/>
      </td>
   </tr>
   <xsl:for-each select="$revnotes[position()&lt;last()]">
      <xsl:sort select="@rev" order="descending" />
      <tr>
         <td>
            <xsl:value-of select="@rev"/>
         </td>
         <td>
            <xsl:value-of select="@user"/>
         </td>
         <td>
            <xsl:value-of select="@date"/>
         </td>
         <td>
            <xsl:value-of select="."/>
         </td>
      </tr>
   </xsl:for-each>
  </xsl:template>

  <xsl:template name="modname">
   <xsl:param name="path" />
   <xsl:choose>
      <xsl:when test="contains($path, '/')">
         <xsl:call-template name="modname">
            <xsl:with-param name="path" select="substring-after($path, '/')" />
         </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="$path" />
      </xsl:otherwise>
   </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
