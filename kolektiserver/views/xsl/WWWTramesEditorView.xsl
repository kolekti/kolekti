<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kol="http://www.exselt.com/kolekti"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"
                xmlns:kt="kolekti:trames"
                xmlns:dav="DAV:"
                xmlns:mod="kolekti:modules"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kol kf ke kcd kd kt dav mod">
  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="viewer" select="/kcd:view/kcd:http/kcd:headers/kcd:header[@name='kolektiviewer']/@content"/>
<!--
  <xsl:variable name="diruri">
    <xsl:call-template name="dirname">
      <xsl:with-param name="path" select="/kcd:view/kcd:http/@uri" />
    </xsl:call-template>
  </xsl:variable>
-->
  <xsl:variable name="urih"><xsl:value-of select="/kcd:view/kcd:http/@uri_hash" /></xsl:variable>
  <xsl:variable name="uri" select="/kcd:view/kcd:http/@reluri"/>
  <xsl:variable name="tramename" select="/kcd:view/kcd:data/dav:displayname"/>

<!--
  <xsl:template name="basename">
    <xsl:param name="path"/>
    <xsl:choose>
      <xsl:when test="contains($path,'/')">
        <xsl:call-template name="basename">
          <xsl:with-param name="path" select="substring-after($path,'/')" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$path"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="dirname">
    <xsl:param name="path"/>
    <xsl:if test="contains($path,'/')">
      <xsl:value-of select="substring-before($path,'/')"/>
      <xsl:text>/</xsl:text>
      <xsl:call-template name="dirname">
        <xsl:with-param name="path" select="substring-after($path,'/')" />
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
-->

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>
<!--
  <xsl:template match="kcd:view">
    <xsl:apply-templates select="kcd:data"/>
  </xsl:template>

  <xsl:template match="kcd:data">
    <div>
      <div class="resourceview_content tramesview">
        <xsl:call-template name="commands"/>
        <div style="clear:both">
          <xsl:apply-templates select="kt:trame"/>
        </div>
      </div>
    </div>
  </xsl:template>
-->
  <xsl:template match="kt:trame">
    <div class="show_resource">
      <div class="resourceview_content tramesview">
        <div class="trame">
          <xsl:apply-templates select="kt:body/*"/>
          <xsl:if test="not(kt:body/*)">
            <div class="tplaceholder">
              <div class="dropmodule"><div><xsl:comment>drop zone</xsl:comment></div></div>
            </div>
          </xsl:if>
        </div>
        <div class="expert">
          <xsl:apply-templates select="head"/>
        </div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="kt:section">
    <div class="section">
      <div class="dropsection"><div><xsl:comment>drop zone</xsl:comment></div></div>
      <xsl:apply-templates/>
      <xsl:if test="not(kt:section)">
        <div class="tplaceholder">
          <div class="dropsection"><div><xsl:comment>drop zone</xsl:comment></div></div>
        </div>
      </xsl:if>
    </div>
    <xsl:if test="not(following-sibling::kt:section)">
      <div class="tplaceholder">
          <div class="dropsection"><div><xsl:comment>drop zone</xsl:comment></div></div>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="kt:section/kt:title">
    <p class="title">
      <span class="ui-icon ui-icon-minusthick">&#xA0;</span>
      <span class="label"><xsl:apply-templates/></span>
    </p>
  </xsl:template>

  <xsl:template match="kt:module">
    <div class="module">
      <div class="dropmodule"><div><xsl:comment>drop zone</xsl:comment></div></div>
      <p class="{@type}">
        <span class="resident" style="display:none">
          <span class="resid">
            <xsl:value-of select="@resid"/>
          </span>
          <span class="urlid">
            <xsl:value-of select="@urlid"/>
          </span>
	  <!--
	  <xsl:if test="@type='mod'">
	    <span class="version">
	      <xsl:value-of select="@version"/>
	    </span>
          </xsl:if>
	  -->
        </span>

        <xsl:choose>
          <xsl:when test="@type='auto'">
            <img i:title="[0239]Module Automatique" src="/_lib/kolekti/icons/Automodule.png"/>
            <span>
              <xsl:value-of select="kt:props/kt:name"/>
            </span>
          </xsl:when>
          <xsl:when test="@type='mod'">
            <!--<xsl:apply-templates select="kt:props" mode="module-owner"/>-->
            <xsl:if test="not(starts-with(@resid, 'kolekti://')) and not(kf:validmod(string(@resid)))">
               <span class="modvalid">
                 <img src="/_lib/kolekti/icons/dialog-warning.png" i:title="[0346]Module mal formé" />
               </span>
            </xsl:if>
            <span class="modtitle">
              <xsl:attribute name="title">
                <xsl:choose>
                  <xsl:when test="starts-with(@resid, '@')">
                    <xsl:value-of select="substring(@resid, 2)" />
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="@resid" />
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:attribute>
              <xsl:value-of select="kt:props/dav:displayname"/>
            </span>
            <xsl:apply-templates select="kt:props" mode="module-actions"/>
          </xsl:when>
        </xsl:choose>
        <!-- <span class="modactions">
         <xsl:choose>
            <xsl:when test="@enabled='0'">
               <span class="enabled" style="display: none;"><img src="" i:title="[0000]Activer le module" alt="+"/></span>
            </xsl:when>
            <xsl:otherwise>
               <span class="enabled" style="display: inline;"><img src="" i:title="[0000]Désactiver le module" alt="-"/></span>
            </xsl:otherwise>
         </xsl:choose>
        </span>-->
      </p>
    </div>

    <xsl:if test="not(following-sibling::kt:module)">
      <div class="tplaceholder">
         <div class="dropmodule"><div><xsl:comment>drop zone</xsl:comment></div></div>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="kt:props" mode="module-actions">
    <span class="tramemodactions">
      <xsl:comment/>
    </span>
  </xsl:template>

  <xsl:template name="commands"> </xsl:template>

  <xsl:template name="actions"> </xsl:template>
</xsl:stylesheet>