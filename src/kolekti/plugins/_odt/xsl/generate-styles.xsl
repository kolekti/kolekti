<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
		xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" 
		xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" 
		xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" 
		xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" 
		xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" 
		xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" 
		xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
		xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
		xmlns:xlink="http://www.w3.org/1999/xlink"		
		xmlns:exsl="http://exslt.org/common"
		xmlns:ke  = "kolekti:extensions:functions:publication"
		xmlns:html="http://www.w3.org/1999/xhtml"
		exclude-result-prefixes="html ke"
		extension-element-prefixes="exsl ke"
		>
  <xsl:output indent="yes"/>
  <xsl:param name="pivot"/>

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="style:header/text:p">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:value-of select="document(ke:get_url($pivot))/html:html/html:head/html:title"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
