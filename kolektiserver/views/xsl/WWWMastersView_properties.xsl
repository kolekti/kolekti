<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:d="DAV:"
                xmlns:k="kolekti"

                exclude-result-prefixes="i kf d k">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="kolekti://utils/ui/xsl/properties.xsl"/>

  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />

  <!-- ####################################### -->
  <!-- Templates for history properties -->
  <!-- ####################################### -->  

  <xsl:template match="k:history">
   <k:history>
    <div class="logs">
      <table>
        <thead>
          <th><i:text>[0243]Nom de l'enveloppe</i:text></th>
          <th><i:text>[0244]Date de l'ajout</i:text></th>
          <th><i:text>[0172]Auteur</i:text></th>
        </thead>
        <tbody>
          <xsl:apply-templates select="listfiles/file">
            <xsl:sort select="@time" order="descending" />
          </xsl:apply-templates>
        </tbody>
      </table>
    </div>
   </k:history>
  </xsl:template>

  <xsl:template match="k:history/listfiles/file">
   <xsl:variable name="masterfile" select="substring-after(@resid, 'masters/')" />
   <tr>
     <td><a href="/projects/{$project/@directory}/masters?open={$masterfile}"><xsl:value-of select="$masterfile" /></a></td>
     <td><xsl:value-of select="kf:format_time(string(@time))" /></td>
     <td><xsl:value-of select="kf:username(string(@uid))" /></td>
   </tr>
  </xsl:template>
</xsl:stylesheet>
