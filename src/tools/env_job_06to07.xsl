<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ext="kolekti:migrate"
  exclude-result-prefixes="ext"
    
>
  <xsl:output method="xml" indent="yes"/>


  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="data">
    <job>
      <dir value="undefined"/>
      <criteria/>

      <xsl:apply-templates select="profiles"/>
      <xsl:apply-templates select="scripts"/>
    </job>
  </xsl:template>
  
  <xsl:template match="profile">
    <profile enabled="1">
      <label><xsl:value-of select="ext:translate_jobstring(label/text(), criterias)"/></label>
      <dir value="{ext:translate_jobstring(/data/field[@name='pubdir']/@value, criterias)}"/>
      <xsl:apply-templates select="criterias"/>
    </profile>
  </xsl:template>

  <xsl:template match="criterias">
    <criteria>
      <xsl:apply-templates/>
    </criteria>
  </xsl:template>

  <xsl:template match="criteria">
    <criterion>
      <xsl:copy-of select="@code"/>
      <xsl:copy-of select="@value"/>
    </criterion>
  </xsl:template>

  <xsl:template match="script">
    <script name="multiscript">
      <xsl:copy-of select="@enabled"/>
      <label><xsl:value-of select="@name"/></label>
      <filename><xsl:value-of select="ext:translate_jobstring(//profile[1]/label/text(), //profile[1]/criterias)"/></filename>
      <publication>
        <script>
          <xsl:copy-of select="@name"/>
          <xsl:apply-templates select="parameters"/>
        </script>
      </publication>
    </script>
  </xsl:template>
  
</xsl:stylesheet>
