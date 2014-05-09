<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:exsl="http://exslt.org/common"
                xmlns:kfp="kolekti:extensions:functions:publication"

                extension-element-prefixes="exsl kfp"
                exclude-result-prefixes="html exsl kfp">

  <xsl:import href="default.xsl" />
  <xsl:import href="TEMPLATEFILE" id="template" />

  <xsl:include href="search.xsl" />

  <xsl:output method="html" indent="yes" />

  <xsl:param name="pubdir" />
  <xsl:param name="templatedir" />
  <xsl:param name="templatetrans" />
  <xsl:param name="template" />
  <xsl:param name="label" />
  <xsl:param name="urlform" />
  <xsl:param name="css" />

  <xsl:variable name="helpname">easiware</xsl:variable>
  <xsl:variable name="modules" select="//html:div[@class='module']" />
  <xsl:variable name="mainsections" select="/html:html/html:body/html:div[@class='section']" />

  <xsl:variable name="pubtitle" select="/html:html/html:head/html:title/text()" />

  <xsl:variable name="upubdir">
    <xsl:if test="not(starts-with($pubdir,'/'))">
      <xsl:text>/</xsl:text>
    </xsl:if>
    <xsl:call-template name="slashes">
      <xsl:with-param name="text" select="$pubdir" />
    </xsl:call-template>
  </xsl:variable>

  <!-- Main template -->
  <xsl:template match="/">
    
    <xsl:apply-templates select="/html:html/html:body" mode="search-file" />
    <exsl:document href="file://{$upubdir}/{$label}/index.html"
                   method="html"
                   indent="yes"
                   encoding="utf-8">
      <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#10;</xsl:text>
      
      <xsl:comment>[if lt IE 7]>      &lt;html class="no-js lt-ie9 lt-ie8 lt-ie7"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if IE 7]>         &lt;html class="no-js lt-ie9 lt-ie8"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if IE 8]>         &lt;html class="no-js lt-ie9"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if gt IE 8]>&lt;!</xsl:comment> <html class="no-js"> <xsl:comment>&lt;![endif]</xsl:comment>

        <head>
          <xsl:call-template name="generate-header" />
        </head>
        <body data-spy="scroll">
            <xsl:call-template name="index-body" />
            <xsl:call-template name="generate-videos-modal" />
        </body>
      </html>
    </exsl:document>
    <!-- generate content files -->
    <xsl:apply-templates select="$modules" />
    <!-- generate summary index files -->
    <xsl:apply-templates select="$mainsections" mode="summary" />
  </xsl:template>

  <!-- Main topics template -->
  <xsl:template match="html:div[@class='module']">
    <xsl:variable name="filename">
      <xsl:call-template name="modfile" />
    </xsl:variable>
    <exsl:document href="file://{$upubdir}/{$label}/{$filename}"
                   method="html"
                   indent="yes"
                   encoding="utf-8">
      <xsl:variable name="modtitle">
        <xsl:call-template name="modtitle" />
      </xsl:variable>
      <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#10;</xsl:text>
      <xsl:comment>[if lt IE 7]>      &lt;html class="no-js lt-ie9 lt-ie8 lt-ie7"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if IE 7]>         &lt;html class="no-js lt-ie9 lt-ie8"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if IE 8]>         &lt;html class="no-js lt-ie9"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if gt IE 8]>&lt;!</xsl:comment> <html class="no-js"> <xsl:comment>&lt;![endif]</xsl:comment>
        <head>
          <xsl:call-template name="generate-header" />
        </head>
        <body data-spy="scroll">
            <xsl:call-template name="topic-body" />
            <xsl:call-template name="generate-videos-modal" />
        </body>
      </html>
    </exsl:document>
  </xsl:template>


  <!-- Section template -->
  <xsl:template match="html:div[@class='section']">
    <xsl:param name="limit" select="1"/>
    
    <xsl:call-template name="section-title">
      <xsl:with-param name="title" select="translate(html:h1, '[]', '')" />
    </xsl:call-template>

    <!-- glitch for numbering the first section in summaries -->
    <xsl:variable name="typelist">
      <xsl:choose>
	<xsl:when test="preceding-sibling::html:div[@class='section']">ul</xsl:when>
	<xsl:otherwise>ol</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:element name="{$typelist}">
      <!--[not(html:div[@class='moduleinfo'][html:p[html:span[@class='infolabel'][. = 'topic_control']][html:span[@class='infovalue'][. = 'NO_TDM']]])]-->
      <xsl:choose>
	<xsl:when test="$limit = 1">
	  <xsl:apply-templates select="html:div[@class='module'][$max-section-topics = number(0) or count(preceding-sibling::html:div[@class='module'][not(html:div[@class='moduleinfo'][html:p[html:span[@class='infolabel'][. = 'topic_control']][html:span[@class='infovalue'][. = 'NO_TDM']]])]) &lt; $max-section-topics][not(html:div[@class='moduleinfo'][html:p[html:span[@class='infolabel'][. = 'topic_control']][html:span[@class='infovalue'][. = 'NO_TDM']]])]" mode="modcontent" />
	</xsl:when>
	<xsl:otherwise>
	  <xsl:apply-templates select="html:div[@class='module'][not(html:div[@class='moduleinfo'][html:p[html:span[@class='infolabel'][. = 'topic_control']][html:span[@class='infovalue'][. = 'NO_TDM']]])]" mode="modcontent" />
	</xsl:otherwise>
      </xsl:choose>
    </xsl:element>
    
    <xsl:if test="$limit  and count(html:div[@class='module']) &gt; $max-section-topics">
      <xsl:variable name="cursection" select="count(preceding::html:div[@class='section'])+1" />
      <xsl:call-template name="section-more">
	<xsl:with-param name="link" select="concat('summary',$cursection,'.html')"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--  Section template for summary -->
  <xsl:template match="html:div[@class='section']" mode="summary">
    <xsl:variable name="cursection" select="count(preceding::html:div[@class='section'])+1" />
    <xsl:call-template name="generate-topics-summary">
        <xsl:with-param name="filename" select="concat('summary', $cursection, '.html')" />
    </xsl:call-template>
  </xsl:template>

  <!--  Module template for content -->
  <xsl:template match="html:div[@class='module']" mode="modcontent">
    <li>
      <xsl:if test=".//html:div[@class='demo video']">
	  <xsl:attribute name="class">video-topic</xsl:attribute>
      </xsl:if>
      <a>
	<xsl:attribute name="href">
	  <xsl:call-template name="modfile" />
	</xsl:attribute>
        <xsl:call-template name="topic-item">
	  <xsl:with-param name="title">
	    <xsl:call-template name="modtitle" />
	  </xsl:with-param>
	</xsl:call-template>
      </a>
    </li>
  </xsl:template>

  <xsl:template match="html:div[@class='moduleinfo']" mode="modcontent" />

  <xsl:template match="html:*|@*" mode="modcontent">
    <xsl:apply-imports/>
    <xsl:copy>
        <xsl:apply-templates select="node()|@*" mode="modcontent" />
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:div[@class='section']/html:h1">
    <xsl:value-of select="translate(., '[]', '')" />
  </xsl:template>


  <xsl:template match="html:*[@class='attention']" mode="modcontent">
    <xsl:copy>
        <xsl:attribute name="class">
            <xsl:text>alert alert-info</xsl:text>
        </xsl:attribute>
        <xsl:apply-templates select="node()"  mode="modcontent"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:img" mode="modcontent">
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
    <img src="{$src}" alt="{@alt}" title="{@title}">
      <xsl:if test="@style">
        <xsl:attribute name="style"><xsl:value-of select="@style" /></xsl:attribute>
      </xsl:if>
    </img>
  </xsl:template>

  <xsl:template match="html:div[@class='demo video']|html:div[@class='expert video']" mode="modcontent" />

  <xsl:template match="html:div[@class='demo video']|html:div[@class='expert video']" mode="video">
    <p class="vidsnippet">
        <a href="{html:a/@href}">
            <span class="vidthumb"><xsl:apply-templates select="html:img" mode="modcontent" /></span>
	    <span class="vidauteur"><xsl:value-of select="html:span[@class='author']" /></span>
	    <span class="viddate"><xsl:value-of select="html:span[@class='date']" /></span>
            <span class="label label-info"><xsl:value-of select="html:span[@class='duration']" /></span>
            <span class="vidtitle"><xsl:value-of select="html:span[@class='label']" /></span>
        </a> 
    </p>
  </xsl:template>

  <xsl:template match="html:span[@class='Policepardéfaut']" mode="modcontent" >
    <xsl:apply-templates mode="modcontent"/>
  </xsl:template>

  <xsl:template match="html:li/node()[1][self::text()][normalize-space(.) = '']" mode="modcontent" />

  <!-- conversion des liens internes au pivot -->
  
  <xsl:template match="html:a[starts-with(@href,'#')]" mode="modcontent" >
    <xsl:copy>
      <xsl:apply-templates select="@*" mode="modcontent"/>
      <xsl:attribute name="href">
	<xsl:value-of select="//html:div[@id=substring-after(current()/@href,'#')]/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel'][.='topic_file']]/html:span[@class='infovalue']"/>
	<xsl:text>.html</xsl:text>
      </xsl:attribute>

      <xsl:apply-templates select="node()" mode="modcontent"/>
    </xsl:copy>
  </xsl:template>

  <!-- Generate content header  -->
  <xsl:template name="generate-header">
    <title><xsl:value-of select="$pubtitle" /></title>
    <meta charset="UTF-8" />
    <!-- Always force latest IE rendering engine (even in intranet) & Chrome Frame
    Remove this if you use the .htaccess -->
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta content="" name="author" />
    <meta name="robots" content="all" />
    <meta name="Keywords" content="" />
    <meta name="Description" content="" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />

    <link href='http://fonts.googleapis.com/css?family=Nunito:700' rel='stylesheet' type='text/css'/>

    <xsl:if test="$css">
      <!-- favicon -->
      <link rel="shortcut icon" href="usercss/{$css}.parts/ico/favicon.ico" />
      <!-- css -->
      <link rel="stylesheet" href="usercss/{$css}.parts/css/bootstrap.css" type="text/css" />
      <link rel="stylesheet" href="usercss/{$css}.parts/css/responsive.css" type="text/css" />
      <link rel="stylesheet" href="usercss/{$css}.parts/{$css}.css" type="text/css" />

    </xsl:if>
    
    <!-- js -->
    <script src="js/respond.min.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>
    <script src="js/jquery-1.8.1.min.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>
    <script src="js/bootstrap.min.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>
<!--    <script src="js/less-1.3.0.min.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>-->
    <xsl:text disable-output-escaping="yes">
    &lt;!--[if lt IE 9]&gt;
    </xsl:text>
    <script src="http://html5shim.googlecode.com/svn/trunk/html5.js" type="text/javascript">
    <xsl:text>&#x0D;</xsl:text></script>
    <xsl:text disable-output-escaping="yes">&lt;![endif]--&gt;</xsl:text>
    <xsl:apply-templates select="/html:html/html:head" mode="search-header" />
  </xsl:template>

  <!-- Generate list of sections -->
  <xsl:template name="sections-list">
    <xsl:param name="class" select="'nav nav-list'" />
    <xsl:apply-templates select="/html:html/html:body/html:div[@class='section']/html:h1" mode="list">
      <xsl:with-param name="curnode" select="." />
    </xsl:apply-templates>
  </xsl:template>

  <!--  Module template for content -->
  <xsl:template match="html:div[@class='section']/html:h1" mode="list">
    <xsl:param name="curnode" />
    <xsl:variable name="secpos" select="count(../preceding-sibling::html:div[@class='section'])+1" />
    <xsl:call-template name="section-list-item">
      <xsl:with-param name="class">
        <xsl:choose>
	  <xsl:when test="$curnode[@class='module'] and $curnode/.. = ..">active</xsl:when>
	  <xsl:when test="$curnode[@class='section'] and $curnode = ..">active</xsl:when>
        </xsl:choose>
	<xsl:choose>
	  <xsl:when test="not(../preceding-sibling::html:div[@class='section'])"> first</xsl:when>
	  <xsl:when test="not(../following-sibling::html:div[@class='section'])"> last</xsl:when>
	</xsl:choose>
      </xsl:with-param>
      <xsl:with-param name="link" select="concat('summary',$secpos,'.html')"/>
      <xsl:with-param name="label">
	<xsl:choose>
	  <xsl:when test="contains(., '[') and contains(., ']')">
	    <xsl:value-of select="substring-before(substring-after(., '['), ']')" />
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="." />
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>


  <!-- Generate list of topics from section -->
  <xsl:template name="section-topics-list">
    <xsl:param name="section" select="number(1)" />
    <xsl:apply-templates select="/html:html/html:body/html:div[@class='section'][$section]">
      <xsl:with-param name="limit" select="1"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- Generate summary file for each main section -->
  <xsl:template name="generate-topics-summary">
    <xsl:param name="filename" />
    <exsl:document href="file://{$upubdir}/{$label}/{$filename}" method="html" indent="yes" encoding="utf-8">
      <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;&#10;</xsl:text>
      <xsl:comment>[if lt IE 7]>      &lt;html class="no-js lt-ie9 lt-ie8 lt-ie7"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if IE 7]>         &lt;html class="no-js lt-ie9 lt-ie8"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if IE 8]>         &lt;html class="no-js lt-ie9"> &lt;![endif]</xsl:comment>
      <xsl:comment>[if gt IE 8]>&lt;!</xsl:comment> <html class="no-js"> <xsl:comment>&lt;![endif]</xsl:comment>
        <head>
          <xsl:call-template name="generate-header" />
        </head>
        <body data-spy="scroll">
            <xsl:call-template name="section-body" />
	    <xsl:call-template name="generate-videos-modal" />
        </body>
      </html>
    </exsl:document>
  </xsl:template>

  <!-- Content of summary file -->
  <xsl:template name="summary-content">
    <xsl:apply-templates select=".">
      <xsl:with-param name="limit" select="0"/>
    </xsl:apply-templates>

    <!--
    <h2><xsl:apply-templates select="html:h1" /></h2>
    <ul class="summary-content">
        <xsl:apply-templates select="html:div[@class='module']" mode="modcontent" />
    </ul>
    -->
  </xsl:template>

  <!--  Content of topic file -->
  <xsl:template name="topic-content">
    <div class="topic">
      <!-- module title -->
      <xsl:apply-templates select="(.//html:h1|.//html:h2|.//html:h3|.//html:h4|.//html:h5|.//html:h6|.//html:dt)[1]" mode="modcontenttitle"/>
      <div class="topiccontent">
        <xsl:apply-templates mode="modcontent" />
      </div>
    </div>
    <div class="search">
        <xsl:text> </xsl:text>
    </div>
  </xsl:template>

  <xsl:template match="html:h1|html:h2|html:h3|html:h4|html:h5|html:h6|html:dt" mode="modcontenttitle">
    <h2><xsl:apply-templates mode="modcontent"/></h2>
  </xsl:template>

  <xsl:template match="html:h1|html:h2|html:h3|html:h4|html:h5|html:h6" mode="modcontent">
    <xsl:variable name="titlelevel" select="number(substring(local-name(),2))"/>
    <xsl:comment>titlelevel : <xsl:value-of select="$titlelevel"/></xsl:comment>
    <xsl:variable name="sectionlevel" select="count(ancestor::html:div[@class='section'])"/>
    <xsl:comment>sectionlevel : <xsl:value-of select="$sectionlevel"/></xsl:comment>
    <xsl:variable name="outlevel" select="$titlelevel - $sectionlevel + 1"/>
    <xsl:comment>outlevel : <xsl:value-of select="$outlevel"/></xsl:comment>
    <xsl:choose>
      <xsl:when test="$outlevel &lt;=2"/>
      <xsl:when test="$outlevel &lt;=6">
	<xsl:element name="h{$outlevel}">
	  <xsl:apply-templates mode="modcontent"/>
	</xsl:element>
      </xsl:when>  
      <xsl:otherwise>
	<p class="intertitre"><xsl:apply-templates mode="modcontent"/></p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Contact template -->
  <xsl:template name="contact">
    <h5>Contactez nos experts</h5>
    <p>La réponse à votre question n'est pas ici ?</p>
    <button class="btn btn-primary" data-toggle="modal" href="#contact-modal">Posez votre question</button>

    <div aria-hidden="true" aria-labelledby="contact-modal-label" role="dialog" tabindex="-1" class="modal hide fade" id="contact-modal" style="display: none;">
        <div class="modal-header">
            <button aria-hidden="true" data-dismiss="modal" class="close" type="button">×</button>
            <h3 id="contact-modal-label">Contactez nos experts</h3>
        </div>
        <div class="modal-body" id="contact-modal-content">
            <iframe src="{$urlform}" frameborder="0"><xsl:text> </xsl:text></iframe>
        </div>
    </div>
  </xsl:template>

  <!-- Video template -->
  <xsl:template name="generate-videos-modal">
    <xsl:if test="$videos-modal = '1'">
        <script type="text/javascript">
            $("p.vidsnippet a").click(function(e) {
                e.preventDefault();
                var url = $(this).attr('href');
                var label = $(this).find('.vidtitle').text();
                $("#videos-modal-label").text(label);
		var w=$(window).innerWidth();
		var wi;
		
		if (w &lt; 270) wi=200;
		else if (w &gt; 600) wi=530;
		else wi=w - 70; 
		var hi= Math.round(wi / 1.777);
		
                $("#videos-modal-content").html('<iframe src="'+url+'" width="'+wi+'" height="'+hi+'" frameborder="0" allowfullscreen="allowfullscreen">Loading video failed.</iframe>');
                $("#videos-modal").modal('show');
		$("#videos-modal").on('hidden', function() {
		  $("#videos-modal-content").html('');
		});
            });
        </script>

        <div aria-hidden="true" aria-labelledby="videos-modal-label" role="dialog" tabindex="-1" class="modal hide fade" id="videos-modal" style="display: none;">
            <div class="modal-header">
                <button aria-hidden="true" data-dismiss="modal" class="close" type="button">×</button>
                <h3 id="videos-modal-label">Vidéo</h3>
            </div>
            <div class="modal-body" id="videos-modal-content">loading...</div>
        </div>
    </xsl:if>
  </xsl:template>

  <xsl:template name="demo-videos">
    <xsl:if test=".//html:div[@class='demo video']">
      <div class="well menuRight vidacticiels">
        <h5><xsl:value-of select="$videos-demo-title" /></h5>
        <xsl:apply-templates select=".//html:div[@class='demo video']" mode="video" />
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template name="expert-videos">
    <xsl:param name="title" />

    <xsl:if test="//html:div[@class='expert video']" >
      <div class="well menuRight temoignages">
        <h5><xsl:value-of select="$videos-expert-title" /></h5>
        <xsl:apply-templates select="//html:div[@class='expert video']" mode="video" />
      </div>
    </xsl:if>
  </xsl:template>

  <!-- addthis template -->
  <xsl:template name="addthis">
    <div class="addthis_toolbox addthis_default_style ">
        <a class="addthis_button_preferred_1 addthis_button_twitter at300b" title="Tweet This" href="#">
            <span class="at16nc at300bs at15nc at15t_twitter at16t_twitter">
                <span class="at_a11y">Share on twitter</span>
            </span>
        </a>
        <a class="addthis_button_preferred_2 addthis_button_facebook at300b" title="Facebook" href="#">
            <span class="at16nc at300bs at15nc at15t_facebook at16t_facebook">
                <span class="at_a11y">Share on facebook</span>
            </span>
        </a>
        <a class="addthis_button_preferred_3 addthis_button_print at300b" title="Print" href="#">
            <span class="at16nc at300bs at15nc at15t_print at16t_print">
                <span class="at_a11y">Share on print</span>
            </span>
        </a>
        <a class="addthis_button_preferred_4 addthis_button_email at300b" title="Email" href="#">
            <span class="at16nc at300bs at15nc at15t_email at16t_email">
                <span class="at_a11y">Share on email</span>
            </span>
        </a>
        <a class="addthis_button_compact at300m" href="#">
            <span class="at16nc at300bs at15nc at15t_compact at16t_compact">
                <span class="at_a11y">More Sharing Services</span>
            </span>
        </a>
        <a class="addthis_counter addthis_bubble_style" style="display: block;" href="#">
            <a class="addthis_button_expanded" title="View more services" href="#">0</a>
            <a class="atc_s addthis_button_compact">
                <span><xsl:text> </xsl:text></span>
            </a>
        </a>
        <div class="atclear"><xsl:text> </xsl:text></div>
        <script type="text/javascript">var addthis_config = {"data_track_addressbar":true};</script>
        <script type="text/javascript" src="http://s7.addthis.com/js/250/addthis_widget.js#pubid=ra-503b6b6a710e6ab1"><xsl:text>&#x0D;</xsl:text></script>
    </div>
  </xsl:template>

  <!-- module title -->
  <xsl:template name="modtitle">
    <xsl:apply-templates select="(.//html:h1|.//html:h2|.//html:h3|.//html:h4|.//html:h5|.//html:h6|.//html:dt)[1]" />
  </xsl:template>

  <!-- module filename -->
  <xsl:template name="modfile">
    <xsl:param name="modid">
      <xsl:value-of select="@id" />
    </xsl:param>
    <xsl:variable name="mod" select="//html:div[@id = $modid]" />
    <xsl:choose>
      <xsl:when test="$mod/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']">
    <xsl:value-of select="$mod/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']/html:span[@class='infovalue']" />
      </xsl:when>
      <xsl:otherwise>
    <xsl:value-of select="$modid" />
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text>.html</xsl:text>
  </xsl:template>

  <!--  module link -->
  <xsl:template name="modhref">
    <xsl:param name="modid" />
    <xsl:variable name="topid">
      <xsl:choose>
    <xsl:when test="contains($modid,'_')">
      <xsl:value-of select="substring-before($modid,'_')" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$modid" />
    </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="mod" select="//html:div[@id = $topid]" />
    <xsl:choose>
      <xsl:when test="$mod/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']">
    <xsl:value-of select="$mod/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']/html:span[@class='infovalue']" />
      </xsl:when>
      <xsl:otherwise>
    <xsl:value-of select="$topid" />
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text>.html</xsl:text>
    <xsl:if test="contains($modid,'_')">
      <xsl:text>#</xsl:text>
      <xsl:value-of select="$modid" />
    </xsl:if>
  </xsl:template>

  <!-- fixed slashes -->
  <xsl:template name="slashes">
    <xsl:param name="text" />
    <xsl:choose>
      <xsl:when test="contains($text,'\')">
    <xsl:value-of select="substring-before($text,'\')" />
    <xsl:text>/</xsl:text>
    <xsl:call-template name="slashes">
      <xsl:with-param name="text" select="substring-after($text,'\')" />
    </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
    <xsl:value-of select="$text" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- quote text -->
  <xsl:template name="trquot">
    <xsl:param name="text" />
    <xsl:choose>
      <xsl:when test='contains($text,"&apos;")'>
    <xsl:value-of select='substring-before($text,"&apos;")' />
    <xsl:text>\&apos;</xsl:text>
    <xsl:call-template name="trquot">
      <xsl:with-param name="text" select='substring-after($text,"&apos;")' />
    </xsl:call-template>
      </xsl:when>
      <xsl:when test='contains($text, "&#xa;")'>
    <xsl:value-of select='substring-before($text,"&#xa;")' />
    <xsl:text> </xsl:text>
    <xsl:call-template name="trquot">
      <xsl:with-param name="text" select='substring-after($text,"&#xa;")' />
    </xsl:call-template>
      </xsl:when>
      <xsl:when test='contains($text,"&#x0A;")'>
    <xsl:value-of select='substring-before($text,"&#x0A;")' />
    <xsl:text> </xsl:text>
    <xsl:call-template name="trquot">
      <xsl:with-param name="text" select='substring-after($text,"&#x0A;")' />
    </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
    <xsl:value-of select="$text" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- get translations -->
  <xsl:template name="gettext">
    <xsl:param name="label" />
    <xsl:value-of select="kfp:variable(string($helpname),string($label))" />
  </xsl:template>

</xsl:stylesheet>
