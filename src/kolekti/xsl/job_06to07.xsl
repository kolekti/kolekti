<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ext="kolekti:ext"
  exclude-result-prefixes="html ext"
  >

  <xsl:output method="xml" />

  <xsl:template match="node()|@*" name="idt">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  
  <xsl:template match="/order">
    <job>
      <xsl:apply-templates/>
    </job>
  </xsl:template>

  <xsl:template match="criterias">
    <criteria>
      <xsl:apply-templates/>
    </criteria>
  </xsl:template>

  <xsl:template match="profile">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="label"/>
      <div value="{/order/pubdir/@value}"/>
      <xsl:apply-templates select="criterias"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="criteria[@checked='0']"/>
  <xsl:template match="criteria/@checked"/>

  <xsl:template match="criteria">
    <criterion>
      <xsl:apply-templates select="@*"/>
    </criterion>
  </xsl:template>

  <xsl:template match="scripts">
    <xsl:copy>
      <script name="xhtml" enabled="0">
        <label>html</label>
        <filename>html_{G}</filename>
        <parameters>
          <parameter name="css" value="default" />
        </parameters>
      </script>
      <script name="WebHelp5" enabled="1">
        <label>WebHelp</label>
        <filename>WebHelp_{G}</filename>
        <parameters>
          <parameter name="template" value="WebHelp"/>
          <parameter name="pivot_filter" value="filter"/>
          <parameter name="css" value="WebHelp5"/>
          <parameter name="zip" value="yes"/>
        </parameters>
      </script>
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>
