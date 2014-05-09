<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:d="DAV:"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:kp="kolekti:publication"

                exclude-result-prefixes="i d kf kp">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="kolekti://utils/ui/xsl/properties.xsl"/>

  <xsl:template match="kp:languages">
   <kp:languages>
     <div class="languages">
      <a name="languages" />
      <h3><i:text>[0234]Langues</i:text></h3>
      <div class="sidebar_section">
       <ul><xsl:apply-templates /></ul>
      </div>
     </div>
   </kp:languages>
  </xsl:template>

  <xsl:template match="kp:languages/kp:lang">
   <li><xsl:value-of select="@dir"/></li>
  </xsl:template>

  <xsl:template match="kp:versions">
   <kp:versions>    
     <div class="versions">
        <a name="versions" />
        <h3><i:text>[0235]Publications antérieures</i:text></h3>
        <div class="sidebar_section">
	  <ul><xsl:apply-templates /></ul>
	</div>
     </div>
   </kp:versions>
  </xsl:template>

  <xsl:template match="kp:versions/kp:version">
   <li class="{@time}">
     <xsl:value-of select="kf:format_time(string(@time))"/>
   </li>
  </xsl:template>
</xsl:stylesheet>
