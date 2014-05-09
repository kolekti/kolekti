<?xml version="1.0" encoding="utf-8"?>
<!--

     kOLEKTi : a structural documentation generator
     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

-->
<?doc UI generation for action components
?>
<?author Stéphane Bonhomme <stephane@exselt.com>?>

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kd="kolekti:dialogs"
                xmlns:e="http://exslt.org/common"
                extension-element-prefixes="ke e"
                exclude-result-prefixes="i kf kd h e">

  <xsl:template match="/h:html//kd:action[@ref]" mode="include">
    <!-- handle once each action -->
    <xsl:if test="not(preceding::kd:action[@ref=current()/@ref])">
      <xsl:apply-templates select="document(concat($kolektiapp,'/ui/actions/',@ref,'.xml'))" mode="include"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="/h:html//kd:action[@ref]">
    <xsl:if test="not(preceding::kd:action[@ref=current()/@ref])">
      <xsl:variable name="inbrowser" select="boolean(ancestor::kd:browser)"/>
      <xsl:apply-templates select="document(concat($kolektiapp,'/ui/actions/',@ref,'.xml'))">
        <xsl:with-param name="inbrowser" select="$inbrowser"/>
      </xsl:apply-templates>
    </xsl:if>
  </xsl:template>

  <xsl:template match="/kd:action" mode="include">
    <!-- include js if class is defined -->
    <xsl:if test="@class">
      <script type="text/javascript" src="/_lib/app/scripts/actions/{@class}.js">
        <xsl:text>&#x0D;</xsl:text>
      </script>
      <link href="/_lib/app/css/actions/{@class}.css" media="all" rel="stylesheet" type="text/css" />
    </xsl:if>
    <xsl:if test=".//kd:ajaxbrowser">
      <!-- objects for tab management -->
      <xsl:apply-templates select=".//kd:ajaxbrowser" mode="include"/>
    </xsl:if>
    <script type="text/javascript">
      <!-- generate actions initializations -->
      var button, tmp, parentobj;
      <xsl:apply-templates select="." mode="head"/>
    </script>
  </xsl:template>


  <!--  **********************  -->
  <!--  actions                 -->
  <!--  **********************  -->

  <!--  **********************  -->
  <!--  actions head part       -->
  <!--  **********************  -->
  <xsl:template match="/kd:action" mode="head">
    <xsl:choose>
      <xsl:when test="@class">
        tmp=new <xsl:value-of select="@class" />('<xsl:value-of select="@id" />');
      </xsl:when>
      <xsl:otherwise>
        tmp=new kolekti_action('<xsl:value-of select="@id" />');
      </xsl:otherwise>
    </xsl:choose>
    if(typeof(tmp.initevent) == "function")
    tmp.initevent();

    kolekti.actions['<xsl:value-of select="@id" />'] = tmp;

    var this_=kolekti;
    <!--//tmp.objid=this.id;-->
    <xsl:apply-templates select="@*|@i:*" mode="script"/>
    <!-- // dialogs-->
    <xsl:apply-templates select="kd:dialog" mode="script"/>
    <!-- // process -->
    <xsl:apply-templates select="kd:process" mode="script"/>
    <!-- // result-->
    <xsl:apply-templates select="kd:result" mode="script"/>
    <!-- // end action <xsl:value-of select="@id"/>-->
  </xsl:template>

  <xsl:template match="/kd:action/@*|/kd:action/@i:*" mode="script">
    tmp.<xsl:value-of select="local-name()"/>='<xsl:apply-templates select="." mode="i18n" />';
  </xsl:template>

  <!-- dialog windows -->

  <xsl:template match="kd:dialog" mode="script">
    tmp= kolekti.actions['<xsl:value-of select="ancestor::kd:action/@id" />'];
    tmp.hasdialog=true;
    tmp.dialogtype='<xsl:value-of select="@type"/>';
    <xsl:if test="@type='ajax'">
      tmp.dialogurl='<xsl:value-of select="@url"/>';
      <xsl:if test="kd:header">
        tmp.headers=new Object();
        <xsl:apply-templates select="kd:header" mode="script"/>
      </xsl:if>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@onopen">
        kolekti.listen('dialog_open',function(arg){this_.<xsl:value-of select="@onopen"/>(arg)},this.id);
      </xsl:when>
      <xsl:when test=".//kd:ajaxbrowser">
        <xsl:for-each select=".//kd:ajaxbrowser">
          <xsl:text>tmp.browsers.push('</xsl:text><xsl:value-of select="@id"/><xsl:text>');</xsl:text>
        </xsl:for-each>
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates mode="script"/>
  </xsl:template>

  <xsl:template match="kd:dialog//text()" mode="script"/>


  <xsl:template match="kd:dialog//kd:propselect" mode="script">
    tmp=kolekti.actions['<xsl:value-of select="ancestor::kd:action/@id" />'].addselector('<xsl:value-of select="@id"/>');
    tmp.url='<xsl:value-of select="@url" />';
    tmp.property='<xsl:value-of select="@property" />';
    tmp.nsproperty='<xsl:value-of select="@nsproperty" />';
  </xsl:template>

  <xsl:template match="kd:dialog//kd:ajaxregion" mode="script">
    tmp=kolekti.actions['<xsl:value-of select="ancestor::kd:action/@id" />'].addajaxregion('<xsl:value-of select="@id"/>');
    tmp.url='<xsl:value-of select="@url" />';
    <xsl:if test="@update">
      tmp.update='<xsl:value-of select="@update" />';
    </xsl:if>
    <xsl:if test="kd:header">
      tmp.headers=new Object();
      <xsl:apply-templates select="kd:header" mode="script"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="kd:dialog//kd:button" mode="script">
    button=kolekti.actions['<xsl:value-of select="ancestor::kd:action/@id" />'].adddialogbutton('<xsl:value-of select="@label"/>');
    //button process
    <xsl:apply-templates select="kd:process|kd:result" mode="script"/>
    //button process end
  </xsl:template>


  <!-- action / button process -->

  <xsl:template match="kd:action/kd:process" mode="script">
    parentobj=kolekti.actions['<xsl:value-of select="ancestor::kd:action/@id" />'];
    //set action buttons
    <xsl:apply-templates  mode="script"/>
  </xsl:template>

  <xsl:template match="kd:button/kd:process" mode="script">
    // button process
    parentobj=button;
    <xsl:apply-templates  mode="script"/>
  </xsl:template>

  <xsl:template match="kd:process/kd:http" mode="script">
    tmp=parentobj.addprocess('http');
    tmp.method='<xsl:value-of select="@method"/>';
    <xsl:if test="@id">
      tmp.id='<xsl:value-of select="@id"/>';
    </xsl:if>
    <xsl:if test="@url">
      tmp.defurl='<xsl:value-of select="@url"/>';
    </xsl:if>
    <xsl:if test="@urlext">
      tmp.urlext='<xsl:value-of select="@urlext"/>';
    </xsl:if>
    <xsl:if test="kd:header">
      tmp.headers=new Object();
      <xsl:apply-templates select="kd:header" mode="script"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="kd:process/kd:dav" mode="script">
    tmp=parentobj.addprocess('dav');
    tmp.method='<xsl:value-of select="@method"/>';
    <xsl:if test="@id">
      tmp.id='<xsl:value-of select="@id"/>';
    </xsl:if>
    <xsl:if test="@url">
      tmp.defurl='<xsl:value-of select="@url"/>';
    </xsl:if>
    <xsl:if test="@urlext">
      tmp.urlext='<xsl:value-of select="@urlext"/>';
    </xsl:if>
    <xsl:if test="kd:header">
      tmp.headers=new Object();
      <xsl:apply-templates select="kd:header" mode="script"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="kd:process//kd:header" mode="script">
    tmp.headers['<xsl:value-of select="@name"/>']='<xsl:value-of select="@content"/>';
  </xsl:template>

  <xsl:template match="kd:process/kd:notify" mode="script">
    tmp=parentobj.addprocess('notify');
    tmp.event='<xsl:value-of select="@event" />';
    <xsl:if test="@id">
      tmp.id='<xsl:value-of select="@id"/>';
    </xsl:if>
    <xsl:if test="@context='true'">
      tmp.with_context=true;
    </xsl:if>
    <xsl:if test="kd:param">
      tmp.params=new Object();
      <xsl:apply-templates select="kd:param" mode="script"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="kd:notify/kd:param" mode="script">
    tmp.params['<xsl:value-of select="@name"/>']='<xsl:value-of select="@content"/>';
  </xsl:template>

  <xsl:template match="kd:param[@process-result]" mode="script">
    tmp.params['<xsl:value-of select="@name"/>']=new Object;
    tmp.params['<xsl:value-of select="@name"/>'].processresult=true;
    tmp.params['<xsl:value-of select="@name"/>'].processid='<xsl:value-of select="@process-result"/>';

  </xsl:template>

  <!-- action / button results -->

  <xsl:template match="kd:action/kd:result" mode="script">
    parentobj=kolekti.actions['<xsl:value-of select="ancestor::kd:action/@id" />'];
    <xsl:apply-templates  mode="script"/>
  </xsl:template>

  <xsl:template match="kd:button/kd:result" mode="script">
    parentobj=button;
    <xsl:apply-templates  mode="script"/>
  </xsl:template>

  <xsl:template match="kd:result/kd:*/kd:notify" mode="script">
    // notify
    tmp=parentobj.addresult('<xsl:value-of select="local-name(parent::*)"/>','notify');
    tmp.event='<xsl:value-of select="@event" />';
    <xsl:if test="@context='true'">
      tmp.with_context=true;
    </xsl:if>
    <xsl:if test="kd:param">
      tmp.params=new Object();
      <xsl:apply-templates select="kd:param" mode="script"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="kd:result/kd:*/kd:message" mode="script">
    // message
    tmp=parentobj.addresult('<xsl:value-of select="local-name(parent::*)"/>','message');
  </xsl:template>

  <xsl:template match="kd:result/kd:*/kd:status" mode="script">
    tmp=afunc('<xsl:value-of select="local-name(parent::*)"/>','status');
  </xsl:template>


  <!--  **********************  -->
  <!--  actions body part       -->
  <!--  **********************  -->

  <xsl:template match="/kd:action">
    <xsl:param name="inbrowser" select="false()"/>
    <div class="action" id="action_{@id}">
      <xsl:if test="not($inbrowser)">
        <span class="label">
          <xsl:choose>
            <xsl:when test="kd:icon">
              <img src="{kd:icon}">
               <xsl:choose>
                  <xsl:when test="kd:label/i:text">
                     <xsl:attribute name="i:alt">
                        <xsl:value-of select="kd:label/i:text" />
                     </xsl:attribute>
                  </xsl:when>
                  <xsl:otherwise>
                     <xsl:attribute name="alt">
                        <xsl:value-of select="kd:label" />
                     </xsl:attribute>
                  </xsl:otherwise>
               </xsl:choose>
              </img>
            </xsl:when>
            <xsl:when test="kd:label">
              <xsl:copy-of select="kd:label/node()" />
            </xsl:when>
            <xsl:otherwise>
               <xsl:apply-templates select="@name|@i:name" mode="i18n" />
            </xsl:otherwise>
          </xsl:choose>
        </span>
      </xsl:if>

      <xsl:apply-templates select="kd:dialog"/>
      <xsl:apply-templates select="kd:upload-dialog"/>
      <xsl:apply-templates select="kd:result"/>
    </div>
  </xsl:template>

  <xsl:template match="/kd:action/kd:dialog">
    <div class="dialog" id="action_dialog_{ancestor::kd:action/@id}">
      <xsl:copy-of select="@title|@i:title" />
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="/kd:action/kd:dialog//kd:propselect">
    <select name="{@name}" id="{ancestor::kd:action/@id}_{@id}">
      <option value="0">Loading...</option>
    </select>
  </xsl:template>


  <xsl:template match="/kd:action/kd:dialog//kd:ajaxregion">
    <fieldset id="{ancestor::kd:action/@id}_{@id}" style="display:none"><xsl:copy-of select="@class"/>Loading...</fieldset>
  </xsl:template>

  <xsl:template match="/kd:action/kd:result/kd:*/kd:message">
    <div class="dialog" id="action_dialog_{ancestor::kd:action/@id}_{local-name(parent::*)}">
      <xsl:copy-of select="@title|@i:title" />
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="/kd:action/kd:result/kd:*/kd:status">
    <div class="dialog" id="action_dialog_{ancestor::kd:action/@id}_{local-name(parent::*)}">
      <xsl:copy-of select="@title|@i:title" />
      <xsl:comment/>
    </div>
  </xsl:template>
</xsl:stylesheet>
