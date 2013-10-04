<?xml version="1.0" encoding="utf-8"?>

<!DOCTYPE xsl:stylesheet [
   <!ENTITY mark "normalize-space(translate(string(.),'abcdefghijklmnopqrstuvwxyzÉÀÇÈÙËÊÎÏÔÖÛÜÂÄéàçèùëêïîöôüûäâ','ABCDEFGHIJKLMNOPQRSTUVWXYZEACEUEEIIOOUUAAACEUEEIIOOUUAA'))">
   <!ENTITY key "normalize-space(string(.))">
  ]>

<xsl:stylesheet version="1.0"
		xmlns:html="http://www.w3.org/1999/xhtml"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		exclude-result-prefixes="html"
		>
  <xsl:key name="indexmarks" match="html:ins[@class='index']|html:span[@rel='index']" use="''"/>
  <xsl:key name="indexmarksentries" match="html:ins[@class='index']|html:span[@rel='index']" use="text()"/>

  <xsl:template name="alphabetical-index">
    <xsl:apply-templates select="//html:ins[@class='index']|//html:span[@rel='index']" mode="alphaindex">
      <xsl:sort select="&key;"/>
    </xsl:apply-templates>
  </xsl:template>
 
  <xsl:template match="html:ins[@class='index']|html:span[@rel='index']" mode="modcontent">
    <a name="markindex" id="indx_{generate-id()}"><xsl:comment> </xsl:comment></a>
    </xsl:template>

  <xsl:template match="html:ins[@class='index']|html:span[@rel='index']" mode="alphaindex">
    <xsl:variable name="letter">
      <xsl:value-of select="substring(&mark;,1,1)"/>
    </xsl:variable>

    <xsl:if test="generate-id()=generate-id(key('indexmarks','')[substring(&mark;,1,1)=$letter][1])">
      <p class="alphaindex letter"><xsl:value-of select="$letter"/></p>
      <div class="alphaindex lettergroup">
        <xsl:apply-templates select="key('indexmarks','')[substring(&mark;,1,1)=$letter]" mode="alphaindexletter">
          <xsl:sort select="&mark;" lang="fr"/>
        </xsl:apply-templates>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="html:ins[@class='index']|html:span[@rel='index']" mode="alphaindexletter">
    <!-- process all index mark starting with the same letter -->
    <xsl:variable name="libel">
      <xsl:value-of select="&key;"/>
    </xsl:variable>

    <xsl:if test="generate-id()=generate-id(key('indexmarks','')[text()=$libel][1])">
      <!-- première marque d'index avec ce libelle -->
      <xsl:choose>
        
        <!-- le libelle contient ":" : index multiniveaux -->
        <xsl:when test="contains($libel,':')">
	  <xsl:variable name="prefix" select="substring-before($libel,':')"/>
	  <xsl:choose>
            <!-- s'il existe une entrée avec la clé de niveau supérieur elle sera insérée à ce moment -->
            <xsl:when test="key('indexmarks','')[&key;=$prefix]"/>
            <!-- si c'est la première entrée parmi celles qui commencent avec ce préfixe -->
	    <xsl:when test="generate-id()=generate-id(key('indexmarks','')[starts-with(&key;,concat($prefix,':'))][1])">
	      <p class="alphaindex entry level0">
		<xsl:value-of select="$prefix"/>
	      </p>
              <!-- traite les sous entrées -->
	      <xsl:apply-templates select="key('indexmarks','')[starts-with(&key;,concat($prefix,':'))]" mode="alphaindexlvl">
		<xsl:with-param name="prefix" select="$prefix"/>
		<xsl:sort select="&mark;" lang="fr"/>
	      </xsl:apply-templates>
	    </xsl:when>
	  </xsl:choose>
	</xsl:when>

	<!-- le libelle ne contient pas ":" : index 1er niveau -->  
	<xsl:otherwise>
	  <p class="alphaindex entry level0">
            <xsl:call-template name="entry-with-link">
              <xsl:with-param name="entry" select="$libel"/>
              <xsl:with-param name="libel" select="$libel"/>
            </xsl:call-template>
            <!--
                 <xsl:value-of select="$libel"/>
                 <xsl:apply-templates select="key('indexmarks','')[&key;=$libel]" mode="alphaindexrefs"/>
            -->
	  </p>
          <!-- s'il existe des sous entrées -->
	  <xsl:if test="key('indexmarks','')[starts-with(&key;,concat($libel,':'))]">
	    <xsl:apply-templates select="key('indexmarks','')[starts-with(&key;,concat($libel,':'))]" mode="alphaindexlvl">
	      <xsl:with-param name="prefix" select="$libel"/>
	      <xsl:sort select="&mark;" lang="fr"/>
	    </xsl:apply-templates>
	  </xsl:if>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- traite les sous-entrées -->
  <xsl:template match="*" mode="alphaindexlvl">
    <xsl:param name="prefix"/>
    <xsl:param name="level">1</xsl:param>
    <xsl:variable name="libel">
      <xsl:value-of select="&key;"/>
    </xsl:variable>
    
    <!-- si on est sur la première sous entrée -->
    <xsl:if test="generate-id()=generate-id(key('indexmarks','')[&key;=$libel][1])">
      <xsl:variable name="subkey" select="substring-after(&key;,concat($prefix,':'))"/>
      <xsl:choose>
        <!-- il existe des sous-entrées sous la sous-entrée courante -->
	<xsl:when test="contains($subkey,':')">
	  <xsl:variable name="subprefix" select="substring-before($subkey,':')"/>
	  <xsl:choose>
            <!-- s'il existe une marque avec exactement la sous-entrée courante-->
	    <xsl:when test="key('indexmarks','')[&key;=concat($prefix,':',$subprefix)]"/>
            <!-- si on est sour la première sous entrée -->
	    <xsl:when test="generate-id()=generate-id(key('indexmarks','')[starts-with(&key;,concat($prefix,':',$subprefix,':'))][1])">
	      <p class="alphaindex entry level{$level}">
                <xsl:call-template name="entry-with-link">
                  <xsl:with-param name="entry" select="$subkey"/>
                  <xsl:with-param name="libel" select="$libel"/>
                </xsl:call-template>
                <!--
                     <xsl:value-of select="$subkey"/>
                     <xsl:apply-templates select="key('indexmarks','')[&key;=$libel]" mode="alphaindexrefs"/>
                -->
	      </p>
	      <xsl:apply-templates select="key('indexmarks','')[starts-with(&key;,concat($prefix,':',$subprefix,':'))]" mode="alphaindexlvl">
		<xsl:with-param name="prefix" select="concat($prefix,':',$subprefix)"/>
		<xsl:with-param name="level" select="1 + $level"/>
		<xsl:sort select="&mark;" lang="fr"/>
	      </xsl:apply-templates>
	    </xsl:when>
	  </xsl:choose>
	</xsl:when>

	<xsl:otherwise>
	  <p class="alphaindex entry level{$level}">
            <xsl:call-template name="entry-with-link">
              <xsl:with-param name="entry" select="$subkey"/>
              <xsl:with-param name="libel" select="$libel"/>
            </xsl:call-template>
            <!--
                 <xsl:value-of select="$subkey"/>
                 <xsl:apply-templates select="key('indexmarks','')[&key;=$libel]" mode="alphaindexrefs"/>
                 -->
	  </p>

	  <xsl:if test="key('indexmarks','')[starts-with(&key;,concat($libel,':'))]">
	    <!-- il existe des sous-clés -->
	    <xsl:apply-templates select="key('indexmarks','')[starts-with(&key;,concat($libel,':'))]" mode="alphaindexlvl">
	      <xsl:with-param name="prefix" select="$libel"/>
              <xsl:with-param name="level" select="$level + 1"/>    
	      <xsl:sort select="&mark;" lang="fr"/>
	    </xsl:apply-templates>
	  </xsl:if>

	</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template name="entry-with-link">
    <xsl:param name="entry"/>
    <xsl:param name="libel"/>
    <xsl:choose>
      <xsl:when test="count(key('indexmarks','')[&key;=$libel])=1">
        <xsl:apply-templates select="key('indexmarks','')[&key;=$libel]" mode="alphaindexrefs">
          <xsl:with-param name="entry" select="$entry"/>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <a href="#" class="linkmodule" onclick="return indexmenu('{generate-id()}')">
          <xsl:value-of select="$entry"/>
        </a>
        <div class="indexmenuentries" id="im{generate-id()}" style="display:none">
          <xsl:apply-templates select="key('indexmarks','')[&key;=$libel]" mode="alphaindexrefsmenu"/>
        </div>
      </xsl:otherwise>
    </xsl:choose>
    
  </xsl:template>

  <xsl:template match="*" mode="alphaindexrefs">
    <xsl:param name="entry"/>
    <xsl:variable name="modref">
      <xsl:for-each select="ancestor-or-self::html:div[@class='module'][1]">
        <xsl:call-template name="modfile"/>
      </xsl:for-each>
    </xsl:variable>
    <xsl:variable name="modtitle">
      <xsl:for-each select="ancestor-or-self::html:div[@class='module'][1]">
        <xsl:call-template name="modtitle"/>
      </xsl:for-each>
    </xsl:variable>
    <a href="#" class="linkmodule" onclick="indexmenutopic('{$modref}')" title="{$modtitle}">
      <xsl:value-of select="$entry"/>
    </a>
  </xsl:template>

  <xsl:template match="*" mode="alphaindexrefsmenu">
    <xsl:variable name="modref">
      <xsl:for-each select="ancestor-or-self::html:div[@class='module'][1]">
        <xsl:call-template name="modfile"/>
      </xsl:for-each>
    </xsl:variable>
    <xsl:variable name="modtitle">
      <xsl:for-each select="ancestor-or-self::html:div[@class='module'][1]">
        <xsl:call-template name="modtitle"/>
      </xsl:for-each>
    </xsl:variable>
    <p>
      <a href="#" class="linkmodule" onclick="indexmenutopic('{$modref}')" title="{$modtitle}">
        <xsl:value-of select="$modtitle"/>
      </a>
    </p>
  </xsl:template>

</xsl:stylesheet>