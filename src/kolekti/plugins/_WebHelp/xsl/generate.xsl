<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:exsl="http://exslt.org/common"
                xmlns:kfp="kolekti:extensions:functions:publication"

                extension-element-prefixes="exsl kfp"
                exclude-result-prefixes="html exsl kfp">
   <xsl:output method="html" indent="yes"
      doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN" />

   <xsl:include href="alphaindex.xsl" />

   <xsl:variable name="helpname">WebHelp5xxx</xsl:variable>

   <xsl:param name="pubdir" />
   <xsl:param name="css" />
   <xsl:param name="templatedir" />
   <xsl:param name="template" />
   <xsl:param name="label" />

   <xsl:variable name="upubdir">
      <xsl:if test="not(starts-with($pubdir,'/'))">
         <xsl:text>/</xsl:text>
      </xsl:if>
      <xsl:call-template name="slashes">
         <xsl:with-param name="text" select="$pubdir" />
      </xsl:call-template>
   </xsl:variable>

   <xsl:variable name="utemplatedir">
      <xsl:if test="not(starts-with($templatedir,'/'))">
         <xsl:text>/</xsl:text>
      </xsl:if>
      <xsl:call-template name="slashes">
         <xsl:with-param name="text" select="$templatedir" />
      </xsl:call-template>
   </xsl:variable>

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

   <xsl:variable name="lang">
      <xsl:value-of select="/html:html/html:body/@lang" />
   </xsl:variable>

   <xsl:variable name="templatefile">
      <xsl:value-of select="$utemplatedir" />
      <xsl:value-of select="$template" />
   </xsl:variable>

   <xsl:variable name="translationfile">
      <xsl:choose>
         <xsl:when test="document($templatefile)//html:span[@id='labels']">
            <xsl:value-of select="document($templatefile)//html:span[@id='labels']" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="$helpname" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>

   <xsl:variable name="helptitle">
      <xsl:value-of select="kfp:replace_strvar(string(/html:html/html:head/html:title/text()))" />
   </xsl:variable>

   <xsl:variable name="starttopic">
      <xsl:choose>
         <xsl:when test="//html:div[@class='moduleinfo']//html:span[@class='infolabel']='hlpstart'">
            <xsl:for-each select="//html:div[@class='module'][html:div[@class='moduleinfo']//html:span[@class='infolabel']='hlpstart'][1]">
               <xsl:call-template name="modfile" />
            </xsl:for-each>
         </xsl:when>
         <xsl:when test="document($templatefile)//html:span[@id='start_topic']!=''">
            <xsl:value-of select="document($templatefile)//html:span[@id='start_topic']" />
         </xsl:when>

         <xsl:otherwise>
            <xsl:call-template name="modfile">
               <xsl:with-param name="modid" select="//html:div[@class='module'][1]/@id" />
            </xsl:call-template>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <!-- main template -->

   <xsl:template match="/">
      <html>
         <head>
            <title>
               <xsl:value-of select="$helptitle" />
            </title>
            <link rel="stylesheet" type="text/css" href="css/main.css" />
            <link rel="stylesheet" type="text/css" href="css/custom.css" />
            <xsl:if test="$css">
               <link rel="stylesheet" href="usercss/{$css}.css" type="text/css" />
            </xsl:if>
            <script type="text/javascript">
               var startpage='<xsl:value-of select="$starttopic" />';
            </script>
            <script src="js/index.js" type="text/javascript">
               <xsl:text>&#x0D;</xsl:text>
            </script>
            <script src="js/search.js" type="text/javascript">
               <xsl:text>&#x0D;</xsl:text>
            </script>
            <script src="js/highlight.js" type="text/javascript">
               <xsl:text>&#x0D;</xsl:text>
            </script>
            <script src="js/help.js" type="text/javascript">
               <xsl:text>&#x0D;</xsl:text>
            </script>
            <script src="js/modcodes.js" type="text/javascript">
               <xsl:text>&#x0D;</xsl:text>
            </script>
            <script src="usercss/{$css}.parts/config.js" type="text/javascript">
               <xsl:text>&#x0D;</xsl:text>
            </script>
         </head>
         <body onload="help_init()">
            <div id="header">
               <div id="tete">
                  <h1><xsl:value-of select="$helptitle" /></h1>
               </div>
               <!-- <xsl:copy-of select="document($templatefile)//html:div[@id='tete']"/> -->
            </div>
            <div id="visuel">
               <a href="{document($templatefile)//html:span[@id='logo_lien']}">
                  <img title="{document($templatefile)//html:span[@id='logo_titre']}" alt="{document($templatefile)//html:span[@id='logo_titre']}" src="illustrations/{document($templatefile)//html:span[@id='logo_visuel']}" />
               </a>
            </div>
            <div id="toolbar">
               <p>
                  <span id="tool_fold_sidepanel">
                     <span id="fold_sidepanel">
                        <xsl:variable name="label">
                           <xsl:call-template name="gettext">
                              <xsl:with-param name="label" select="'masquer'" />
                           </xsl:call-template>
                        </xsl:variable>
                        <button onclick="hide_sidepanel()" title="{$label}">
                           <img title="{$label}" alt="{$label}" src="img/hide.gif" />
                        </button>
                     </span>
                     <span id="unfold_sidepanel">
                        <xsl:variable name="label">
                           <xsl:call-template name="gettext">
                              <xsl:with-param name="label" select="'montrer'" />
                           </xsl:call-template>
                        </xsl:variable>
                        <button onclick="show_sidepanel()" title="{$label}">
                           <img title="{$label}" alt="{$label}" src="img/show.gif" />
                        </button>
                     </span>
                  </span>
                  <!-- <span id="tool_hide"> <xsl:variable name="label"> <xsl:call-template 
                     name="gettext"> <xsl:with-param name="label" select="'masquer'"/> </xsl:call-template> 
                     </xsl:variable> <button onclick="hidepanel()" title="{$label}"> <img title="{$label}" 
                     alt="{$label}" src="img/hide.gif"/> </button> </span> -->
                  <span id="tool_show_toc" style="display:none">
                     <xsl:variable name="label2">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'montrer'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <button onclick="showtoc()" title="{$label2}">
                        <img title="{$label2}" alt="{$label2}" src="img/show.gif" />
                     </button>
                  </span>
                  <span id="tool_search" class="recherche">
                     <form onsubmit="return search();">
                        <input type="text" size="20" id="search_field" />
                        <xsl:variable name="label3">
                           <xsl:call-template name="gettext">
                              <xsl:with-param name="label" select="'chercher'" />
                           </xsl:call-template>
                        </xsl:variable>
                        <button id="tool_searchb" type="submit" title="{$label3}">
                           <img title="{$label3}" alt="{$label3}" src="img/search.gif" />
                        </button>
                     </form>
                  </span>
                  <!-- <span id="tool_toc">
                           <xsl:variable name="label4">
                              <xsl:call-template name="gettext">
                                 <xsl:with-param name="label" select="'TDM'"/>
                              </xsl:call-template> 
                           </xsl:variable>
                           <button title="{$label4}" onclick="showtoc()">
                              <img title="{$label4}" alt="{$label4}" src="img/toc.gif"/>
                           </button>
                        </span> -->

                  <!--navigation interface -->
                  <span id="tool_nav" class="navigation_structure">
                     <xsl:variable name="labeltnf">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'premier'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_first">
                        <button id="tool_nav_f" title="{$labeltnf}" onclick="first_topic()" style="display:none">
                           <img title="{$labeltnf}" alt="{$labeltnf}" src="img/first.gif" />
                        </button>
                        <button id="tool_nav_f_dis" class="disabled" title="{$labeltnf}">
                           <img title="{$labeltnf}" alt="{$labeltnf}" src="img/dis_first.gif" />
                        </button>
                     </span>
                     <xsl:variable name="label5">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'precedent'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_prev">
                        <button id="tool_nav_p" title="{$label5}" onclick="prev_topic()" style="display:none">
                           <img title="{$label5}" alt="{$label5}" src="img/prev.gif" />
                        </button>
                        <button id="tool_nav_p_dis" class="disabled" title="{$label5}">
                           <img title="{$label5}" alt="{$label5}" src="img/dis_prev.gif" />
                        </button>
                     </span>
                     <xsl:variable name="label6">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'suivant'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_next">
                        <button id="tool_nav_n" title="{$label6}" onclick="next_topic()">
                           <img title="{$label6}" alt="{$label6}" src="img/next.gif" />
                        </button>
                        <button id="tool_nav_n_dis" class="disabled" title="{$label6}">
                           <img title="{$label6}" alt="{$label6}" src="img/dis_next.gif" />
                        </button>
                     </span>
                     <xsl:variable name="labeltnl">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'fin'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_last">
                        <button id="tool_nav_l" title="{$labeltnl}" onclick="last_topic()" style="display:none">
                           <img title="{$labeltnl}" alt="{$labeltnl}" src="img/last.gif" />
                        </button>
                        <button id="tool_nav_l_dis" class="disabled" title="{$labeltnl}">
                           <img title="{$labeltnl}" alt="{$labeltnl}" src="img/dis_last.gif" />
                        </button>
                     </span>
                  </span>

                  <!-- navigation with history -->
                  <span id="tool_nav_h" class="navigation_historique">
                     <xsl:variable name="labeltnf">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'premier'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_h_first">
                        <button id="tool_nav_h_f" title="{$labeltnf}" onclick="h_first_topic()" style="display:none">
                           <img title="{$labeltnf}" alt="{$labeltnf}" src="img/h_first.gif" />
                        </button>
                        <button id="tool_nav_h_f_dis" class="disabled" title="{$labeltnf}">
                           <img title="{$labeltnf}" alt="{$labeltnf}" src="img/h_dis_first.gif" />
                        </button>
                     </span>
                     <xsl:variable name="label5">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'precedent'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_h_prev">
                        <button id="tool_nav_h_p" title="{$label5}" onclick="h_prev_topic()" style="display:none">
                           <img title="{$label5}" alt="{$label5}" src="img/h_prev.gif" />
                        </button>
                        <button id="tool_nav_h_p_dis" class="disabled" title="{$label5}">
                           <img title="{$label5}" alt="{$label5}" src="img/h_dis_prev.gif" />
                        </button>
                     </span>
                     <xsl:variable name="label6">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'suivant'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_h_next">
                        <button id="tool_nav_h_n" title="{$label6}" onclick="h_next_topic()">
                           <img title="{$label6}" alt="{$label6}" src="img/h_next.gif" />
                        </button>
                        <button id="tool_nav_h_n_dis" class="disabled" title="{$label6}">
                           <img title="{$label6}" alt="{$label6}" src="img/h_dis_next.gif" />
                        </button>
                     </span>
                     <xsl:variable name="labeltnl">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'dernier'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="tool_nav_h_last">
                        <button id="tool_nav_h_l" title="{$labeltnl}" onclick="h_last_topic()" style="display:none">
                           <img title="{$labeltnl}" alt="{$labeltnl}" src="img/h_last.gif" />
                        </button>
                        <button id="tool_nav_h_l_dis" class="disabled" title="{$labeltnl}">
                           <img title="{$labeltnl}" alt="{$labeltnl}" src="img/h_dis_last.gif" />
                        </button>
                     </span>
                  </span>
                  <span id="tool_home">
                     <xsl:variable name="label7">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'accueil'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <button id="tool_nav_home" title="{$label7}" onclick="defaulttopic()">
                        <img title="{$label7}" alt="{$label7}" src="img/home.gif" />
                     </button>
                  </span>
                  <span id="tool_span_print">
                     <xsl:variable name="label8">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'imprimer'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <button id="tool_print" title="{$label8}" onclick="printtopic()">
                        <img title="{$label8}" alt="{$label8}" src="img/print.gif" />
                     </button>
                  </span>
                  <span id="tool_span_bookmark">
                     <xsl:variable name="label9">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'signet'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <button id="tool_bookmark" title="{$label9}" onclick="bktopic()">
                        <img title="{$label9}" alt="{$label9}" src="img/bkmark.gif" />
                     </button>
                  </span>
                  <span id="tool_span_uhlight" class="recherche">
                     <xsl:variable name="labela">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'DeSurligne'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <button id="tool_uhlight" style="display:none" title="{$labela}" onclick="cmdulight()">
                        <img title="{$labela}" alt="{$labela}" src="img/unhlight.gif" />
                     </button>
                  </span>
               </p>
            </div>
            <!-- end buttons -->
            <div id="breadcrumbs" class="cbc navigation_historique">
               <xsl:text>&#xA0;</xsl:text>
            </div>
            <div id="context" class="cbc navigation_structure">
               <xsl:text>&#xA0;</xsl:text>
            </div>

            <!-- panneau latéral -->
            <div id="sidepanel">
               <!-- onglets -->
               <div id="tabs">
                  <ul class="tabs">
                     <li onclick="showtabtoc()" id="toctab" class="activetab">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'TdmTitreTab'" />
                        </xsl:call-template>
                     </li>
                     <li onclick="showtabsearch()" id="searchtab">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'SearchTitreTab'" />
                        </xsl:call-template>
                     </li>
                     <xsl:if test="//html:ins[@class='index']|//html:span[@rel='index']">
                        <li onclick="showtabalphaindex()" id="alphaindextab">
                           <xsl:call-template name="gettext">
                              <xsl:with-param name="label" select="'AlphaIndexTitreTab'" />
                           </xsl:call-template>
                        </li>
                     </xsl:if>
                  </ul>
               </div>

               <!-- table des matières -->
               <div id="toc">
                  <p id="toctitle" class="toctitle">
                     <xsl:call-template name="gettext">
                        <xsl:with-param name="label" select="'TdmTitre'" />
                     </xsl:call-template>
                  </p>
                  <div id="toccontent">
                     <ul id="listToc">
                        <xsl:apply-templates select="html:html/html:body" mode="TOC" />
                     </ul>
                  </div>
               </div>

               <!-- recherche -->
               <div id="search">
                  <p id="searchtitle" class="searchtitle">
                     <xsl:variable name="labelc">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'fermer'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <span id="search_span_close">
                        <button id="search_close" title="{$labelc}" onclick="showtoc()">
                           <img title="{$labelc}" alt="{$labelc}" src="img/close.gif" />
                        </button>
                     </span>
                     <xsl:call-template name="gettext">
                        <xsl:with-param name="label" select="'ResRecherche'" />
                     </xsl:call-template>
                  </p>
                  <div id="searchoptions">
                     <p id="searchoptionslink" onclick="fold('searchoptionscontent')">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'RechOptTitre'" />
                        </xsl:call-template>
                     </p>
                     <div id="searchoptionscontent" style="display:none">
                        <p>
                           <span class="label">
                              <xsl:call-template name="gettext">
                                 <xsl:with-param name="label" select="'RechOpt1'" />
                              </xsl:call-template>
                           </span>
                           <br />
                           <input type="radio" name="opt1" id="optTM" onclick="a_opt()" checked="checked" />
                           <label for="optTM">
                              <xsl:call-template name="gettext">
                                 <xsl:with-param name="label" select="'RechOptTM'" />
                              </xsl:call-template>
                           </label>
                           <br />
                           <input type="radio" name="opt1" id="opt1M" onclick="a_opt()" />
                           <label for="opt1M">
                              <xsl:call-template name="gettext">
                                 <xsl:with-param name="label" select="'RechOpt1M'" />
                              </xsl:call-template>
                           </label>
                        </p>
                        <p>
                           <span class="label">
                              <xsl:call-template name="gettext">
                                 <xsl:with-param name="label" select="'RechOpt2'" />
                              </xsl:call-template>
                           </span>
                           <br />
                           <input type="radio" name="opt2" id="optMC" onclick="a_opt()" checked="checked" />
                           <label for="optMC">
                              <xsl:call-template name="gettext">
                                 <xsl:with-param name="label" select="'RechOptMC'" />
                              </xsl:call-template>
                           </label>
                           <br />
                           <input type="radio" name="opt2" id="optMD" onclick="a_opt()" />
                           <label for="optMD">
                              <xsl:call-template name="gettext">
                                 <xsl:with-param name="label" select="'RechOptMD'" />
                              </xsl:call-template>
                           </label>
                        </p>
                     </div>
                  </div>
                  <div id="sidebar_search">
                     <form onsubmit="return search();">
                        <input type="text" size="20" id="search_field_side" />
                        <xsl:variable name="label3">
                           <xsl:call-template name="gettext">
                              <xsl:with-param name="label" select="'chercher'" />
                           </xsl:call-template>
                        </xsl:variable>
                        <button id="tool_searchb" type="submit" title="{$label3}">
                           <img title="{$label3}" alt="{$label3}" src="img/search.gif" />
                        </button>
                     </form>
                  </div>
                  <div id="search_uhlight" style="display:none">
                     <xsl:variable name="labela">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'DeSurligne'" />
                        </xsl:call-template>
                     </xsl:variable>
                     <button id="tool_uhlight2" style="display:none" title="{$labela}" onclick="cmdulight()">
                        <img title="{$labela}" alt="{$labela}" src="img/unhlight.gif" />
                     </button>
                  </div>
                  <p id="nores">
                     <xsl:call-template name="gettext">
                        <xsl:with-param name="label" select="'AucunResultat'" />
                     </xsl:call-template>
                  </p>
                  <div id="searchres">
                  </div>
               </div>

               <!-- alphebtical index -->
               <xsl:if test="//html:ins[@class='index']|//html:span[@rel='index']">
                  <div id="alphaindex">
                     <p id="alphaindextitle" class="alphaindextitle">
                        <xsl:call-template name="gettext">
                           <xsl:with-param name="label" select="'AlphaIndexTitre'" />
                        </xsl:call-template>
                     </p>
                     <div id="alphaindexcontent" class="alphaindexcontent">
                        <xsl:call-template name="alphabetical-index" />
                     </div>
                  </div>
               </xsl:if>
            </div>
            <div id="allwordsdiv" style="display:none"><xsl:text>&#x0D;</xsl:text></div>
            <div id="main">
               <div id="sphandle">
                  <xsl:text>&#xA0;</xsl:text>
               </div>
               <iframe id="topicframe" name="topicframe" frameborder="0"><xsl:text>&#x0D;</xsl:text></iframe>
            </div>
            <div id="footer">
               <xsl:copy-of select="document($templatefile)//html:div[@id='pied']" />
            </div>
            <iframe id="searchresframe" height="0" width="0" style="border-color:white;position:absolute;top:0;right:0" />
            <!-- <iframe id="debugframe" height="100" width="500" style="position:absolute;top:100px;left:500px"/> -->
            <script type="text/javascript">
               var label_score="<xsl:call-template name="gettext"><xsl:with-param name="label" select="'score'" /></xsl:call-template>";
               var label_moreres="<xsl:call-template name="gettext"><xsl:with-param name="label" select="'plus10res'" /></xsl:call-template>";
            </script>
         </body>
      </html>
      <xsl:apply-templates select="html:html/html:body//html:div[@class='module']" />
      <exsl:document href="{$upubdir}/js/modcodes.js" method='text'>
         <xsl:text>var modcodes = new Object();</xsl:text>
         <xsl:apply-templates select="html:html/html:body//html:div[@class='module']" mode="modcodes" />
      </exsl:document>
      <exsl:document href="{$upubdir}/js/texts.html" method='html' indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN">
         <html>
            <head>
               <title></title>
            </head>
            <body>
               <xsl:apply-templates select="html:html/html:body//html:div[@class='module']" mode="textcontent" />
            </body>
         </html>
      </exsl:document>
   </xsl:template>

   <xsl:template match="html:div[@class='module']" mode="modcodes">
      <xsl:variable name="modcode">
         <xsl:call-template name="modfile" />
      </xsl:variable>
      <xsl:variable name="modtitle">
         <xsl:call-template name="modtitle" />
      </xsl:variable>
      <xsl:text>modcodes['</xsl:text>
      <xsl:value-of select="$modcode" />
      <xsl:text>']='</xsl:text>
      <xsl:call-template name="trquot">
         <xsl:with-param name="text" select="$modtitle" />
      </xsl:call-template>
      <xsl:text>';&#x0A;</xsl:text>
   </xsl:template>

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
         <xsl:otherwise>
            <xsl:value-of select="$text" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>

   <xsl:template match="html:div[@class='module']" mode="textcontent">
      <xsl:variable name="filename">
         <xsl:call-template name="modfile" />
      </xsl:variable>
      <div id="{$filename}">
         <xsl:for-each select="text()|*[not(@class='moduleinfo')]">
            <xsl:value-of select="." />
         </xsl:for-each>
      </div>
   </xsl:template>

   <xsl:template match="html:div[@class='module']">
      <xsl:variable name="filename">
         <xsl:call-template name="modfile" />
      </xsl:variable>
      <xsl:message>
        <xsl:value-of select="$filename"/>
      </xsl:message>
      <exsl:document href="{$upubdir}/{$filename}" method='html' indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN">
         <html>
            <head>
               <title>topic</title>
               <link rel="stylesheet" type="text/css" href="css/custom.css" />
               <link rel="stylesheet" type="text/css" href="css/topic.css" />
               <xsl:if test="$css">
                  <link rel="stylesheet" href="usercss/{$css}.css" type="text/css" />
               </xsl:if>
               <xsl:copy-of select="/html:html/html:head/html:link[@rel='stylesheet']" />
               <xsl:copy-of select="/html:html/html:head/html:script" />
               <script src="js/topic.js" type="text/javascript">
               </script>
            </head>
            <body onload="inittopic()" id="topic">
               <div id="topic_header">
                  <xsl:copy-of select="document($templatefile)//html:div[@id='tete_topic']" />
               </div>
               <xsl:apply-templates select="*[not(@class='moduleinfo')]" mode="modcontent" />
               <div id="topic_footer">
                  <xsl:copy-of select="document($templatefile)//html:div[@id='pied_topic']" />
               </div>
            </body>
         </html>
      </exsl:document>
   </xsl:template>

   <xsl:template match="html:h1|html:h2|html:h3|html:h4|html:h5|html:h6" mode="modcontent">
      <xsl:variable name="currentlvl" select="substring-after(local-name(),'h')" />
      <xsl:variable name="sectionlvl" select="count(ancestor::html:div[@class='section'])" />
      <xsl:variable name="newlvl" select="$currentlvl - ($sectionlvl -1)" />
      <xsl:element name="h{$newlvl}" namespace="http://www.w3.org/1999/xhtml">
         <xsl:apply-templates select="node()|@*" mode="modcontent" />
      </xsl:element>
   </xsl:template>

   <xsl:template match="html:a[@href='#']" mode="modcontent">
      <xsl:apply-templates select="node()" mode="modcontent" />
   </xsl:template>

   <xsl:template match="html:a[@href!='#'][starts-with(@href,'#')]" mode="modcontent">
      <xsl:copy>
         <xsl:attribute name="onclick">
            <xsl:text>topic(</xsl:text>
            <xsl:call-template name="modfilejs">
               <xsl:with-param name="modid" select="substring-after(@href,'#')" />
            </xsl:call-template>
            <xsl:text>)</xsl:text>
         </xsl:attribute>
         <xsl:apply-templates select="@*" mode="modcontent" />
         <xsl:attribute name="href">
            <xsl:call-template name="modhref">
               <xsl:with-param name="modid" select="substring-after(@href,'#')" />
            </xsl:call-template>
         </xsl:attribute>
         <xsl:apply-templates select="node()" mode="modcontent" />
      </xsl:copy>
   </xsl:template>

   <xsl:template match="html:a[@href!='#'][not(starts-with(@href,'#'))]">
      <xsl:copy>
         <xsl:apply-templates select="@*" mode="modcontent" />
         <xsl:attribute name="target">_blank</xsl:attribute>
         <xsl:apply-templates select="node()" mode="modcontent" />
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

   <xsl:template match="html:embed" mode="modcontent">
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

   <xsl:template match="node()|@*" mode="modcontent">
      <xsl:copy>
         <xsl:apply-templates select="node()|@*" mode="modcontent" />
      </xsl:copy>
   </xsl:template>

   <xsl:template match="html:a[@class='indexmq']" mode="modcontent" />

   <xsl:template match="html:div[@class='module']" mode="TOC">
      <xsl:variable name="modref">
         <xsl:call-template name="modfile" />
      </xsl:variable>
      <xsl:variable name="modtitle">
         <xsl:call-template name="modtitle" />
      </xsl:variable>
      <li id="tocmod{substring-before($modref,'.html')}">
         <span class="bascule">
            <span class="pictodash tocpicto">
               <img src="img/dash.gif" alt="-" />
            </span>
         </span>
         <span>
            <a href="#" class="linkmodule" onclick="topic('{$modref}')" title="{$modtitle}">
               <xsl:value-of select="$modtitle" />
            </a>
         </span>
      </li>
   </xsl:template>

   <xsl:template match="html:div[@class='section'][@hidden]" mode="TOC" />
   <xsl:template match="html:div[@class='section'][not(@hidden)]" mode="TOC">
      <li>
         <xsl:call-template name="bascule">
            <xsl:with-param name="id" select="generate-id()" />
         </xsl:call-template>
         <xsl:variable name="modref">
            <xsl:call-template name="modfile">
               <xsl:with-param name="modid" select=".//html:div[@class='module'][1]/@id" />
            </xsl:call-template>
         </xsl:variable>
         <xsl:variable name="modtitle">
            <xsl:call-template name="modtitle" />
         </xsl:variable>
         <a href="#" class="linkmodule" onclick="topic('{$modref}')" title="{$modtitle}">
            <xsl:value-of select="$modtitle" />
         </a>
         <ul id="belt{generate-id()}" style="display:none">
            <xsl:apply-templates mode="TOC" />
         </ul>
      </li>
   </xsl:template>

   <xsl:template name="bascule">
      <span class="bascule">
         <span class="pictoright tocpicto" title="montrer" onclick="fold_show('{generate-id()}')" id="cond{generate-id()}">
            <img src="img/right.gif" alt="montrer" />
         </span>
         <span class="pictodown tocpicto" title="cacher" onclick="fold_hide('{generate-id()}')" id="comp{generate-id()}" style="display:none">
            <img src="img/down.gif" alt="cacher" />
         </span>
      </span>
   </xsl:template>

   <xsl:template match="text()" mode="TOC" />

   <xsl:template name="modfile">
      <xsl:param name="modid">
         <xsl:value-of select="@id" />
      </xsl:param>
      <xsl:choose>
         <xsl:when test="//html:div[@id=$modid]/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']">
            <xsl:value-of select="//html:div[@id=$modid]/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']/html:span[@class='infovalue']" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="$modid" />
         </xsl:otherwise>
      </xsl:choose>
      <xsl:text>.html</xsl:text>
   </xsl:template>

   <xsl:template name="modfilejs">
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
      <xsl:text>'</xsl:text>
      <xsl:choose>
         <xsl:when
            test="//html:div[@id=$topid]/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']">
            <xsl:value-of select="//html:div[@id=$topid]/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']/html:span[@class='infovalue']" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="$topid" />
         </xsl:otherwise>
      </xsl:choose>
      <xsl:text>'</xsl:text>
      <xsl:if test="contains($modid,'_')">
         <xsl:text>,'</xsl:text>
         <xsl:value-of select="$modid" />
         <xsl:text>'</xsl:text>
      </xsl:if>
   </xsl:template>

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
      <xsl:choose>
         <xsl:when
            test="//html:div[@id=$topid]/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']">
            <xsl:value-of select="//html:div[@id=$topid]/html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']='topic_file']/html:span[@class='infovalue']" />
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

   <xsl:template name="modtitle">
      <xsl:apply-templates select="(.//html:h1|.//html:h2|.//html:h3|.//html:h4|.//html:h5|.//html:h6|.//html:dt)[1]" mode="TOCtitle" />
   </xsl:template>

   <xsl:template match="html:span[@class='title_num']" mode="TOCtitle" />
   <xsl:template match="html:ins[@class='index']|html:span[@rel='index']" mode="TOCtitle" />

   <!-- get translations -->
   <xsl:template name="gettext">
      <xsl:param name="label" />
      <xsl:value-of select="kfp:variable('xxx',string($label))" />
      <!--      <xsl:value-of select="kfp:variable(string($translationfile),string($label))" /> -->
   </xsl:template>
</xsl:stylesheet>
