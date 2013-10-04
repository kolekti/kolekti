<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:html="http://www.w3.org/1999/xhtml"
		xmlns="http://www.w3.org/1999/xhtml"
      exclude-result-prefixes="html"
		version='1.0'
>

  <xsl:output method="xml" encoding="utf-8" omit-xml-declaration="no"/>

  <xsl:param name="css"/>

  <xsl:variable name="has-toc">
    <xsl:value-of select="count(//html:div[@class='TDM'])"/>
  </xsl:variable>

  <xsl:template match="html:head">
    <xsl:copy>
      <xsl:apply-templates select="html:title"/>
      <xsl:comment> metadata </xsl:comment>
      <meta name="version" content="S5 1.1" />
      <meta name="presdate" content="20050728" />
      <meta name="author" content="Eric A. Meyer" />
      <meta name="company" content="Complex Spiral Consulting" />
      <xsl:comment> configuration parameters </xsl:comment>
      <meta name="defaultView" content="slideshow" />
      <meta name="controlVis" content="hidden" />
      <xsl:comment> style sheet links </xsl:comment>
      <link rel="stylesheet" href="ui/default/slides.css" type="text/css" media="projection" id="slideProj" />
      <link rel="stylesheet" href="ui/default/outline.css" type="text/css" media="screen" id="outlineStyle" />
      <link rel="stylesheet" href="ui/default/print.css" type="text/css"  media="print" id="slidePrint" />
      <link rel="stylesheet" href="ui/default/opera.css" type="text/css"  media="projection" id="operaFix" />
      <xsl:if test="$css">
	<link rel="stylesheet" href="ui/kolekti/{$css}.css" type="text/css"
	      media="screen" id="userStyle" />
      </xsl:if>
      <xsl:comment> S5 JS </xsl:comment>
      <script type="text/javascript" src="ui/default/slides.js">
	<xsl:text>&#x0A;</xsl:text>
      </script>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:body"> 
    <div class="layout">
      
      <div id="controls">
	<xsl:comment> DO NOT EDIT </xsl:comment>
      </div>
      
      <div id="currentSlide">
	<xsl:comment> DO NOT EDIT </xsl:comment>
      </div>

      <div id="header">
	<xsl:comment> </xsl:comment>
      </div>
      
      <div id="footer">
	<h2><xsl:value-of select="/html:html/html:head/html:title"/></h2>
	<p style="font-size:50%">Ce document est généré par <a href="http://www.kolekti.org/">kOLEKTi</a> et présenté par <a href="http://www.meyerweb.com/eric/tools/s5/credits.html">S5</a></p>
      </div>
    </div>

    <div class="presentation">
      <div class="slide">
	<h1><xsl:value-of select="/html:html/html:head/html:title"/></h1>
	<div id="presentation-info">
	  <xsl:copy-of select=".//html:div[@class='presinfo']//html:*[@id='presentation-subtitle']"/>
	  <xsl:copy-of select=".//html:div[@class='presinfo']//html:*[@id='presentation-author']"/>
	  <xsl:copy-of select=".//html:div[@class='presinfo']//html:*[@id='presentation-company']"/>
	  <xsl:copy-of select=".//html:div[@class='presinfo']//html:*[@id='presentation-place']"/>
	  <xsl:copy-of select=".//html:div[@class='presinfo']//html:*[@id='presentation-date']"/>
	</div>
      </div>
      <xsl:if test="$has-toc">
	<div class="slide">
	  <h1><xsl:value-of select="/html:html/html:head/html:title"/></h1>
	  <div class="presentation-toc">
	    <ul>
	      <xsl:apply-templates select="html:div[@class='section']" mode="TOC"/>
	    </ul>
	  </div>
	</div>
      </xsl:if>
      <xsl:apply-templates select="html:div[@class='section']|html:div[@class='module']"/>
    </div>
  </xsl:template>

  <!-- ignore the tdm from pivot -->
  <xsl:template match="html:div[@class='TDM']"/>

  <xsl:template match="html:div[@class='section']" mode="TOC">
    <xsl:param name="curid">0</xsl:param>
    <li>
      <xsl:choose>
	<xsl:when test="$curid=0"/>
	<xsl:when test="generate-id()=$curid">
	  <xsl:attribute name="class">current-section</xsl:attribute>
	</xsl:when>
	<xsl:when test="not(descendant::html:div[@class='section'][generate-id()=$curid])">
	  <xsl:attribute name="class">light-section</xsl:attribute>
	</xsl:when>
      </xsl:choose>
      <xsl:apply-templates select="(html:h1|html:h2|html:h3|html:h4|html:h5)[1]/node()"/>
      <xsl:if test=".//html:div[@class='section'][generate-id()=$curid]">
	<ul>
	  <xsl:choose>
	    <xsl:when test="html:div[@class='section'][generate-id()=$curid]">
	      <xsl:apply-templates select="html:div[@class='section']" mode="TOC">
		<xsl:with-param name="curid" select="$curid"/>
	      </xsl:apply-templates>
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:apply-templates select="html:div[@class='section'][descendant-or-self::html:div[generate-id()=$curid]]" mode="TOC">
		<xsl:with-param name="curid" select="$curid"/>
	      </xsl:apply-templates>
	    </xsl:otherwise>
	  </xsl:choose>
	</ul>
      </xsl:if>
    </li>
  </xsl:template>

  <!-- section level : may generate a toc slide -->
  <xsl:template match="html:div[@class='section']">
    <xsl:if test="$has-toc and html:div[@class='module'][not(.//html:div[@class='presinfo'])]">
      <div class="slide">
	<h1><xsl:value-of select="/html:html/html:head/html:title"/></h1>
	<div class="presentation-toc">
	  <ul>
	    <xsl:variable name="curid" select="generate-id()"/>
	    <xsl:apply-templates select="/html:html/html:body/html:div[@class='section']" mode="TOC">
	      <xsl:with-param name="curid" select="$curid"/>
	    </xsl:apply-templates>
	  </ul>
	</div>
      </div>
    </xsl:if>
    <xsl:apply-templates select="html:div[@class='section']|html:div[@class='module']"/>
  </xsl:template>


  <!-- this is a module with slides inside, silently ignore the div -->
  <xsl:template match="html:div[@class='module'][.//html:div[@class='slide']][not(.//html:div[@class='presinfo'])]">
    <xsl:apply-templates select=".//html:div[@class='slide']"/>
  </xsl:template>

  <!-- this is a module without slides inside, generate a div slide -->
  <xsl:template match="html:div[@class='module'][not(.//html:div[@class='slide'])][not(.//html:div[@class='presinfo'])]">
    <div class="slide">
      <xsl:call-template name="slide-content"/>
    </div>
  </xsl:template>

  <xsl:template match="html:div[@class='module'][.//html:div[@class='presinfo']]"/>

  <xsl:template match="html:div[@class='slide']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:call-template name="slide-content"/>
    </xsl:copy>
  </xsl:template>


  <xsl:template name="slide-content">
    <xsl:variable name="depth">
      <xsl:value-of select="substring-after(local-name((.//html:h1|.//html:h2|.//html:h3|.//html:h4|.//html:h5|.//html:h6)[1]),'h') - 1"/>
    </xsl:variable>
    <xsl:apply-templates mode="slide-content">
      <xsl:with-param name="depth" select="$depth"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="html:h1|html:h2|html:h3|html:h4|html:h5|html:h6" mode="slide-content">
    <xsl:param name="depth"/>
    <xsl:variable name="hd" select="substring-after(local-name(),'h')"/>
    <xsl:element name="h{$hd - $depth}">
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates select="node()" mode="slide-content">
	<xsl:with-param name="depth" select="$depth"/>
      </xsl:apply-templates>
    </xsl:element>
  </xsl:template>

  <xsl:template match="node()|@*" mode="slide-content">
    <xsl:param name="depth"/>
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="slide-content">
	<xsl:with-param name="depth" select="$depth"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="node()|@*">
    <xsl:param name="depth"/>
    <xsl:copy>
      <xsl:apply-templates select="node()|@*">
	<xsl:with-param name="depth" select="$depth"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

  <!-- remove the titles numerotation -->
  <xsl:template match="html:span[@class='title_num']" mode="slide-content"/>
  <xsl:template match="html:span[@class='title_num']"/>

  <!-- remove the modules meta-information -->
  <xsl:template match="html:div[@class='moduleinfo']" mode="slide-content"/>
  <xsl:template match="html:div[@class='moduleinfo']"/>
  

  <xsl:template match="html:img" mode="slide-content">
   <xsl:variable name="src">
      <xsl:choose>
         <xsl:when test="starts-with(@src, 'http://')">
            <xsl:value-of select="@newsrc" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>medias/</xsl:text>
            <xsl:value-of select="substring-after(@src, 'medias/')" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <img src="{$src}" alt="{@alt}" title="{@title}" />
  </xsl:template>
  
  <xsl:template match="html:embed" mode="slide-content">
   <xsl:variable name="src">
      <xsl:choose>
         <xsl:when test="starts-with(@src, 'http://')">
            <xsl:value-of select="@src" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>medias/</xsl:text>
            <xsl:value-of select="substring-after(@src, 'medias/')" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <embed width="{@width}" height="{@height}" type="{@type}" pluginspage="{@pluginspage}" src="{$src}" />
  </xsl:template>

</xsl:stylesheet>