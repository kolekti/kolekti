<?xml version="1.0" encoding="utf-8"?>

<!DOCTYPE xsl:stylesheet [
<!ENTITY inclass "contains(concat(' ',normalize-space($class),' '),concat(' ',normalize-space(@class),' '))">
]>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
		xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" 
		xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" 
		xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" 
		xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" 
		xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" 
		xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" 
		xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
		xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
		xmlns:xlink="http://www.w3.org/1999/xlink"		
		xmlns:exsl="http://exslt.org/common"
		xmlns:html="http://www.w3.org/1999/xhtml"
		exclude-result-prefixes="html"
		extension-element-prefixes="exsl"
		>
<xsl:output indent="yes"/>
  <xsl:param name="pivot"/>
  <xsl:param name="styles"/>
  <xsl:param name="mapping"/>

  <xsl:variable name="mappings" select="document($mapping)/mappings"/>
  <xsl:variable name="stylesdoc" select="document($styles)/office:document-styles"/>
  <xsl:variable name="imgzoom">
    <xsl:choose>
      <xsl:when test="document($mapping)/mappings/imgprop/@zoomfactor">
	<xsl:value-of select="document($mapping)/mappings/imgprop/@zoomfactor"/>
      </xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="automatic-styles" select="/office:document-content/office:automatic-styles"/>
  <xsl:variable name="template-tables" select="/office:document-content/office:body//table:table"/>

  <xsl:variable name="custom-cell-styles">
    <xsl:for-each select="/office:document-content/office:body/office:text//table:table-cell[string(.)]">
      <xsl:variable name="table" select="substring-before(@table:style-name,'.')"/>
      <style name="{$table}.{string(.)}"/>
    </xsl:for-each>
  </xsl:variable> 

  <xsl:variable name="tpltoc" select="/office:document-content/office:body/office:text/text:table-of-content[1]"/>
  <xsl:variable name="tplindex" select="/office:document-content/office:body/office:text/text:alphabetical-index[1]"/>

  <xsl:template match="/office:document-content">
    <!--
    <xsl:message><xsl:value-of select="document('')/xsl:stylesheet/namespace::text"/></xsl:message>
    -->
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="/office:document-content//node() | /office:document-content//@*" priority="-1">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>


  <xsl:template match="office:automatic-styles">
    <xsl:copy>
      <style:style style:name="kolekti-sub" style:family="text">
	<style:text-properties style:text-position="sub 58%"/>
      </style:style>
      <style:style style:name="kolekti-sup" style:family="text">
	<style:text-properties style:text-position="super 58%"/>
      </style:style>
      <style:style style:name="kolekti-ital" style:family="text">
	<style:text-properties fo:font-style="italic" style:font-style-asian="italic" style:font-style-complex="italic"/>
      </style:style>
      <style:style style:name="kolekti-bold" style:family="text">
	<style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
      </style:style>
      <style:style style:name="kolekti-dt" style:family="text">
	<style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
      </style:style>
      <style:style style:name="kolekti-toct" style:family="paragraph">
	<style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="1.021cm" fo:text-align="center" style:justify-single-word="false" fo:break-before="page"/>
	<style:text-properties fo:font-size="16pt" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
      </style:style>
      <style:style style:name="kolekti-cell" style:family="table-cell">
	<style:table-cell-properties style:vertical-align="top" fo:padding="0.101cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.005cm solid #000000"/>
      </style:style>
      <style:style style:name="kolekti-gc" style:family="graphic" style:parent-style-name="Graphics">
	<style:graphic-properties fo:margin-left="0cm" fo:margin-right="0cm" 
				  style:vertical-pos="top" style:vertical-rel="baseline" style:horizontal-pos="center" style:horizontal-rel="paragraph" 
				  fo:padding="0cm" fo:border="none" style:shadow="none" style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)" 
				  draw:luminance="0%" draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%" draw:gamma="100%" 
				  draw:color-inversion="false" draw:image-opacity="100%" draw:color-mode="standard"/>
      </style:style>
      <xsl:apply-templates select="document($mapping)/mappings/map/extension" mode="styles"/>
      <xsl:apply-templates select="style:style[@style:family='table']"/> 
      <xsl:apply-templates select="style:style[@style:family='table-column']"/> 
      <xsl:apply-templates select="style:style[@style:family='table-cell']"/> 
      <!--generate custom cell styles named in template -->
      <xsl:apply-templates select="/office:document-content/office:body/office:text//table:table-cell[string(.)]" mode="stylescells"/>
      <xsl:apply-templates select="document($pivot)//html:table" mode="styles"/>
      <!--<xsl:apply-templates select="style:style[@style:family='graphic']"/> -->
      <xsl:apply-templates select="document($pivot)//html:img" mode="styles"/>
      <xsl:apply-templates select="number:number-style"/>
      <xsl:apply-templates select="number:date-style"/>
      <xsl:apply-templates select="number:text-style"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="table:table-cell" mode="stylescells">
    <xsl:variable name="table" select="substring-before(@table:style-name,'.')"/>
    <xsl:variable name="cell"  select="string(.)"/> 
    <xsl:for-each select="/office:document-content/office:automatic-styles/style:style[@style:family='table-cell'][@style:name=current()/@table:style-name]">
      <style:style style:name="{substring-before(@style:name,'.')}.{$cell}" style:family="table-cell" style:display-name="{substring-before(@style:display-name,'.')}.{$cell}">
        <xsl:copy-of select="node()"/>
      </style:style>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="office:text">
    <xsl:copy>
      <xsl:apply-templates select="office:forms|text:sequence-decls"/>
      <xsl:apply-templates select="document($pivot)"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:html">
    <xsl:apply-templates select="html:body"/>
  </xsl:template>

  <xsl:template match="html:div [@class][@class='moduleinfo']" priority="999"/>
  <xsl:template match="html:span[@class='title_num']"/>


  <!-- generate index -->

  <xsl:template match="html:div[@class][@class='INDEX']" priority="999">
    <text:p text:style-name="{$mappings/index/title/@style}"><xsl:value-of select="html:p[@class='INDEX_titre']"/></text:p>
    <text:alphabetical-index text:style-name="{$tplindex/@text:style-name}" text:name="{html:p[@class='INDEX_titre']}">
      <xsl:copy-of select="$tplindex/text:alphabetical-index-source"/>
      <text:index-body>
        <xsl:apply-templates mode="index"/>
      </text:index-body>
    </text:alphabetical-index>
  </xsl:template>

  <xsl:template match="html:p[starts-with(@class, 'alphaindex entry level')]" mode="index">
    <xsl:variable name="level" select="substring-after(@class,'alphaindex entry level')"/>
    <xsl:variable name="lvlstyle">
      <xsl:value-of select="$tplindex/text:alphabetical-index-source/text:alphabetical-index-entry-template[@text:outline-level=$level]/@text:style-name"/>
    </xsl:variable>
    <text:p text:style-name="{$lvlstyle}"><xsl:value-of select="text()"/><text:tab/>0</text:p>
  </xsl:template>

  <!-- convert index marks -->
  <xsl:template match="html:span[@rel='index']|html:ins[@class='index']">
    <text:alphabetical-index-mark>
      <xsl:call-template name="index-mark-attributes">
	<xsl:with-param name="keys" select="normalize-space(.)"/>
      </xsl:call-template>
      <xsl:attribute name="text:main-entry">true</xsl:attribute>
    </text:alphabetical-index-mark>
    <!--
	text:string-value="entree3" 
	text:key1="n1"/>
    -->
  </xsl:template>

  <xsl:template name="index-mark-attributes">
    <xsl:param name="keys"/>
    <xsl:choose>
      <xsl:when test="not(contains($keys,':'))">
	<xsl:attribute name="text:string-value">
	  <xsl:value-of select="$keys"/>
	</xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="prefix" select="substring-before($keys,':')"/>
	<xsl:variable name="postfix" select="substring-after($keys,':')"/>
	<xsl:choose>
	  <xsl:when test="not(contains($postfix,':'))">
	    <xsl:attribute name="text:key1">
	      <xsl:value-of select="$prefix"/>
	    </xsl:attribute>
	    <xsl:call-template name="index-mark-attributes">
	      <xsl:with-param name="keys" select="$postfix"/>
	    </xsl:call-template>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:variable name="prefix2" select="substring-after($postfix,':')"/>
	    <xsl:variable name="postfix2" select="substring-after($postfix,':')"/>
	    <xsl:choose>
	      <xsl:when test="not(contains($postfix2,':'))">
		<xsl:attribute name="text:key2">
		  <xsl:value-of select="$prefix"/>
		</xsl:attribute>
		<xsl:call-template name="index-mark-attributes">
		  <xsl:with-param name="keys" select="$postfix"/>
		</xsl:call-template>
	      </xsl:when>
	      <xsl:otherwise>
		<xsl:call-template name="index-mark-attributes">
		  <xsl:with-param name="keys" select="$postfix"/>
		</xsl:call-template>
	      </xsl:otherwise>
	    </xsl:choose>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- generate table of contents -->
  <xsl:template match="html:div[@class][@class='TDM']" priority="999">
    <text:p text:style-name="{$mappings/toc/title/@style}"><xsl:value-of select="html:p[@class='TDM_titre']"/></text:p>

    <text:table-of-content text:style-name="{$tpltoc/@text:style-name}" text:name="{html:p[@class='TDM_titre']}">
      <xsl:copy-of select="$tpltoc/text:table-of-content-source"/>

      <text:index-body>
	<xsl:apply-templates mode="toc"/>
      </text:index-body>
    </text:table-of-content>
  </xsl:template>

  <xsl:template match="html:p[starts-with(@class,'TDM_niveau_')]" mode="toc">
    <xsl:variable name="level" select="substring-after(@class,'TDM_niveau_')"/>
    <xsl:if test="$level &lt;= $tpltoc/text:table-of-content-source/@text:outline-level">
      <xsl:variable name="lvlstyle">
	<xsl:value-of select="$tpltoc/text:table-of-content-source/text:table-of-content-entry-template[@text:outline-level=$level]/@text:style-name"/>
      </xsl:variable>
      <text:p text:style-name="{$lvlstyle}"><xsl:value-of select="."/><text:tab/>0</text:p>
    </xsl:if>
  </xsl:template>

  <xsl:template match="html:h1">
    <text:h text:outline-level="1">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates select="." mode="revmarks" />
    </text:h>
  </xsl:template>

  <xsl:template match="html:h2">
    <text:h text:outline-level="2">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates select="." mode="revmarks" />
    </text:h>
  </xsl:template>

  <xsl:template match="html:h3">
    <text:h text:outline-level="3">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates select="." mode="revmarks" />
    </text:h>
  </xsl:template>

  <xsl:template match="html:h4">
    <text:h text:outline-level="4">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates select="." mode="revmarks" />
    </text:h>
  </xsl:template>

  <xsl:template match="html:h5">
    <text:h text:outline-level="5">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates select="." mode="revmarks" />
    </text:h>
  </xsl:template>

  <xsl:template match="html:h6">
    <text:h text:outline-level="6">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates select="." mode="revmarks" />
    </text:h>
  </xsl:template>
  
  <xsl:template match="html:*" mode="revmarks">
   <xsl:variable name="linkid" select="//html:a[@class='voirpage' and @href=concat('#', ../@id)]" />
   <xsl:if test="not($linkid = '')">
      <text:reference-mark-start text:name="{../@id}"/>
   </xsl:if>
      <xsl:apply-templates/>
   <xsl:if test="not($linkid = '')">
      <text:reference-mark-end text:name="{../@id}"/>
   </xsl:if>
  </xsl:template>
  
  <xsl:template match="html:a[@class='voirpage']">
   <xsl:variable name="href" select="substring(@href, 2)" />
   <text:reference-ref text:reference-format="page" text:ref-name="{$href}">0</text:reference-ref>
  </xsl:template>
  
  <xsl:template match="html:p[starts-with(@class,'k ')]"/>
  
  <xsl:template match="html:p">
    <text:p>
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates/>
    </text:p>
  </xsl:template>

  <xsl:template match="html:ol">
    <text:list>
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates/>
    </text:list>
  </xsl:template>

  <xsl:template match="html:ul">
    <text:list>
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates/>
    </text:list>
  </xsl:template>

  <xsl:template match="html:li">
    <text:list-item>
      <xsl:if test="parent::html:ol and not(preceding-sibling::html:li)">
	<xsl:attribute name="text:start-value">1</xsl:attribute>
      </xsl:if>

<!--
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
-->
	  
      <xsl:if test="node()[not(self::html:h1 or self::html:h2 or self::html:h3 or self::html:h4 or self::html:h5 or self::html:h6 or self::html:ul or self::html:ol or self::html:dl or self::html:table or self::html:fieldset or self::html:p or self::html:div or self::html:pre or self::html:blockquote or self::html:address or self::html:hr or self::html:form )]">
	<text:p>
	  <xsl:call-template name="style">
	    <xsl:with-param name="ns" select="'text'"/>
	  </xsl:call-template>
	  <xsl:apply-templates select="node()[not(self::html:h1 or self::html:h2 or self::html:h3 or self::html:h4 or self::html:h5 or self::html:h6 or self::html:ul or self::html:ol or self::html:dl or self::html:table or self::html:fieldset or self::html:p or self::html:div or self::html:pre or self::html:blockquote or self::html:address or self::html:hr or self::html:form )]"/>
	</text:p>
      </xsl:if>
	<xsl:apply-templates select="node()[self::html:h1 or self::html:h2 or self::html:h3 or self::html:h4 or self::html:h5 or self::html:h6 or self::html:ul or self::html:ol or self::html:dl or self::html:table or self::html:fieldset or self::html:p or self::html:div or self::html:pre or self::html:blockquote or self::html:address or self::html:hr or self::html:form ]"/>
    </text:list-item>
  </xsl:template>


  <xsl:template match="html:dl">
    <text:p text:style-name="ela6-text">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates/>
    </text:p>
  </xsl:template>

  <xsl:template match="html:dt">
    <text:span text:style-name="kolekti-dt">
      <xsl:call-template name="style">
        <xsl:with-param name="ns" select="'text'"/>
      </xsl:call-template>
      <xsl:apply-templates/>
    </text:span>
  </xsl:template>

  <xsl:template match="html:dd">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="html:table" mode="styles">
    <xsl:variable name="tnum" select="count(preceding::html:table)+1"/>
    <xsl:variable name="class" select="@class"/>
    <xsl:variable name="tablestyle">
      <xsl:choose>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=$class]">
	  <xsl:value-of select="$class"/>
        </xsl:when>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=concat('autoformat_5f_',$class)]">
          <xsl:value-of select="concat('autoformat_5f_',$class)"/>
        </xsl:when>
      </xsl:choose>
    </xsl:variable>
    
    <!-- defines the table style for this instance -->

    <style:style style:name="Tableau{$tnum}" style:family="table">
      <xsl:choose>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=$class]">
	  <xsl:copy-of select="$automatic-styles/style:style[@style:family='table'][@style:name=$class]/*"/>
        </xsl:when>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=concat('autoformat_5f_',$class)]">
          <xsl:copy-of select="$automatic-styles/style:style[@style:family='table'][@style:name=concat('autoformat_5f_',$class)]/*"/>
        </xsl:when>
        <xsl:otherwise>
	  <style:table-properties  table:align="left" style:writing-mode="lr-tb"/>
        </xsl:otherwise>
      </xsl:choose>
    </style:style>

    <!-- defines the table columns styles for this instance -->

    <xsl:for-each select="html:tbody[1]/html:tr[1]/html:td|html:tbody[1]/html:tr[1]/html:th">
      <xsl:variable name="colid" select="translate(string(position()),'123456789','ABCDEFGHI')"/>
      <xsl:if test="$automatic-styles/style:style[@style:family='table-column'][@style:name=concat($tablestyle,'.',$colid)]">
        <style:style style:name="Tableau{$tnum}.{$colid}"  style:family="table-column">
          <xsl:copy-of select="$automatic-styles/style:style[@style:family='table-column'][@style:name=concat($tablestyle,'.',$colid)]/*"/>
        </style:style>
      </xsl:if>
    </xsl:for-each>
    
    <!-- defines the table cell aliases styles for this instance -->
  </xsl:template>

  <xsl:template match="html:table">
    <xsl:variable name="tnum" select="count(preceding::html:table)+1"/>
    <xsl:variable name="class" select="@class"/>
    <xsl:variable name="tablestyle">
      <xsl:choose>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=$class]">
	  <xsl:value-of select="$class"/>
        </xsl:when>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=concat('autoformat_5f_',$class)]">
          <xsl:value-of select="concat('autoformat_5f_',$class)"/>
        </xsl:when>
      </xsl:choose>
    </xsl:variable>

    <table:table table:name="Tableau{$tnum}" table:style-name="Tableau{$tnum}">
    <xsl:comment>a<xsl:value-of select="concat('Tableau',$tnum,'. ',$tablestyle)"/></xsl:comment>
    <xsl:for-each select="$template-tables[@table:name=$tablestyle]/table:table-column">

    <xsl:comment>col <xsl:value-of select="local-name()"/></xsl:comment>
       <xsl:copy>
         <xsl:copy-of select="@*"/>
         <xsl:attribute name="table:style-name">
           <xsl:value-of select="concat('Tableau',$tnum,'.')"/>
           <xsl:value-of select="substring-after(@table:style-name,'.')"/>
         </xsl:attribute>
       </xsl:copy>
    </xsl:for-each>

<!--
      <xsl:for-each select="html:tbody[1]/html:tr[1]/html:td|html:tbody[1]/html:tr[1]/html:th">
        <xsl:variable name="colid" select="translate(string(position()),'123456789','ABCDEFGHI')"/>
        <xsl:if test="$automatic-styles/style:style[@style:family='table-column'][@style:name=concat($tablestyle,'.',$colid)]">
	<table:table-column table:style-name="Tableau{$tnum}.{translate(string(position()),'123456789','ABCDEFGHI')}"/>
      </xsl:for-each>
-->
      <table:table-header-rows>
	<xsl:apply-templates select="html:thead/html:tr"/>
      </table:table-header-rows>
      <xsl:apply-templates select="html:tbody/html:tr"/>
      <xsl:apply-templates select="html:tfoot/html:tr"/>
    </table:table>
  </xsl:template>

  <xsl:template match="html:tr">
    <table:table-row>
      <xsl:apply-templates/>
    </table:table-row>
  </xsl:template>

  <xsl:template match="html:td|html:th">
    <xsl:variable name="tclass" select="ancestor::html:table/@class"/>
    <xsl:variable name="tablestyle">
      <xsl:choose>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=$tclass]">
	  <xsl:value-of select="$tclass"/>
        </xsl:when>
        <xsl:when test="@class and $automatic-styles/style:style[@style:family='table'][@style:name=concat('autoformat_5f_',$tclass)]">
          <xsl:value-of select="concat('autoformat_5f_',$tclass)"/>
        </xsl:when>
      </xsl:choose>
    </xsl:variable>

    <table:table-cell>
      <xsl:attribute name="table:style-name">
	<xsl:choose>
          <xsl:when test="$tablestyle and @class">
            <xsl:value-of select="concat($tablestyle,'.',@class)"/>
          </xsl:when>
          <xsl:when test="$tablestyle and parent::html:td/@class">
            <xsl:value-of select="concat($tablestyle,'.',parent::html:td/@class)"/>
          </xsl:when>
          <xsl:otherwise>kolekti-cell</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:if test="@rowspan">
         <xsl:attribute name="table:number-rows-spanned">
            <xsl:value-of select="@rowspan" />
         </xsl:attribute>
      </xsl:if>
      <xsl:if test="@colspan">
         <xsl:attribute name="table:number-columns-spanned">
            <xsl:value-of select="@colspan" />
         </xsl:attribute>
      </xsl:if>
      <xsl:choose>
	<xsl:when test="node()[1][self::html:p] or node()[1][self::html:ol] or node()[1][self::html:ul]">
	  <xsl:apply-templates/>
	</xsl:when>
	<xsl:otherwise>
	  <text:p>
	    <xsl:call-template name="style">
	      <xsl:with-param name="ns" select="'text'"/>
	    </xsl:call-template>
	    <xsl:apply-templates/>
	  </text:p>
	</xsl:otherwise>
      </xsl:choose>
    </table:table-cell>
  </xsl:template>

  <xsl:template match="html:img[@class]" mode="styles"> 
    <style:style style:name="fr{1+count(preceding::html:img)}" style:family="graphic" style:parent-style-name="{@class}">
    </style:style>
  </xsl:template>

  <xsl:template match="html:img" mode="styles"> 
    <style:style style:name="fr{1+count(preceding::html:img)}" style:family="graphic" style:parent-style-name="kolekti-gc">
    </style:style>
  </xsl:template>


  <xsl:template match="html:img[@class]"> 
    <draw:frame draw:style-name="fr{1+count(preceding::html:img)}" draw:name="images{1+count(preceding::html:img)}" text:anchor-type="paragraph"  draw:z-index="0">
      <xsl:call-template name="img-attrsize"/>
      <draw:image xlink:href="Pictures/{@newimgid}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
    </draw:frame>
  </xsl:template>

  <xsl:template match="html:img"> 
    <draw:frame draw:style-name="fr{1+count(preceding::html:img)}" draw:name="images{1+count(preceding::html:img)}" text:anchor-type="as-char"  draw:z-index="0">
      <xsl:call-template name="img-attrsize"/>
      <draw:image xlink:href="Pictures/{@newimgid}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
    </draw:frame>
  </xsl:template>

  <xsl:template name="img-attrsize">
      <xsl:attribute name="svg:height">
	<xsl:choose>
	  <!--<xsl:when test="@height and @orig_resh"><xsl:value-of select="@height div @orig_resh"/><xsl:text>in</xsl:text></xsl:when>-->
	  <xsl:when test="@height"><xsl:value-of select="@height * $imgzoom * 2.54"/>cm</xsl:when>
	  <xsl:when test="@orig_height and @orig_resh"><xsl:value-of select="(@orig_height div @orig_resh) * 2.54"/><xsl:text>cm</xsl:text></xsl:when>
	  <xsl:when test="@orig_height"><xsl:value-of select="@orig_height * $imgzoom * 2.54"/><xsl:text>cm</xsl:text></xsl:when>
	</xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="svg:width">
	<xsl:choose>
<!--	  <xsl:when test="@width and @orig_resw"><xsl:value-of select="@width div @orig_resw"/><xsl:text>in</xsl:text></xsl:when>-->
	  <xsl:when test="@width"><xsl:value-of select="@width * $imgzoom * 2.54"/>cm</xsl:when>
	  <xsl:when test="@orig_width and @orig_resw"><xsl:value-of select="(@orig_width div @orig_resw) * 2.54"/><xsl:text>cm</xsl:text></xsl:when>
	  <xsl:when test="@orig_width"><xsl:value-of select="@orig_width * $imgzoom * 2.54"/><xsl:text>cm</xsl:text></xsl:when>
	</xsl:choose>
      </xsl:attribute>
  </xsl:template>


  <xsl:template match="html:div[@class]">
    <xsl:variable name="class" select="@class"/>
    <xsl:choose>
      <xsl:when test="$mappings/map[@element='div'][(@class and &inclass;) or not(@class)]/frame">
	<xsl:variable name="framename">
	  <xsl:choose>
	    <xsl:when test="$mappings/map[@element='div'][(@class and &inclass;)]">
	      <xsl:choose>
		<xsl:when test="$mappings/map[@element='div'][(@class and &inclass;)]/frame/@style">
		  <xsl:value-of select="$mappings/map[@element='div'][(@class and &inclass;)]/frame/@style"/>
		</xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="$class"/>
                </xsl:otherwise>
	      </xsl:choose>
	    </xsl:when>
	    <xsl:when test="$mappings/map[@element='div'][not(@class)]/frame/@style">
	      <xsl:value-of select="$mappings/map[@element='div']/frame/@style"/>
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:value-of select="$class"/>
	    </xsl:otherwise>
	  </xsl:choose>
	</xsl:variable>

	<xsl:variable name="frameanchor">
	  <xsl:choose>
	    <xsl:when test="$mappings/map[@element='div'][(@class and &inclass;)]">
	      <xsl:choose>
		<xsl:when test="$mappings/map[@element='div'][(@class and &inclass;)]/frame/@anchor">
		  <xsl:value-of select="$mappings/map[@element='div'][(@class and &inclass;)]/frame/@anchor"/>
		</xsl:when>
		<xsl:otherwise>paragraph</xsl:otherwise>
	      </xsl:choose>
	    </xsl:when>
	    <xsl:when test="$mappings/map[@element='div'][not(@class)]/frame/@anchor">
	      <xsl:value-of select="$mappings/map[@element='div']/frame/@anchor"/>
	    </xsl:when>
	    <xsl:otherwise>paragraph</xsl:otherwise>
	  </xsl:choose>
	</xsl:variable>

        <xsl:choose>
	  <xsl:when test="$frameanchor = 'page'">
            <draw:frame draw:style-name="{$framename}" draw:name="Frame{generate-id()}" draw:z-index="0">
              <xsl:call-template name="FrameStyleSizeAttrs">
                <xsl:with-param name="frame" select="$framename"/>
              </xsl:call-template>
              <xsl:attribute name="text:anchor-type">
                <xsl:value-of select="$frameanchor"/>
              </xsl:attribute>
              <draw:text-box fo:min-height="1.041cm">
                <xsl:apply-templates/>
              </draw:text-box>
            </draw:frame>
          </xsl:when>
          <xsl:otherwise>
	    <xsl:variable name="anchorstyle">
	      <xsl:value-of select="$framename"/>
	      <xsl:text>Anchor</xsl:text>
	    </xsl:variable>

	    <text:p text:style-name="{$anchorstyle}">
	      <draw:frame draw:style-name="{$framename}" draw:name="Frame{generate-id()}" draw:z-index="0">
	        <xsl:call-template name="FrameStyleSizeAttrs">
	          <xsl:with-param name="frame" select="$framename"/>
	        </xsl:call-template>
	        <xsl:attribute name="text:anchor-type">
		  <xsl:value-of select="$frameanchor"/>
	        </xsl:attribute>
	        <draw:text-box fo:min-height="1.041cm">
	          <xsl:apply-templates/>
	        </draw:text-box>
	      </draw:frame>
	    </text:p>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
	<xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- inline elements -->

  <xsl:template match="html:sup">
    <text:span text:style-name="kolekti-sup">
      <xsl:apply-templates/>
    </text:span>
  </xsl:template>

  <xsl:template match="html:sub">
    <text:span text:style-name="kolekti-sub">
      <xsl:apply-templates/>
    </text:span>
  </xsl:template>

  <xsl:template match="html:i|html:em">
    <text:span text:style-name="kolekti-ital">
      <xsl:apply-templates/>
    </text:span>
  </xsl:template>

  <xsl:template match="html:b|html:strong">
    <text:span text:style-name="kolekti-bold">
      <xsl:apply-templates/>
    </text:span>
  </xsl:template>

  <xsl:template match="html:span">
    <xsl:choose>
      <xsl:when test='$mappings/footnote[@class=current()/@class]'>
	<text:span>
	  <text:note text:note-class="footnote">
            <text:note-citation></text:note-citation>
            <text:note-body>
              <text:p>
                <text:span>
		  <xsl:apply-templates/>
		</text:span>
	      </text:p>
	    </text:note-body>
	  </text:note>
	</text:span>
      </xsl:when>
      <xsl:otherwise>
	<text:span>
	  <xsl:call-template name="style">
	    <xsl:with-param name="ns" select="'text'"/>
	  </xsl:call-template>
	  <xsl:apply-templates/>
	</text:span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="html:br">
    <text:line-break/>
  </xsl:template>

  <xsl:template match="map/extension[@master-page-name]" mode="styles">
    <style:style style:name="{parent::map/@style}-{@class}" style:family="paragraph" style:parent-style-name="{parent::map/@style}" style:master-page-name="{@master-page-name}"/>
  </xsl:template>

  <xsl:template match="map/extension[@break-before]" mode="styles">
    <style:style style:name="{parent::map/@style}-{@class}" style:family="paragraph" style:parent-style-name="{parent::map/@style}">
      <style:paragraph-properties fo:break-before="page"/>
    </style:style>
  </xsl:template>




  <xsl:template name="style">
    <xsl:param name="ns"/>

    <xsl:variable name="class">
      <xsl:value-of  select="@class"/>
    </xsl:variable>

    <xsl:variable name="name">
      <xsl:value-of  select="local-name(.)"/>
    </xsl:variable>

    <xsl:variable name="parent">
      <xsl:value-of  select="local-name(parent::*)"/>
    </xsl:variable>

    <xsl:variable name="stylename">
      <xsl:choose>

	<xsl:when test="@class">
	  <!-- <!ENTITY inclass "contains(concat(' ',normalize-space(current()/@class),' '),@class)"> -->
	  <xsl:choose>

	    <!-- element, class and parent -->
	    <xsl:when test="$mappings/map[@element=$name][@parent=$parent][@class][&inclass;][@style]">
	      <xsl:value-of select="$mappings/map[@element=$name][@parent=$parent][@class][&inclass;]/@style"/>
	      <xsl:if test="$mappings/map[@element=$name][@parent=$parent][@class][&inclass;]/extension[&inclass;]">
		<xsl:text>-</xsl:text>
		<xsl:value-of select="$mappings/map[@element=$name][@parent=$parent][@class][&inclass;]/extension[&inclass;]/@class"/>
	      </xsl:if>
	    </xsl:when>

	    <!-- element, class  -->

	    <xsl:when test="$mappings/map[@element=$name][not(@parent)][@class][&inclass;][@style]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@parent)][@class][&inclass;]/@style"/>
	      <xsl:if test="$mappings/map[@element=$name][not(@parent)][@class][&inclass;]/extension[&inclass;]">
		<xsl:text>-</xsl:text>
		<xsl:value-of select="$mappings/map[@element=$name][not(@parent)][@class][&inclass;]/extension[&inclass;]/@class"/>
	      </xsl:if>
	    </xsl:when>

	    <!-- class  -->

	    <xsl:when test="$mappings/map[not(@element)][not(@parent)][@class][&inclass;][@style]">
	      <xsl:value-of select="$mappings/map[not(@element)][not(@parent)][@class][&inclass;]/@style"/>
	      <xsl:if test="$mappings/map[not(@element)][not(@parent)][@class][&inclass;]/extension[&inclass;]">
		<xsl:text>-</xsl:text>
		<xsl:value-of select="$mappings/map[not(@element)][not(@parent)][@class][&inclass;]/extension[&inclass;]/@class"/>
	      </xsl:if>
	    </xsl:when>

	    <!-- element and parent -->

	    <xsl:when test="$mappings/map[@element=$name][not(@class)][@parent=$parent][@style]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][@parent=$parent]/@style"/>
	      <xsl:if test="$mappings/map[@element=$name][not(@class)][@parent=$parent]/extension[&inclass;]">
		<xsl:text>-</xsl:text>
		<xsl:value-of select="$mappings/map[@element=$name][not(@class)][@parent=$parent]/extension[&inclass;]/@class"/>
	      </xsl:if>
	    </xsl:when>

	    <!-- element with extension -->
	    <xsl:when test="$mappings/map[@element=$name][not(@class)][not(@parent)][@style]/extension[&inclass;]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][not(@parent)]/@style"/>
	      <xsl:text>-</xsl:text>
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][not(@parent)]/extension[&inclass;]/@class"/>
	    </xsl:when>

	    <xsl:otherwise>
	      <xsl:value-of select="@class"/>
	    </xsl:otherwise>
	  </xsl:choose>

	</xsl:when>

	<xsl:otherwise>
	  <xsl:choose>

	    <!-- element and parent  -->

	    <xsl:when test="$mappings/map[@element=$name][not(@class)][@parent=$parent][@style]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][@parent=$parent]/@style"/>
	    </xsl:when>

	    <!-- element  -->

	    <xsl:when test="$mappings/map[@element=$name][not(@class)][not(@parent)][@style]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][not(@parent)]/@style"/>
	    </xsl:when>

	  </xsl:choose>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="framename">
      <xsl:choose>
	<xsl:when test="@class">
	  <xsl:choose>

	    <!-- element, class and parent -->
	    <xsl:when test="$mappings/map[@element=$name][@parent=$parent][@class][&inclass;][@addframe]">
	      <xsl:value-of select="$mappings/map[@element=$name][@parent=$parent][@class][&inclass;]/@addframe"/>
	    </xsl:when>

	    <!-- element, class  -->
	    <xsl:when test="$mappings/map[@element=$name][not(@parent)][@class][&inclass;][@addframe]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@parent)][@class][&inclass;]/@addframe"/>
	    </xsl:when>

	    <!-- class  -->
	    <xsl:when test="$mappings/map[not(@element)][not(@parent)][@class][&inclass;][@addframe]">
	      <xsl:value-of select="$mappings/map[not(@element)][not(@parent)][@class][&inclass;]/@addframe"/>
	    </xsl:when>

	    <!-- element and parent -->

	    <xsl:when test="$mappings/map[@element=$name][not(@class)][@parent=$parent][@addframe]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][@parent=$parent]/@addframe"/>
	    </xsl:when>
	  </xsl:choose>
	</xsl:when> <!-- @class -->

	<xsl:otherwise>
	  <xsl:choose>

	    <!-- element and parent  -->
	    <xsl:when test="$mappings/map[@element=$name][not(@class)][@parent=$parent][@addframe]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][@parent=$parent]/@addframe"/>
	    </xsl:when>

	    <!-- element  -->
	    <xsl:when test="$mappings/map[@element=$name][not(@class)][not(@parent)][@addframe]">
	      <xsl:value-of select="$mappings/map[@element=$name][not(@class)][not(@parent)]/@addframe"/>
	    </xsl:when>

	  </xsl:choose>
	</xsl:otherwise>
      </xsl:choose>

      
    </xsl:variable>

    <xsl:if test="$stylename!=''">
      <xsl:attribute name="{$ns}:style-name">
	<xsl:value-of select="$stylename"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:if test="$framename!=''">

      <draw:frame draw:style-name="{$framename}" draw:name="Cadre{generate-id()}" text:anchor-type="paragraph">
	<!-- get width and height from style -->
	<xsl:call-template name="FrameStyleSizeAttrs">
	  <xsl:with-param name="frame" select="$framename"/>
	</xsl:call-template>
	<draw:text-box>
	  <text:p><!--
	    <xsl:value-of select="local-name($stylesdoc/office:styles/style:style[1])"/>
	  <xsl:call-template name="FrameStyleWidth">
	    <xsl:with-param name="frame" select="$framename"/>
	  </xsl:call-template>
	  <xsl:text>x</xsl:text>
	  <xsl:call-template name="FrameStyleHeight">
	    <xsl:with-param name="frame" select="$framename"/>
	  </xsl:call-template>

	  --></text:p>
	</draw:text-box>
      </draw:frame>
    </xsl:if>
  </xsl:template>


  <xsl:template name="FrameStyleWidth">
    <xsl:param name="frame"/>

    <xsl:value-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@svg:width"/>

  </xsl:template>

  <xsl:template name="FrameStyleHeight">
    <xsl:param name="frame"/>
    <xsl:value-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@svg:height"/>
  </xsl:template>

  <xsl:template name="FrameStyleSizeAttrs">
    <xsl:param name="frame"/>
    <xsl:copy-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@*"/>
    <!--
    <xsl:copy-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@svg:width"/>
    <xsl:copy-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@fo:min-width"/>
    <xsl:copy-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@style:rel-width"/>
    <xsl:copy-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@svg:height"/>
    <xsl:copy-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@fo:min-height"/>
    <xsl:copy-of select="$stylesdoc/office:styles/style:style[@style:name=$frame][@style:family='graphic']/style:graphic-properties/@style:rel-height"/>
    -->
  </xsl:template>
</xsl:stylesheet>
