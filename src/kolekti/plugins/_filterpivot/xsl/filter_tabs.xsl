<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:h="http://www.w3.org/1999/xhtml"
  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="h"
  version="1.0">
  
  <xsl:param name="tabsfile" select="'sources/share/tabs.xml'"/>
  <xsl:variable name="tabs" select="concat($rootdir, '/sources/share/tabs.xml')"/>
    
  <xsl:template match="node()|@*" name="id">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="h:head">
    
    <xsl:message>tabsfile : <xsl:value-of select="$tabsfile"/></xsl:message>
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="node()"/>
      <style type="text/css">
        .tabs_left {
          position: running(tabs-left);
          transform: rotate(90deg);
        }
        .tabs_right {
          position: running(tabs-right);
          transform: rotate(90deg);
        }

        .tabs_group {
        <!-- default value, may be overriden by xml <volume> style rule -->        
        font-size:1em;
        color:black;
        font-weight: 200%;
        height:10mm;       

        position:relative;
        left:0;
        right:0;        
        width:100%;
        }
        
        .tabs {
        position:absolute;
        height:5mm;
        }
        
        .tabs_group_left .tabs {
        bottom:-2mm;
        
        }
        .tabs_group_right .tabs {
        top: -2mm;
        }
        
        .tab-right {
        transform: rotate(180deg);
        }
        .tab-left {
            
        }
        
        .tab {
          <!-- default value, may be overriden by any present xml <tab> style rule -->
          display:inline-block;
          background-color: Silver;
          padding: 2px 4px 10px 4px;
          margin-left: 5px;
          border-radius: 2px;
          visibility:hidden;
          }

          .tab.visible {
          visibility:inherit;
          }
          
        @page:left {
        @left-top {
          content: element(tabs-left);
        }

        }
          @page:right { 
          @right-top {
          content: element(tabs-right);
          }
        }        

      </style>
      <style type="text/css">
        <xsl:variable name="lang" select="/h:html/h:body/@lang"/>
        .tabs_group {
        <xsl:value-of select="document($tabs)/tabs/volume[tag/@lang = $lang]/style"/>
        <xsl:value-of select="document($tabs)/tabs/style"/>
        }
        <xsl:for-each select="document($tabs)/tabs/volume[tag/@lang = $lang]/tab[style]">
        .tab-<xsl:value-of select="@lang"/> {
          <xsl:value-of select="style"/>  
        }
        </xsl:for-each>
      </style>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="h:body">
    <xsl:variable name="lang" select="@lang"/>
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <div class="tabs_left">
        <div class="tabs_group tabs_group_left">
          <xsl:apply-templates select="document($tabs)/tabs/volume" mode="tabcontent">
            <xsl:with-param name="lang" select="$lang"/>
            <xsl:with-param name="side" select="'left'"/>
          </xsl:apply-templates>
        </div>
      </div>
      <div class="tabs_right">
        <div class="tabs_group tabs_group_right">
          <xsl:apply-templates select="document($tabs)/tabs/volume" mode="tabcontent">
            <xsl:with-param name="lang" select="$lang"/>
            <xsl:with-param name="side" select="'right'"/>                        
          </xsl:apply-templates>
        </div>
      </div>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>    

  
  <xsl:template match="volume" mode="tabcontent">
    <xsl:param name="lang"/>
    <xsl:param name="side"/>
    <xsl:if test="tab[@lang=$lang]">
      <!-- si le volume contient le tab de la langue de publication -->
      <div class="tabs">
        <xsl:apply-templates select="tab">
          <xsl:with-param name="lang" select="$lang"/>
          <xsl:with-param name="side" select="$side"/>
        </xsl:apply-templates>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="volume/tab">  
    <xsl:param name="lang"/>
    <xsl:param name="side"/>
    <div class="tab">
      <xsl:attribute name="class">
        <xsl:text>tab tab-</xsl:text>
        <xsl:value-of select="@lang"/>        
        <xsl:text> tab-</xsl:text>
        <xsl:value-of select="$side"/>        
        <xsl:if test="@lang=$lang">
          <xsl:text> visible</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <span><xsl:value-of select="@label"/></span>
    </div>
  </xsl:template>
  
</xsl:stylesheet>
