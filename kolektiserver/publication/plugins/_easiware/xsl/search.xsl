<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:exsl="http://exslt.org/common"
                xmlns:kfp="kolekti:extensions:functions:publication"

                extension-element-prefixes="exsl kfp"
                exclude-result-prefixes="html exsl kfp">

    <xsl:template match="html:head" mode="search-header">
        <script src="js/modcodes.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>
        <script src="js/modtexts.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>
        <script src="js/index.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>
        <script src="js/search.js" type="text/javascript"><xsl:text>&#x0D;</xsl:text></script>
        <script type="text/javascript">
          var label_score="<xsl:call-template name="gettext"><xsl:with-param name="label" select="'score'" /></xsl:call-template>";
          var label_moreres="<xsl:call-template name="gettext"><xsl:with-param name="label" select="'plus10res'" /></xsl:call-template>";
        </script>
    </xsl:template>

    <xsl:template match="html:*" mode="search-header" />

    <xsl:template match="html:body" mode="search-file">
        <exsl:document href="file://{$upubdir}/{$label}/js/modtexts.js" method='text'>
            var modtexts = new Object();
            <xsl:apply-templates select="$modules" mode="textcontent" />
        </exsl:document>
        <exsl:document href="file://{$upubdir}/{$label}/js/modcodes.js" method='text'>
            var modcodes = new Object();
            <xsl:apply-templates select="$modules" mode="modcodes" />
        </exsl:document>
    </xsl:template>

    <xsl:template match="html:*" mode="search-file" />

    <xsl:template match="html:div[@class='module']" mode="textcontent">
        <xsl:variable name="filename">
          <xsl:call-template name="modfile" />
        </xsl:variable>
        <xsl:text>modtexts['</xsl:text>
        <xsl:value-of select="$filename" />
        <xsl:text>'] = '</xsl:text>
        <xsl:apply-templates mode="textcontent" select="node()[not(@class='moduleinfo')]" />
        <xsl:text>';&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="text()" mode="textcontent">
        <xsl:call-template name="trquot">
          <xsl:with-param name="text" select="normalize-space(.)" />
        </xsl:call-template>
        <xsl:text> </xsl:text>
    </xsl:template>

    <xsl:template match="html:span[@class='title_num']" mode="textcontent"/>
    <xsl:template match="html:div[@class='moduleinfo']" mode="textcontent"/>

    <xsl:template match="html:div[@class='module']" mode="modcodes">
        <xsl:variable name="modcode">
          <xsl:call-template name="modfile" />
        </xsl:variable>
        <xsl:variable name="modt">
          <xsl:call-template name="modtitle" />
        </xsl:variable>
        <xsl:variable name="modtitle">
          <xsl:for-each select="ancestor::html:div[@class='section']">
        <xsl:sort order="ascending" select="count(ancestor::*)"/>
        <xsl:if test="not(position()=1)">
          <xsl:copy-of select="html:*[1]/text()"/>
          <!--        <xsl:if test="position()!=last() or $modt!=''"> -->
          <xsl:text> / </xsl:text>
          <!--        </xsl:if>-->
        </xsl:if>
          </xsl:for-each>
          <xsl:value-of select="$modt"/>
        </xsl:variable>
        <xsl:text>modcodes['</xsl:text>
        <xsl:value-of select="$modcode" />
        <xsl:text>']='</xsl:text>
        <xsl:call-template name="trquot">
          <xsl:with-param name="text" select="$modtitle" />
        </xsl:call-template>
        <xsl:text>';&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="html:*" mode="modcodes" />
</xsl:stylesheet>
