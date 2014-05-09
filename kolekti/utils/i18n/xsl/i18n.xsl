<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns="http://www.w3.org/1999/xhtml"

                exclude-result-prefixes="i">

   <xsl:output method="xml" indent="yes"/>

   <xsl:template match="node()|@*">
      <xsl:copy>
         <xsl:apply-templates select="node()|@*"/>
      </xsl:copy>
   </xsl:template>

   <xsl:template match="i:text">
      <xsl:variable name="s" select="kf:gettext(string(.))" />
      <xsl:choose>
         <xsl:when test="i:param">
            <xsl:apply-templates select="i:param[1]" mode="param">
               <xsl:with-param name="s" select="$s" />
            </xsl:apply-templates>
         </xsl:when>
         <xsl:otherwise>
           <xsl:value-of select="$s" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <xsl:template match="@i:*">
      <xsl:attribute name="{local-name()}">
         <xsl:value-of select="kf:gettext(string(.))" />
      </xsl:attribute>
   </xsl:template>
   
   <xsl:template match="i:param" mode="param">
      <xsl:param name="s" />
      <xsl:choose>
         <xsl:when test="following-sibling::i:param">
            <xsl:apply-templates select="following-sibling::i:param[1]" mode="param">
               <xsl:with-param name="s" select="kf:replace_param($s, string(@name), string(@value))" />
            </xsl:apply-templates>
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="kf:replace_param($s, string(@name), string(@value))" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
</xsl:stylesheet>