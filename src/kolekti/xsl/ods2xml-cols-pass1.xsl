<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   

xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" 
xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" 
xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" 
xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" 
xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"

  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="office style text table fo"
  version="1.0">

  <xsl:output method="xml" indent="yes"/>


  <xsl:template match="/">
    <variables>
      <critlist>
	<xsl:apply-templates select="//table:table[1]/table:table-row[starts-with(table:table-cell[1]/text:p/text(),':')]"/>
      </critlist>
      <values>
	<xsl:apply-templates select="//table:table[1]/table:table-row[starts-with(table:table-cell[1]/text:p/text(),'&amp;')]"/>
      </values>
    </variables>
  </xsl:template>


  <xsl:template match="table:table-row">
    <row>
      <xsl:apply-templates select="table:table-cell"/>
    </row>
  </xsl:template>

  <xsl:template match="table:table-cell[1]">
    <hcell>
      <xsl:apply-templates select="text:p"/>
    </hcell>
  </xsl:template>

  <xsl:template match="table:table-cell">
    <cell>
      <xsl:apply-templates select="text:p"/>
    </cell>
    <xsl:if test="@table:number-columns-repeated and (text:p or following-sibling::table:table-cell[text:p])">
      <xsl:call-template name="reccell">
	<xsl:with-param name="num" select="@table:number-columns-repeated - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template name="reccell">
    <xsl:param name="num"/>
    <xsl:if test="$num &gt; 0">
      <cell>
	<xsl:apply-templates select="text:p"/>
      </cell>
      <xsl:call-template name="reccell">
	<xsl:with-param name="num" select="$num - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- ********************************************************************************************* -->

  <xsl:template match="text:p">
     <xsl:if test="preceding-sibling::text:p">
       <br/>
     </xsl:if>
     <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text:span[@text:style-name]">
    <xsl:message>span <xsl:value-of select="@text:style-name"/></xsl:message>
    <xsl:call-template name="checksup">
      <xsl:with-param name="stylename" select="@text:style-name"/>
      <xsl:with-param name="content"><xsl:apply-templates/></xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:value-of select="normalize-space(.)"/>
  </xsl:template>

  <xsl:template name="checksup">
    <xsl:param name="stylename"/>
    <xsl:param name="content"/>

    <xsl:choose>
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:text-properties[starts-with(@style:text-position,'super ')]">
	<xsl:message>sup</xsl:message>
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
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:text-properties[starts-with(@style:text-position,'sub ')]">
	<xsl:message>sub</xsl:message>
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
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:text-properties[@fo:font-weight='bold']">
	<xsl:message>bold</xsl:message>
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
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:text-properties[@fo:font-style='italic']">
	<xsl:message>em</xsl:message>
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
      <xsl:when test="/office:document-content/office:automatic-styles/style:style[@style:name=$stylename]/style:text-properties[@style:text-underline-style='solid']">
	<xsl:message>under</xsl:message>
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
