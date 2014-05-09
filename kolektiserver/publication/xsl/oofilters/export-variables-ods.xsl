<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   

xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" 
xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" 
xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" 
xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" 

  xmlns:exsl="http://exslt.org/common"
  xmlns="http://www.w3.org/1999/xhtml"
  extension-element-prefixes="exsl"
  exclude-result-prefixes="office style text table"
  version="1.0">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <variables>
      <critlist>
	<xsl:apply-templates select="//table:table[1]/table:table-row[starts-with(table:table-cell/text:p/text(),':')]/table:table-cell[1]" mode="listcrits"/>
      </critlist>
      <xsl:apply-templates select="//table:table[1]"/>
    </variables>
  </xsl:template>

  <xsl:template match="table:table-cell" mode="listcrits">
    <crit name="{substring-after(normalize-space(text:p),':')}"/>
  </xsl:template>


  <xsl:template match="table:table">
    <xsl:apply-templates select="table:table-row[starts-with(table:table-cell/text:p/text(),'&amp;')]"/>
  </xsl:template>

  <xsl:template match="table:table-row">
    <variable code="{substring-after(normalize-space(table:table-cell[1]),'&amp;')}">
      <xsl:apply-templates select="table:table-cell[text:p][position() &gt; 1]"/>
    </variable>
  </xsl:template>

  <xsl:template match="table:table-cell">
    <xsl:call-template name="genvarval">
      <xsl:with-param name="pos" select="count(preceding-sibling::table:table-cell[not(@table:number-columns-repeated)]) + sum(preceding-sibling::table:table-cell/@table:number-columns-repeated)"/>
    </xsl:call-template>
  </xsl:template>


  <xsl:template name="genvarval">
    <xsl:param name="pos"/>
    <xsl:param name="curpos">0</xsl:param>
    <value>
      <xsl:call-template name="getcrits">
	<xsl:with-param name="col" select="$pos+$curpos"/>
      </xsl:call-template>
      <content><xsl:apply-templates/></content>
    </value>
    <xsl:if test="@table:number-columns-repeated and $curpos &lt; (@table:number-columns-repeated - 1)">
      <xsl:call-template name="genvarval">
	<xsl:with-param name="pos" select="$pos"/>
	<xsl:with-param name="curpos" select="$curpos + 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- ********************************************************************************************* -->


  <xsl:template name="getcrits">
    <xsl:param name="col"/>
    <xsl:apply-templates select="//table:table[1]/table:table-row[starts-with(table:table-cell/text:p/text(),':')]/table:table-cell[text:p]" mode="crits">
      <xsl:with-param name="col" select="$col"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="table:table-cell" mode="crits">
    <xsl:param name="col"/>
    <xsl:variable name="pos" select="count(preceding-sibling::table:table-cell[not(@table:number-columns-repeated)]) + sum(preceding-sibling::table:table-cell/@table:number-columns-repeated)"/>
    <xsl:choose>
      <xsl:when test="$pos = $col">
	<xsl:call-template name="crit"/>
      </xsl:when>
      <xsl:when test="@table:number-columns-repeated and $pos &lt; $col and ($pos+@table:number-columns-repeated) &gt; $col">
	<xsl:call-template name="crit"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="crit">
    <crit name="{substring-after(normalize-space(parent::*/table:table-cell[1]),':')}" value="{normalize-space(.)}"/>
  </xsl:template>

  <!-- ********************************************************************************************* -->

  <xsl:template match="text:p">
     <xsl:if test="preceding-sibling::text:p">
       <br/>
     </xsl:if>
     <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text:span[@text:style-name]">
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
