<xsl:stylesheet
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
xmlns:math="http://www.w3.org/1998/Math/MathML"
xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
xmlns:ooo="http://openoffice.org/2004/office"
xmlns:ooow="http://openoffice.org/2004/writer"
xmlns:oooc="http://openoffice.org/2004/calc"
xmlns:dom="http://www.w3.org/2001/xml-events"
xmlns:xforms="http://www.w3.org/2002/xforms"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:rpt="http://openoffice.org/2005/report"
xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
xmlns:xhtml="http://www.w3.org/1999/xhtml"
xmlns:grddl="http://www.w3.org/2003/g/data-view#"
xmlns:tableooo="http://openoffice.org/2009/table"
xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0"
version="1.0"
>

<xsl:template match="/variables">
<office:document-content office:version="1.2" grddl:transformation="http://docs.oasis-open.org/office/1.2/xslt/odf2rdf.xsl">
  <office:scripts/>
  <office:font-face-decls>
    <style:font-face style:name="Arial1" svg:font-family="Arial" style:font-pitch="variable"/>
    <style:font-face style:name="Times New Roman" svg:font-family="'Times New Roman'" style:font-family-generic="roman" style:font-pitch="variable"/>
    <style:font-face style:name="Arial" svg:font-family="Arial" style:font-family-generic="swiss" style:font-pitch="variable"/>
    <style:font-face style:name="Calibri" svg:font-family="Calibri" style:font-family-generic="swiss" style:font-pitch="variable"/>
    <style:font-face style:name="Arial Unicode MS" svg:font-family="'Arial Unicode MS'" style:font-family-generic="system" style:font-pitch="variable"/>
    <style:font-face style:name="Mangal" svg:font-family="Mangal" style:font-family-generic="system" style:font-pitch="variable"/>
    <style:font-face style:name="Tahoma" svg:font-family="Tahoma" style:font-family-generic="system" style:font-pitch="variable"/>
  </office:font-face-decls>
  <office:automatic-styles>
    <style:style style:name="co1" style:family="table-column">
      <style:table-column-properties fo:break-before="auto" style:column-width="5.989cm"/>
    </style:style>
    <style:style style:name="ro1" style:family="table-row">
      <style:table-row-properties style:row-height="0.900cm" fo:break-before="auto" style:use-optimal-row-height="true"/>
    </style:style>
    <style:style style:name="ce1" style:family="table-cell" style:parent-style-name="Default" style:data-style-name="N0">
      <style:table-cell-properties fo:background-color="transparent" fo:wrap-option="wrap" fo:border="none" style:vertical-align="top"/>
    </style:style>
    <style:style style:name="ce2" style:family="table-cell" style:parent-style-name="Default" style:data-style-name="N1">
      <style:table-cell-properties fo:background-color="#e6e6e6" fo:wrap-option="wrap" fo:border="0.06pt solid #000000" style:vertical-align="top"/>
      <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>

    </style:style>
    <style:style style:name="ta1" style:family="table" style:master-page-name="Default">
      <style:table-properties table:display="true" style:writing-mode="lr-tb"/>
    </style:style>
    <style:style style:name="T1" style:family="text">
      <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="T2" style:family="text">
      <style:text-properties fo:font-style="italic" style:font-style-asian="italic" style:font-style-complex="italic"/>
    </style:style>
    <style:style style:name="T3" style:family="text">
      <style:text-properties style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
    </style:style>
    <style:style style:name="T4" style:family="text">
      <style:text-properties fo:font-size="10pt" style:text-position="super" style:font-size-asian="10pt" style:font-size-complex="10pt"/>
    </style:style>
    <style:style style:name="T5" style:family="text">
      <style:text-properties style:text-position="sub"/>
    </style:style>


    
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      <table:calculation-settings table:case-sensitive="false" table:automatic-find-labels="false" table:use-regular-expressions="false">
        <table:iteration table:maximum-difference="0.0001"/>
      </table:calculation-settings>
      <table:table table:name="Variables" table:style-name="ta1">
	<xsl:apply-templates select="variable[1]" mode="table-column"/>
	<xsl:apply-templates select="critlist" mode="table-rowcrits"/>
	<xsl:apply-templates select="variable" mode="table-rowvalues"/>
      </table:table>	  
      <table:named-expressions/>
    </office:spreadsheet>
  </office:body>
</office:document-content>
</xsl:template>

<xsl:template match="value" mode="table-column">
  <table:table-column table:style-name="co1" table:default-cell-style-name="ce1"/>
</xsl:template>

<xsl:template match="critlist" mode="table-rowcrits">
  <table:table-row table:style-name="ro1">
    <table:table-cell table:style-name="ce2" office:value-type="string">
      <text:p><xsl:value-of select="."/></text:p>
    </table:table-cell>
    <xsl:apply-templates select="following-sibling::variable[1]/value/crit[concat(':',@name) = current()]" mode="table-rowcrits"/>
  </table:table-row>
</xsl:template>

<xsl:template match="crit" mode="table-rowcrits">
  <table:table-cell table:style-name="ce2" office:value-type="string">
    <text:p><xsl:value-of select="@value"/></text:p>
  </table:table-cell>
</xsl:template>

<xsl:template match="variable" mode="table-rowvalues">
  <table:table-row table:style-name="ro1">
    <table:table-cell table:style-name="ce2" office:value-type="string">
      <text:p>&amp;<xsl:value-of select="@code"/></text:p>
    </table:table-cell>
    <xsl:apply-templates select="value" mode="table-rowvalues"/>
  </table:table-row>
</xsl:template>

<xsl:template match="value" mode="table-rowvalues">
  <table:table-cell table:style-name="ce1" office:value-type="string">
    <xsl:apply-templates select="content" mode="table-rowvalues"/>
  </table:table-cell>
</xsl:template>

<xsl:template match="content" mode="table-rowvalues">
  <text:p><xsl:apply-templates mode="table-rowvalues"/></text:p>
</xsl:template>



<xsl:template match="strong" mode="table-rowvalues">
  <text:span text:style-name="T1">
    <xsl:apply-templates mode="table-rowvalues"/>
  </text:span>
</xsl:template>

<xsl:template match="em" mode="table-rowvalues">
  <text:span text:style-name="T2">
    <xsl:apply-templates mode="table-rowvalues"/>
  </text:span>
</xsl:template>

<xsl:template match="span[@style='text-decoration: underline']" mode="table-rowvalues">
  <text:span text:style-name="T3">
    <xsl:apply-templates mode="table-rowvalues"/>
  </text:span>
</xsl:template>

<xsl:template match="sup" mode="table-rowvalues">
  <text:span text:style-name="T4">
    <xsl:apply-templates mode="table-rowvalues"/>
  </text:span>
</xsl:template>

<xsl:template match="sub" mode="table-rowvalues">
  <text:span text:style-name="T5">
    <xsl:apply-templates mode="table-rowvalues"/>
  </text:span>
</xsl:template>

</xsl:stylesheet>
