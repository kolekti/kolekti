<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:d="DAV:"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:kc="kolekti:configuration"
                xmlns:ks="kolekti:scripts"
                xmlns:kt="kolekti:trames"

                exclude-result-prefixes="i d kf kc ks kt">

  <xsl:output method="xml" indent="yes"/>

  <xsl:include href="kolekti://utils/ui/xsl/properties.xsl"/>

  <!-- ################## -->
  <!-- Sidebar properties -->
  <!-- ################## -->

  <xsl:template match="kc:versions">
   <kc:versions>
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
          <xsl:text>&amp;viewer=orderseditor</xsl:text>
       </xsl:variable>
        <li><a href="{$vurl}" target="configurationversion" title="{$author} : {@message}"><xsl:value-of select="kf:format_time(string(@time))"/></a></li>
      </xsl:for-each>
    </ul>
        </div>
      </div>
   </kc:versions>
  </xsl:template>

  <xsl:template match="kc:notes">
   <kc:notes>
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
   </kc:notes>
  </xsl:template>

  <!-- #################################### -->
  <!-- Templates for pubprofiles properties -->
  <!-- #################################### -->

  <xsl:template match="kc:profile">
   <kc:profile>
      <fieldset>
         <div class="actions">
            <ul>
               <li>
                  <input type="checkbox" name="enabled" id="{generate-id()}" checked="checked" />
                  <label for="{generate-id()}"><i:text>[0330]Actif</i:text></label>
               </li>
               <li><button class="delete"><i:text>[0095]Supprimer</i:text></button></li>
            </ul>
         </div>
         <div class="profile">
            <p class="profilelabel">
               <label for="label{generate-id()}"><i:text>[0150]Label</i:text></label>
               <span class="formvalue">
                  <input id="label{generate-id()}" type="text" name="label" value="{publicationprofile/label/text()}"/>
               </span>
            </p>
	         <xsl:apply-templates select="kf:getcriterias()" mode="profile">
	            <xsl:with-param name="pcriterias" select="publicationprofile/criterias" />
	         </xsl:apply-templates>
         </div>
      </fieldset>
   </kc:profile>
  </xsl:template>

  <xsl:template match="criterias/criteria" mode="profile">
   <xsl:param name="pcriterias" />
   <xsl:variable name="curcriteria" select="$pcriterias/criteria[@code=current()/@code]" />
   <div class="criteria">
      <span class="formselect">
         <input type="checkbox" name="enabled" id="{generate-id($curcriteria)}">
            <xsl:if test="$curcriteria/@checked = '1'">
               <xsl:attribute name="checked">checked</xsl:attribute>
            </xsl:if>
         </input>
         <label for="{generate-id($curcriteria)}"><xsl:value-of select="@name" /> (<xsl:value-of select="@code" />)</label>
      </span>
      <span class="formvalue">
         <xsl:choose>
            <xsl:when test="@type = 'enum'">
               <select id="criteria_{generate-id()}" name="{@code}">
                  <xsl:for-each select="value">
                     <xsl:sort select="@name" />
                     <option value="{@code}">
                        <xsl:if test="$curcriteria/@value = @code">
                           <xsl:attribute name="selected">selected</xsl:attribute>
                        </xsl:if>
                     <xsl:value-of select="@name" /> (<xsl:value-of select="@code" />)</option>
                  </xsl:for-each>
               </select>
            </xsl:when>
            <xsl:when test="@type = 'int'">
               <select id="criteria_{generate-id()}" name="{@code}">
                  <xsl:call-template name="optloopvalue">
                     <xsl:with-param name="curval" select="range/@min" />
                     <xsl:with-param name="max" select="range/@max" />
                  </xsl:call-template>
               </select>
            </xsl:when>
            <xsl:otherwise>
               <input type="text" name="{@code}" id="criteria_{generate-id()}" value="{$curcriteria/@value}" />
            </xsl:otherwise>
         </xsl:choose>
      </span>
   </div>
  </xsl:template>
  
  <xsl:template name="optloopvalue">
   <xsl:param name="curval" />
   <xsl:param name="max" />

   <option value="{$curval}"><xsl:value-of select="$curval" /></option>

   <xsl:if test="$curval &lt; $max">
      <xsl:call-template name="optloopvalue">
         <xsl:with-param name="curval" select="$curval+1" />
         <xsl:with-param name="max" select="$max" />
      </xsl:call-template>
   </xsl:if>
  </xsl:template>

  <!-- ############################### -->
  <!-- Templates for script properties -->
  <!-- ############################### -->
  
  <xsl:template match="ks:script">
   <ks:script>
      <fieldset class="script">
         <legend><xsl:value-of select="pubscript/name" /></legend>
         <div class="actions">
            <ul>
               <li>
                  <input type="checkbox" name="enabled" id="{generate-id()}" checked="checked" />
                  <label for="{generate-id()}"><i:text>[0330]Actif</i:text></label>
               </li>
               <li><button class="delete"><i:text>[0095]Supprimer</i:text></button></li>
            </ul>
         </div>
         <div class="script">
            <input type="hidden" name="name" value="{pubscript/@id}" />
            <p class="suffix">
               <input type="checkbox" name="suffix" id="suffixe{generate-id()}"/>
               <label for="suffixe{generate-id()}"><i:text>[0332]Suffixe</i:text></label>
               <span class="formvalue">
                  <input type="text" name="suffixeval" id="{generate-id()}" value="{suffixe/text()}" />
               </span>
            </p>
            <xsl:for-each select="pubscript/parameters/parameter">
               <p class="parameter">
                  <xsl:choose>
                     <xsl:when test="@type = 'boolean'">
                        <input type="checkbox" name="{@name}" id="{generate-id()}" />
                        <label for="{generate-id()}"><xsl:value-of select="@label" /></label>
                     </xsl:when>
                     <xsl:when test="@type = 'filelist'">
                        <xsl:variable name="ext" select="@ext" />
                        <label for="{generate-id()}"><xsl:value-of select="@label" /></label>
                        <select name="{@name}" id="{generate-id()}">
                           <xsl:comment>options list</xsl:comment>
                           <xsl:for-each select="kf:listtemplates(concat('@design/publication/', @dir))">
                              <xsl:variable name="name" select="substring-before(@value, concat('.', $ext))" />
                              <xsl:if test="$name != ''">
                                 <option value="{$name}"><xsl:value-of select="$name" /></option>
                              </xsl:if>
                           </xsl:for-each>
                        </select>
                     </xsl:when>
                     <xsl:otherwise>
                        <label for="{generate-id()}"><xsl:value-of select="@label" /></label>
                        <input type="text" name="{@name}" id="{generate-id()}" />
                     </xsl:otherwise>
                  </xsl:choose>
               </p>
            </xsl:for-each>
         </div>
      </fieldset>
   </ks:script>
  </xsl:template>
</xsl:stylesheet>
