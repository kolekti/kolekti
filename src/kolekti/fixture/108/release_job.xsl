<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  version="1.0">

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="script[@name='princexml'][@enabled=1]">
    <script name="multiscript" enabled="1">

      <xsl:copy-of select="label"/>
      <xsl:copy-of select="filename"/>
      <publication>
        <script name="princexml_nbpage">
          <parameters>
            <parameter name="CSS" value="{parameters/parameter[@name='CSS']/@value}"/>
          </parameters>
        </script>
        <script name="serializepdf">
          <parameters/>
        </script>
      </publication>
      <validation/>
    </script>
  </xsl:template>
  
  
</xsl:stylesheet>
