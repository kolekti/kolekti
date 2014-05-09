<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:d="DAV:"
                xmlns:km="kolekti:modules"

                xmlns:kf="kolekti:extensions:functions"
                exclude-result-prefixes="d km kf">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="kolekti://utils/ui/xsl/properties.xsl"/>

  <xsl:template match="km:heading">
   <km:heading>
     <p class="heading">
      <span><a href="#usecase"><i:text>[0175]Cas d'emploi</i:text></a></span>
      <span class="case"><a href="#filterview"><i:text>[0179]Vue filtrée</i:text></a></span>
      <span class="case"><a href="#versions"><i:text>[0176]Versions</i:text></a></span>
      <span class="case"><a href="#diagnostic"><i:text>[0180]Diagnostic</i:text></a></span>
      <span class="case"><a href="#notes"><i:text>[0181]Notes de modification</i:text></a></span>
     </p>
   </km:heading>
  </xsl:template>

  <xsl:template match="km:usage">
   <km:usage>
     <div class="usecase">
        <a name="usecase" />
        <h3><i:text>[0175]Cas d'emploi</i:text></h3>
        <div class="sidebar_section">
          <h4><i:text>[0029]Trames</i:text></h4>
          <xsl:choose>
           <xsl:when test="km:trame">
             <ul><xsl:apply-templates /></ul>
           </xsl:when>
           <xsl:otherwise>
             <p><i:text>[0182]Aucune trame</i:text></p>
           </xsl:otherwise>
          </xsl:choose>
        </div>
     </div>
   </km:usage>
  </xsl:template>
  
  <xsl:template match="km:usage/km:trame">
   <li>
      <span style="display: none;">
         <span class="resid"><xsl:value-of select="@resid" /></span>
         <span class="urlid"><xsl:value-of select="@urlid" /></span>
         <span class="url"><xsl:value-of select="@url" /></span>
      </span>
      <span>
         <xsl:apply-templates />
      </span>
   </li>
  </xsl:template>
  
  <xsl:template match="km:filterview">
   <km:filterview>
      <div class="filterview">
        <a name="filterview" />
        <h3><i:text>[0179]Vue filtrée</i:text></h3>
        <div class="sidebar_section">
          <div class="reset_section">
           <span class="vieweritemaction">
              <img class="reset" src="/_lib/kolekti/icons/icon_reset.png" i:alt="[0183]Réinitialiser" i:title="[0184]Réinitialiser le filtrage" />
           </span>
          </div>
          <xsl:for-each select="criteria">
           <xsl:if test="kf:hascriteria(string(@code))">
             <p class="crit_select"><xsl:value-of select="@name" /> (<xsl:value-of select="@code" />)
                <span style="display: none;" class="code"><xsl:value-of select="@code" /></span>
                <select name="{@code}">
                   <option value="">-- <i:text>[0185]Sans filtrage</i:text> --</option>
                   <xsl:for-each select="value">
                      <option value="{@code}"><xsl:value-of select="@name" /> (<xsl:value-of select="@code" />)</option>
                   </xsl:for-each>
                </select>
             </p>
           </xsl:if>
          </xsl:for-each>
        </div>
      </div>
   </km:filterview>
  </xsl:template>

  <xsl:template match="km:versions">
   <km:versions>
      <div class="versions">
        <a name="versions" />
        <h3><i:text>[0176]Versions</i:text></h3>
        <div class="sidebar_section">
         <ul>
      <xsl:for-each select="rev">
        <xsl:variable name="author">
          <xsl:choose>
       <xsl:when test="@uid = -1">
         <xsl:value-of select="@author"/>
       </xsl:when>
       <xsl:otherwise>
         <xsl:value-of select="kf:username(string(@uid))"/>
       </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:variable name="vurl">
          <xsl:value-of select="ancestor::d:response/d:href"/>
          <xsl:text>?rev=</xsl:text>
          <xsl:value-of select="@revnum"/>
       </xsl:variable>
        <li><a href="{$vurl}" target="moduleversion" title="{$author} : {@message}"><xsl:value-of select="kf:format_time(string(@time))"/></a></li>
      </xsl:for-each>
    </ul>
        </div>
      </div>
   </km:versions>
  </xsl:template>

  <xsl:template match="km:diagnostic">
   <km:diagnostic>
      <div class="diagnostic">
        <a name="diagnostic" />
        <h3><i:text>[0180]Diagnostic</i:text></h3>
        <div class="sidebar_section">
          <xsl:apply-templates />
          <xsl:if test="count(child::*) = 0">
            <p><i:text>[0186]Aucune erreur trouvée</i:text></p>
          </xsl:if>
        </div>
      </div>
   </km:diagnostic>
  </xsl:template>

  <xsl:template match="km:diagnostic/warning">
   <p style="color:orange;">
   <xsl:choose>
     <xsl:when test="@criteriascss = '1'"><i:text>[0347]Déclaration de la feuille de style des critères manquante</i:text></xsl:when>
   </xsl:choose>
   </p>
  </xsl:template>

  <xsl:template match="km:diagnostic/error">
   <p style="color:red;">
     <xsl:choose>
       <xsl:when test="@module = '1'">
         <i:text>[0346]Module mal formé</i:text>
       </xsl:when>
       <xsl:when test="@type = 'a'">
         <i:text>[0187]Lien vers le module %(modname)s inexistant
           <i:param name="modname">
             <xsl:attribute name="value">
               <xsl:apply-templates />
             </xsl:attribute>
           </i:param>
         </i:text>
       </xsl:when>
       <xsl:when test="@type = 'img'">
         <i:text>[0189]Image %(imgname)s manquante
           <i:param name="imgname">
             <xsl:attribute name="value">
               <xsl:apply-templates />
             </xsl:attribute>
           </i:param>
         </i:text>
        </xsl:when>
       <xsl:when test="@type = 'embed'">
         <i:text>[0191]Animation %(medname)s manquante
           <i:param name="medname">
             <xsl:attribute name="value">
               <xsl:apply-templates />
             </xsl:attribute>
           </i:param>
         </i:text>
       </xsl:when>
     </xsl:choose>
   </p>
  </xsl:template>

  <xsl:template match="km:diagnostic/criteriaerror">
   <xsl:if test="not(preceding-sibling::criteriaerror[@code=current()/@code])">
      <p style="color:red;">
         <i:text>
            <xsl:text>[0192]Le critère %(code)s n'est pas défini.</xsl:text>
            <i:param name="code" value="{string(@code)}" />
         </i:text>
      </p>
   </xsl:if>
  </xsl:template>

  <xsl:template match="km:diagnostic/criteria_valueerror">
   <xsl:if test="not(preceding-sibling::criteria_valueerror[@code=current()/@code and @value=current()/@value])">
      <p style="color:red;">
         <i:text>
            <xsl:text>[0193]La valeur %(value)s du critère %(code)s n'est pas défini ou valide.</xsl:text>
            <i:param name="value" value="{string(@value)}" />
            <i:param name="code" value="{string(@code)}" />
         </i:text>
      </p>
   </xsl:if>
  </xsl:template>

  <xsl:template match="km:notes">
   <km:notes>
      <div class="notes">
        <a name="notes" />
        <h3><i:text>[0181]Notes de modification</i:text></h3>
        <div class="sidebar_section">
          <textarea>&#xA0;</textarea>
     <xsl:if test="normalize-space(.) != ''">
       <p>
         <em><i:text>[0194]Note précédente</i:text> : </em><br/>
         <xsl:value-of select="."/><br/>
         <button id="sidebarnotecopy"><i:text>[0195]Copier</i:text></button>
       </p>
     </xsl:if>
        </div>
      </div>
   </km:notes>
  </xsl:template>
</xsl:stylesheet>
