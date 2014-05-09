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
                xmlns:dav="DAV:"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kol kf ke kcd kd dav">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="kcd:data">
   <xsl:apply-templates select="kcd:namespace[@id='http']/kcd:value[@key='body']" />
  </xsl:template>

  <xsl:template match="criterias">
   <div id="criterias">
     <xsl:apply-templates select="criteria"/>
     <p id="btn_addcriterias"><span><i:text>[0153]Ajouter un critère</i:text></span></p>
   </div>
  </xsl:template>  

  <xsl:template match="criteria">
    <div class="criteria">
      <p>
        <span class="criteria_name"><label><i:text>[0079]Nom</i:text>:</label><input type="text" name="criteria_name" value="{@name}" /></span>
        <span class="criteria_code"><label><i:text>[0154]Code</i:text>:</label><input type="text" name="criteria_code" value="{@code}" /></span>
        <span class="criteria_type">
          <label for="criteria_type"><i:text>[0155]Type</i:text>:</label>
          <select name="criteria_type">
            <option value="text"><xsl:if test="@type='text'"><xsl:attribute name="selected">selected</xsl:attribute></xsl:if><i:text>[0156]Texte</i:text></option>
            <option value="enum"><xsl:if test="@type='enum'"><xsl:attribute name="selected">selected</xsl:attribute></xsl:if><i:text>[0157]Enumération</i:text></option>
            <option value="int"><xsl:if test="@type='int'"><xsl:attribute name="selected">selected</xsl:attribute></xsl:if><i:text>[0158]Entier</i:text></option>
          </select>
        </span>
        <span class="criteria_delete"><img src="/_lib/kolekti/icons/btn_close.png" alt="X" i:title="[0159]Supprimer le critère"/></span>
      </p>
    <xsl:choose>
      <xsl:when test="@type='enum'">
         <xsl:call-template name="enumvalue" />
      </xsl:when>
      <xsl:when test="@type='int'">
         <xsl:call-template name="intvalue" />
      </xsl:when>
    </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template name="enumvalue">
    <div class="criteriasvalues">
      <xsl:for-each select="value">
        <p>
         <span class="criteria_value"><label for="value"><i:text>[0160]Valeur</i:text>:</label><input type="text" name="value" value="{@name}"/></span>
         <span class="criteria_code"><label for="code"><i:text>[0154]Code</i:text>:</label><input type="text" name="code" value="{@code}"/></span>
         <span class="criteria_delete"><img src="/_lib/kolekti/icons/btn_close.png" alt="X" i:title="[0161]Supprimer la valeur"/></span>
        </p>
      </xsl:for-each>
      <p class="btn_addvalue"><span><i:text>[0162]Ajouter une valeur</i:text></span></p>
    </div>
  </xsl:template>

  <xsl:template name="intvalue">
    <div class="criteriasvalues">
      <p>
         <span class="criteria_min"><label><i:text>[0163]Min</i:text>:</label><input type="text" name="min" value="{range/@min}"/></span>
         <span class="criteria_max"><label><i:text>[0164]Max</i:text>:</label><input type="text" name="max" value="{range/@max}"/></span>
      </p>
    </div>
  </xsl:template>  
</xsl:stylesheet>