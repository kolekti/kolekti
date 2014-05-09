<?xml version="1.0" encoding="utf-8"?>
<!-- kOLEKTi : a structural documentation generator Copyright (C) 2007 Stéphane 
   Bonhomme (stephane@exselt.com) This program is free software: you can redistribute 
   it and/or modify it under the terms of the GNU General Public License as 
   published by the Free Software Foundation, either version 3 of the License, 
   or (at your option) any later version. This program is distributed in the 
   hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied 
   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
   GNU General Public License for more details. You should have received a copy 
   of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>. -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml" xmlns="http://www.w3.org/1999/xhtml"
                xmlns:kfp="kolekti:extensions:functions:publication"

                extension-element-prefixes="kfp" exclude-result-prefixes="html kfp"
                version="1.0">

   <xsl:output method="xml" indent="no" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

   <xsl:include href="textes-auto.xsl" />

   <xsl:template match="node()|@*">
      <xsl:copy>
         <xsl:apply-templates select="node()|@*" />
      </xsl:copy>
   </xsl:template>

   <!-- templates de remplacement des prédicats dans les chemins d'images -->

   <xsl:template match="html:img/@src|html:embed/@src">
      <xsl:attribute name="src">
         <xsl:value-of select="kfp:replace_mastercrit(string(.))" />
      </xsl:attribute>
   </xsl:template>

   <!-- templates de remplacement des conditions -->

   <xsl:template match="html:div[@class='module']">
      <xsl:variable name="children">
         <xsl:apply-templates
            select="node()[not(self::html:div[@class='moduleinfo'])]" />
      </xsl:variable>
      <xsl:if test="normalize-space(string($children))">
         <xsl:copy>
            <xsl:apply-templates select="@*" />
            <xsl:copy-of select="html:div[@class='moduleinfo']" />
            <xsl:copy-of select="$children" />
         </xsl:copy>
      </xsl:if>
   </xsl:template>

   <xsl:template match="html:div[contains(@class,'=')]|html:span[contains(@class,'=')]">
      <xsl:variable name="classcond">
         <xsl:choose>
            <xsl:when test="starts-with(@class,'cond:')">
               <xsl:value-of select="translate(substring-after(@class,':'),' ','')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="translate(@class,' ','')" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>

      <xsl:variable name="cond">
         <xsl:call-template name="process_list_cond">
            <xsl:with-param name="listcond" select="$classcond" />
         </xsl:call-template>
      </xsl:variable>
      <xsl:choose>
         <xsl:when test="$cond='true'">
            <xsl:apply-templates select="node()" />
         </xsl:when>
         <xsl:when test="$cond='false'"> </xsl:when>
         <xsl:otherwise>
            <xsl:copy>
               <xsl:apply-templates select="@*" />
               <xsl:attribute name="class"><xsl:value-of select="$cond"/></xsl:attribute>
               <xsl:apply-templates select="node()" />
            </xsl:copy>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <xsl:template match="html:*[contains(@class,'=')]">
      <xsl:variable name="classcond">
         <xsl:choose>
            <xsl:when test="starts-with(@class,'cond:')">
               <xsl:value-of select="translate(substring-after(@class,':'),' ','')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="translate(@class,' ','')" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>

      <xsl:variable name="cond">
         <xsl:call-template name="process_list_cond">
            <xsl:with-param name="listcond" select="$classcond" />
         </xsl:call-template>
      </xsl:variable>
      <xsl:choose>
         <xsl:when test="$cond='true'">
            <xsl:copy>
               <xsl:apply-templates select="node()|@*[not(local-name()='class')]" />
            </xsl:copy>
         </xsl:when>
         <xsl:when test="$cond='false'"> </xsl:when>
         <xsl:otherwise>
            <xsl:copy> 
               <xsl:apply-templates select="@*" />
               <xsl:attribute name="class"><xsl:value-of select="$cond"/></xsl:attribute>
               <xsl:apply-templates select="node()" />
            </xsl:copy>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <xsl:template match="html:var[not(contains(@class,':'))]">
      <xsl:choose>
         <xsl:when test="/html:html/html:head/html:meta[@scheme='condition' and @name=current()/@class]">
            <xsl:value-of select="/html:html/html:head/html:meta[@scheme='condition' and @name=current()/@class]/@content" />
         </xsl:when>
         <xsl:otherwise>
            <var class="{@class}"><xsl:apply-templates /></var>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <!-- ce template produit un booleen vrai si toutes les conditions de listcond 
      sont vérifiées -->
   <xsl:template name="process_list_cond">
      <xsl:param name="listcond" />
      <xsl:choose>
         <xsl:when test="contains($listcond,';')">
            <xsl:variable name="cond_prefix">
               <xsl:call-template name="process_cond">
                  <xsl:with-param name="cond"
                     select="substring-before($listcond,';')" />
               </xsl:call-template>
            </xsl:variable>

            <xsl:choose>
               <xsl:when test="$cond_prefix='false'">
                  <xsl:value-of select="$cond_prefix" />
               </xsl:when>
               <xsl:when test="$cond_prefix='true'">
                  <xsl:call-template name="process_list_cond">
                    <xsl:with-param name="listcond" select="substring-after($listcond,';')" />
                  </xsl:call-template>
               </xsl:when>
               <xsl:otherwise>
                  <xsl:variable name="rest_cond">
                     <xsl:call-template name="process_list_cond">
                        <xsl:with-param name="listcond" select="substring-after($listcond,';')" />
                     </xsl:call-template>
                   </xsl:variable>

                   <xsl:choose>
                      <xsl:when test="$rest_cond = 'false'">
                         <xsl:value-of select="$rest_cond"/>
                      </xsl:when>
                      <xsl:when test="$rest_cond = 'true'">
                        <xsl:value-of select="$cond_prefix"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="$cond_prefix"/>
                        <xsl:text>;</xsl:text>
                        <xsl:value-of select="$rest_cond"/>
                      </xsl:otherwise>
                   </xsl:choose>
               </xsl:otherwise>
            </xsl:choose>
         </xsl:when>
         <xsl:otherwise>
            <xsl:call-template name="process_cond">
               <xsl:with-param name="cond" select="$listcond" />
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <!-- ce template produit un booleen vrai si la condition cond est verfiee -->
   <xsl:template name="process_cond">
      <xsl:param name="cond" />
      <xsl:variable name="predicat" select="substring-before($cond,'=')" />
      <xsl:variable name="values">
         <xsl:choose>
            <xsl:when test="starts-with(substring-after($cond,'='),'\')">
               <xsl:value-of select="substring-after(substring-after($cond,'='),'\')" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="substring-after($cond,'=')" />
            </xsl:otherwise>
         </xsl:choose>
      </xsl:variable>

      <xsl:choose>
         <xsl:when test="/html:html/html:head/html:meta[@scheme='condition'][@name=$predicat]">
            <!-- la condition est exprimee pour ce document -->
            <xsl:variable name="found">
               <xsl:choose>
                  <xsl:when test="starts-with($values,'[')">
                     <xsl:call-template name="value_in_range">
                        <xsl:with-param name="value" select="/html:html/html:head/html:meta[@scheme='condition'][@name=$predicat]/@content" />
                        <xsl:with-param name="range" select="$values" />
                     </xsl:call-template>
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:call-template name="value_in_list">
                        <xsl:with-param name="value" select="/html:html/html:head/html:meta[@scheme='condition'][@name=$predicat]/@content" />
                        <xsl:with-param name="list" select="$values" />
                     </xsl:call-template>
                  </xsl:otherwise>
               </xsl:choose>
            </xsl:variable>
            <xsl:choose>
               <xsl:when test="starts-with(substring-after($cond,'='),'\')">
                  <xsl:value-of select="$found='false'" />
               </xsl:when>
               <xsl:otherwise>
                  <xsl:value-of select="$found" />
               </xsl:otherwise>
            </xsl:choose>
         </xsl:when>
         <xsl:otherwise>
            <!-- la condition n'est pas exprimee pour ce document -->
            <xsl:value-of select="$cond" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <!-- ce template produit un booleen vrai si la chaine value est dans la 
      liste -->
   <xsl:template name="value_in_list">
      <xsl:param name="value" />
      <xsl:param name="list" />
      <xsl:choose>
         <xsl:when test="contains($list,',')">
            <xsl:choose>
               <xsl:when test="$value=substring-before($list,',')">
                  <xsl:value-of select="true()" />
               </xsl:when>
               <xsl:otherwise>
                  <xsl:call-template name="value_in_list">
                     <xsl:with-param name="value" select="$value" />
                     <xsl:with-param name="list" select="substring-after($list,',')" />
                  </xsl:call-template>
               </xsl:otherwise>
            </xsl:choose>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="$value=$list" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <!-- ce template produit un booleen vrai si la chaine value est un nombre 
      et est compris dans le range [min-max] -->
   <xsl:template name="value_in_range">
      <xsl:param name="value" />
      <xsl:param name="range" />
      <xsl:variable name="min" select="number(substring-after(substring-before($range,'-'),'['))" />
      <xsl:variable name="max" select="number(substring-before(substring-after($range,'-'),']'))" />
      <xsl:variable name="val" select="number($value)" />
      <xsl:value-of select="boolean($val &gt;= $min and $val &lt;= $max)" />
   </xsl:template>

   <!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -->

   <!-- template de suppression de la div moduleinfo -->
   <!-- <xsl:template match="html:div[@class='moduleinfo']"/> -->

</xsl:stylesheet>
