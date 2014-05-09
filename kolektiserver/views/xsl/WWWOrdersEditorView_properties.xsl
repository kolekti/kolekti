<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:d="DAV:"
                xmlns:kc="kolekti:configuration"
                xmlns:ks="kolekti:scripts"
                xmlns:kt="kolekti:trames"

                exclude-result-prefixes="i d kc ks kt">

  <xsl:import href="WWWConfigurationView_properties.xsl" />
  <xsl:output method="xml" indent="yes"/>

  <!-- ####################################### -->
  <!-- Templates for listpubprofiles properties -->
  <!-- ####################################### -->  

  <xsl:template match="kc:listpubprofiles">
   <kc:listpubprofiles>
      <ul>
         <xsl:apply-templates />
      </ul>
   </kc:listpubprofiles>
  </xsl:template>

  <xsl:template match="kc:listpubprofiles/profile">
   <li>
      <span>
       <input type="checkbox" id="{@name}" name="{@name}" value="{@resid}">
        <xsl:if test="@checked='checked'">
          <xsl:attribute name="checked">checked</xsl:attribute>
        </xsl:if>
       </input>
       <label for="{@name}"><xsl:value-of select="@name" /></label>
       <xsl:variable name="dirid">
        <xsl:value-of select="substring-before(@url, '/publication_profiles/')" />
        <xsl:text>/publication_profiles?open=</xsl:text>
       </xsl:variable>
       <span class="profilelink">
        (<a href="{concat($dirid, substring-after(@url, '/publication_profiles/'))}"><i:text>[0324]ouvrir</i:text></a>)
       </span>
     </span>
     <xsl:apply-templates select="details" mode="profiledetails" />
   </li>
  </xsl:template>

  <xsl:template match="details/kc:profile/publication_profile" mode="profiledetails">
      <div class="profiledetails">
        <p class="profilepivname"><span class="label"><i:text>[0143]Nom du pivot</i:text>:</span><xsl:value-of select="pivname/@name" /></p>
        <p class="profilepubpath"><span class="label"><i:text>[0144]Répertoire de publication</i:text>:</span><xsl:value-of select="pubpath/@src" /></p>
        <div class="profilecriterias">
           <p class="label"><i:text>[0145]Critères</i:text></p>
           <xsl:choose>
              <xsl:when test="count(criterias/criteria) &gt; 0">
                <ul><xsl:apply-templates select="criterias/criteria" mode="profiledetails" /></ul>
              </xsl:when>
              <xsl:otherwise><i:text>[0197]Aucune critère de sélectionné</i:text></xsl:otherwise>
           </xsl:choose>
        </div>
        <div class="profilescripts">
           <p class="label">Scripts</p>
           <xsl:choose>
              <xsl:when test="count(scripts/script) &gt; 0">
                <ul><xsl:apply-templates select="scripts/script" mode="profiledetails" /></ul>
              </xsl:when>
              <xsl:otherwise><i:text>[0198]Aucune script de sélectionné</i:text></xsl:otherwise>
           </xsl:choose>
        </div>
      </div>
  </xsl:template>

  <xsl:template match="criterias/criteria" mode="profiledetails">
   <li><xsl:value-of select="@code" /> = <xsl:value-of select="@value" /></li>
  </xsl:template>

  <xsl:template match="scripts/script" mode="profiledetails">
   <li>
      <xsl:value-of select="@label" /> (<xsl:value-of select="@name" />)
      <xsl:if test="parameters/parameter">
         <ul>
            <xsl:for-each select="parameters/parameter">
               <li><xsl:value-of select="@name" /> = <xsl:value-of select="@value" /></li>
            </xsl:for-each>
         </ul>
      </xsl:if>
   </li>
  </xsl:template>

</xsl:stylesheet>