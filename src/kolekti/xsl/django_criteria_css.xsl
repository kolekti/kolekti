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
    
       color: red;
       display:block;
       font-size: 11px;
       font-family: sans-serif;
       font-style: normal;
       font-weight:normal;
       background-color: #F0F0F0;
       border-bottom: 1px solid #D0D0D0;
       padding: 1px;
       margin:0;
    }

    span[class~="="]:before,
    a[class~="="]:before,
    strong[class~="="]:before,
    em[class~="="]:before,
    sub[class~="="]:before,
    sup[class~="="]:before,
    s[class~="="]:before,
    u[class~="="]:before,
    ins[class~="="]:before {
    display:inline;
    border-right: 1px solid #D0D0D0;
    padding-right:2px;
    margin-right:2px;
    }
    
    
    tr[class~="="] td{
       border: 2px solid purple;
       }
       .=:before {
           color:blue}
       <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="criterion">
    .<xsl:value-of select="@code"/>:before {
    color:blue
    }
    <xsl:apply-templates/>
  </xsl:template>

    <xsl:template match="value">
      .<xsl:value-of select="."/>:before {
    color:blue
    }
    </xsl:template>
</xsl:stylesheet>
