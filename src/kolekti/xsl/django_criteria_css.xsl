<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  version="1.0">

  <xsl:output  method="text" />
  <xsl:template match="/">
    *[class~="="] {
       border: 1px solid blue;
       margin: 2px 2px 2px 2px;
       padding: 2px 2px 2px 2px;
    }
    
    *[class~="="]:before {
       content : attr(class);
       color: blue;
       display:block;
       font-size: 11px;
       border-bottom: 1px solid #D0D0D0;
       padding: 2px;
       margin:0;
    }

    tr[class~="="] td{
       border: 2px solid purple;
    }
  </xsl:template>

  <xsl:template match="criterion">
  </xsl:template>
</xsl:stylesheet>
