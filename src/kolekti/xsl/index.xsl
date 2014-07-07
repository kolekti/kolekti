<?xml version="1.0" encoding="utf-8"?>
<!--
    kOLEKTi : a structural documentation generator
    Copyright (C) 2007 Stéphane Bonhomme (stephane@exselt.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


-->
<!DOCTYPE xsl:stylesheet [
   <!ENTITY mark "normalize-space(translate(.,'abcdefghijklmnopqrstuvwxyzÉÀÇÈÙËÊÎÏÔÖÛÜÂÄ','ABCDEFGHIJKLMNOPQRSTUVWXYZEACEUEEIIOOUUAA'))">
   <!ENTITY key "normalize-space(.)">
  ]>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  xmlns:html="http://www.w3.org/1999/xhtml" 
  xmlns="http://www.w3.org/1999/xhtml" 
  exclude-result-prefixes="html"
  version="1.0">

  <!-- this key contains all index marks -->
  <xsl:key name="indexmarks" match="html:span[@rel='index']|html:ins[@class='index']" use="''"/>
  <xsl:key name="indexmarksentries" match="html:ins[@class='index']|html:span[@rel='index']" use="text()"/>

  <!-- Copy all to output (filter) -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>


  <!-- adds anchors to index marks  -->
  <xsl:template match="html:span[@rel='index']|html:ins[@class='index']">
    <xsl:param name="level" select="1"/>
    <a name="idx_{generate-id()}" 
       id="idx_{generate-id()}" 
       class="indexmq">
      <xsl:comment>
	<xsl:copy-of select="normalize-space(.)"/>
      </xsl:comment>
    </a>
    <xsl:copy-of select="."/>
  </xsl:template>


  <!-- index section -->
  <xsl:template match="html:div[starts-with(@class,'INDEX')]">
    <div>
      <xsl:copy-of select="@class"/>
      <xsl:apply-templates select="html:*[@class='INDEX_titre']" mode="indextitle" />
      <div class="INDEX_corps">
	<xsl:apply-templates select="/html:html/html:body" mode="index"/>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="html:*[@class='INDEX_titre']" mode="indextitle">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:*[@class='INDEX_titre']" mode="index" />

  <!-- process body in index -->
  <xsl:template match="html:body" mode="index">
    <xsl:apply-templates select="//html:ins[@class='index']|//html:span[@rel='index']" mode="alphaindex">
      <xsl:sort select="&key;"  lang="fr"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- handle an index mark in the index -->

  <xsl:template match="html:ins[@class='index']|html:span[@rel='index']" mode="alphaindex">
    <xsl:variable name="letter">
      <xsl:value-of select="substring(&mark;,1,1)"/>
    </xsl:variable>
    
    <xsl:if test="generate-id()=generate-id(key('indexmarks','')[substring(&mark;,1,1)=$letter][1])">
      <!-- generate the letter -->
      <p class="alphaindex letter"><xsl:value-of select="$letter"/></p>

      <!-- handle all entries with this letter -->
      <div class="alphaindex lettergroup">
	<xsl:apply-templates select="key('indexmarks','')[substring(&mark;,1,1)=$letter]" mode="alphaindexletter">
	  <xsl:sort select="&mark;" lang="fr"/>
	</xsl:apply-templates>
      </div>
    </xsl:if>
  </xsl:template>


  <!-- process all index mark starting with the same letter -->
  <xsl:template match="html:ins[@class='index']|html:span[@rel='index']" mode="alphaindexletter">
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
    
    <!-- output the entry text -->
    <xsl:value-of select="$entry"/>

    <!-- output links -->
    <xsl:apply-templates select="key('indexmarks','')[&key;=$libel]" mode="alphaindexrefs">
      <xsl:with-param name="entry" select="$entry"/>
    </xsl:apply-templates>    
  </xsl:template>

  <xsl:template match="*" mode="alphaindexrefs">
    <xsl:if test="not(position()='1')">
      <span class="indexrefs-sep">,</span>
    </xsl:if>
    <xsl:text> </xsl:text>
    <a href="#idx_{generate-id()}"><xsl:value-of select="position()"/></a>
  </xsl:template>


</xsl:stylesheet>
