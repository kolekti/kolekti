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
  
  <xsl:include href="WWWConfigurationView_properties.xsl"/>

  <xsl:variable name="projectdir">/projects/<xsl:value-of select="kf:get_http_data('kolekti', 'project')/@directory" /></xsl:variable>

  <xsl:template match="node()|@*">
      <xsl:apply-templates select="node()|@*" />
  </xsl:template>

  <xsl:template match="kcd:data">
   <xsl:apply-templates select="kcd:namespace[@id='http']/kcd:value[@key='body']" />
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='http']/kcd:value[@key='body']">
   <xsl:call-template name="orderseditor" />
  </xsl:template>

  <xsl:template name="orderseditor">
   <div class="orderseditor">
     <xsl:call-template name="orderparams" />
     <xsl:call-template name="trames" />
     <xsl:apply-templates select="order/profiles" />
     <xsl:apply-templates select="order/scripts" />
   </div>
  </xsl:template>

  <xsl:template name="orderparams">
   <p class="pubdir">
      <label for="pubdir"><i:text>[0144]Répertoire de publication</i:text></label>
      <span class="formvalue">
         <input id="pubdir" type="text" name="pubdir" value="{order/pubdir/@value}"/>
      </span>
   </p>
   <p class="pubtitle">
      <label for="pubtitle"><i:text>[0345]Titre du document</i:text></label>
      <span class="formvalue">
         <input id="pubtitle" type="text" name="pubtitle" value="{order/pubtitle/@value}"/>
      </span>
   </p>
  </xsl:template>

  <xsl:template name="trames">
   <xsl:variable name="tramesrc">
      <xsl:choose>
         <xsl:when test="starts-with(order/trame/@value, '@trames/') or starts-with(order/trame/@value, '/projects/')"> 
            <xsl:value-of select="substring-after(order/trame/@value, 'trames/')" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:value-of select="order/trame/@value" />
         </xsl:otherwise>
      </xsl:choose>  
   </xsl:variable>

   <fieldset>
     <legend><i:text>[0171]Trame</i:text></legend>
     <div class="trames">
       <p>
         <span class="wndfield">
           <input type="text" name="trameurl" value="{$tramesrc}" />
         </span>
       </p>   
       <p class="tramechoose">
         <span class="ui-icon ui-icon-plusthick" style="float: left;">&#xA0;</span>
         <span><i:text>[0199]Afficher l'explorateur</i:text></span>
       </p>
       <iframe style="display: none;" src="{$projectdir}/trames?trames_select=1"><xsl:text>&#xA0;</xsl:text></iframe> 
     </div>
   </fieldset>
  </xsl:template>

  <xsl:template match="profiles">
   <fieldset>
     <legend><i:text>[0200]Profils de publication</i:text></legend>
     <xsl:apply-templates />
     <p class="addprofile">
      <select name="profile">
         <option value=""><i:text>[0329]Nouveau profil vierge</i:text></option>
         <xsl:for-each select="kf:listtemplates('@configuration/publication_profiles/')">
            <xsl:sort select="@value" />
            <option value="{@value}"><xsl:value-of select="substring-before(@value, '.')" /></option>
         </xsl:for-each>
      </select>
      <button><i:text>[0120]Ajouter</i:text></button>
     </p>
   </fieldset>
  </xsl:template>

  <xsl:template match="profiles/profile">
   <fieldset>
      <div class="actions">
         <ul>
            <li>
               <input type="checkbox" name="enabled" id="{generate-id()}">
                  <xsl:if test="@enabled='1'">
                     <xsl:attribute name="checked">checked</xsl:attribute>
                  </xsl:if>
               </input>
               <label for="{generate-id()}"><i:text>[0330]Actif</i:text></label>
            </li>
            <li><button class="delete"><i:text>[0095]Supprimer</i:text></button></li>
         </ul>
      </div>
      <div class="profile">
         <p class="profilelabel">
            <label for="label{generate-id()}"><i:text>[0150]Label</i:text></label>
            <span class="formvalue">
               <input id="label{generate-id()}" type="text" name="label" value="{label/text()}"/>
            </span>
         </p>
         <xsl:apply-templates select="kf:getcriterias()" mode="profile">
            <xsl:with-param name="pcriterias" select="criterias" />
         </xsl:apply-templates>
      </div>
   </fieldset>
  </xsl:template>

  <xsl:template match="scripts">
   <xsl:variable name="pubscripts" select="kf:getpubscripts()" />
   <fieldset>
      <legend><i:text>[0331]Sorties</i:text></legend>
      <xsl:apply-templates select="script">
         <xsl:with-param name="pubscripts" select="$pubscripts" />
      </xsl:apply-templates>
      <p class="addscript">
         <select name="profile">
            <xsl:comment>list of scripts</xsl:comment>
            <xsl:for-each select="$pubscripts/pubscript">
               <xsl:sort select="name/text()" />
               <option value="{@id}"><xsl:value-of select="name" /></option>
            </xsl:for-each>
         </select>
         <button><i:text>[0120]Ajouter</i:text></button>
      </p>
   </fieldset>
  </xsl:template>

  <xsl:template match="scripts/script">
   <xsl:param name="pubscripts" />
   <fieldset class="script">
      <legend><xsl:value-of select="$pubscripts/pubscript[@id=current()/@name]/name" /></legend>
      <div class="actions">
         <ul>
            <li>
               <input type="checkbox" name="enabled" id="{generate-id()}">
                  <xsl:if test="@enabled='1'">
                     <xsl:attribute name="checked">checked</xsl:attribute>
                  </xsl:if>
               </input>
               <label for="{generate-id()}"><i:text>[0330]Actif</i:text></label>
            </li>
            <li><button class="delete"><i:text>[0095]Supprimer</i:text></button></li>
         </ul>
      </div>
      <div class="script">
         <input type="hidden" name="name" value="{@name}" />
         <p class="suffix">
            <input type="checkbox" name="suffix" id="suffix{generate-id()}">
              <xsl:if test="suffix/@enabled='1'">
                <xsl:attribute name="checked">checked</xsl:attribute>
              </xsl:if>
            </input>
            <label for="suffix{generate-id()}"><i:text>[0332]Suffixe</i:text></label>
            <span class="formvalue">
               <input type="text" name="suffixval" id="{generate-id()}" value="{suffix/text()}" />
            </span>
         </p>
         <xsl:variable name="curelem" select="." />
         <xsl:for-each select="$pubscripts/pubscript[@id=current()/@name]/parameters/parameter">
            <p class="parameter">
               <xsl:choose>
                  <xsl:when test="@type = 'boolean'">
                     <input type="checkbox" name="{@name}" id="{generate-id()}">
                        <xsl:if test="$curelem/parameters/parameter[@name=current()/@name]/@value='1'">
                           <xsl:attribute name="checked">checked</xsl:attribute>
                        </xsl:if>
                     </input>
                     <label for="{generate-id()}"><xsl:value-of select="@label" /></label>
                  </xsl:when>
                  <xsl:when test="@type = 'filelist'">
                     <xsl:variable name="ext" select="@ext" />
                     <label for="{generate-id()}"><xsl:value-of select="@label" /></label>
                     <select name="{@name}" id="{generate-id()}">
                        <xsl:comment>options list</xsl:comment>
                        <xsl:variable name="param" select="." />
                        <xsl:for-each select="kf:listtemplates(concat('@design/publication/', @dir))">
                           <xsl:variable name="name" select="substring-before(@value, concat('.', $ext))" />
                           <xsl:if test="$name != ''">
                              <option value="{$name}">
                                 <xsl:if test="concat($curelem/parameters/parameter[@name=$param/@name]/@value, '.', $ext) = @value">
                                    <xsl:attribute name="selected">selected</xsl:attribute>
                                 </xsl:if>
                                 <xsl:value-of select="$name" />
                              </option>
                           </xsl:if>
                        </xsl:for-each>
                     </select>
                  </xsl:when>
                  <xsl:otherwise>
                     <label for="{generate-id()}"><xsl:value-of select="@label" /></label>
                     <input type="text" name="{@name}" id="{generate-id()}" value="{$curelem/parameters/parameter[@name=current()/@name]/@value}"/>
                  </xsl:otherwise>
               </xsl:choose>
            </p>
         </xsl:for-each>
     </div>
   </fieldset>
  </xsl:template>
</xsl:stylesheet>