<?xml version="1.0" encoding="utf-8"?>
<!--
    kOLEKTi : a structural documentation generator
    Copyright (C) 2007 Stéphane Bonhomme (stephane@exselt.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


-->
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  xmlns:html="http://www.w3.org/1999/xhtml"
  xmlns:diff="http://namespaces.shoobx.com/diff"
  xmlns:ex="http://exslt.org/common"
  exclude-result-prefixes="html diff ex"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
	           omit-xml-declaration="yes"
	           />

  <xsl:include href="django_variables.xsl"/>
  <xsl:include href="django_conditions.xsl"/> 
  <xsl:include href="django_tables.xsl"/>
  <xsl:include href="django_identity.xsl"/>
  <xsl:include href="django_pictures.xsl"/>


  <xsl:template match="/"> 
    <div class="topicdiffsource col-md-12"
         data-diff-count="{count(.//*[@diff:insert]|.//*[@diff:delete]|.//*[@diff:insert-formatting]|.//*[@diff:delete-formatting]|.//diff:insert|.//diff:delete)}"
         >
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  

  <xsl:template name = "popover">
    <xsl:param name="color"/>
    <xsl:param name="content"/>
    <xsl:variable name="diffdetails">
      <xsl:call-template name="diffdetails"/>
    </xsl:variable>
    
    <xsl:variable name="verbatimdiffdetails">
      <xsl:apply-templates select="ex:node-set($diffdetails)" mode="verbatim"/>
    </xsl:variable>
    
    <a tabindex="0"
       class="btn-popover text-{$color}"
       role="button"
       data-toggle="popover"
       data-trigger="focus"
       data-placement="bottom"
       title="Détails de la différence"
       data-content="{$verbatimdiffdetails}">
      <xsl:copy-of select="$content"/>
<!--      <i class="glyphicon glyphicon-plus-sign"/>-->
    </a>    
  </xsl:template>
  
  <xsl:template name="diffdetails">
    <div class="diff row" style="min-width:300px">
      <div class="diff-release col-md-6">
        <p>module source :</p>
        <div class="panel panel-default">
          <div class="panel-body">
            <xsl:apply-templates select="(ancestor-or-self::p|ancestor-or-self::h1|ancestor-or-self::h2|ancestor-or-self::h3|ancestor-or-self::h4|ancestor-or-self::h5|ancestor-or-self::h6|ancestor-or-self::li|ancestor-or-self::dt|ancestor-or-self::dd|ancestor-or-self::td|ancestor-or-self::th)[last()]" mode="diff-pop"/>
          </div>
        </div>
      </div>
      <div class="diff-source col-md-6">
        <p>assemblage :</p>
        <div class="panel panel-default">
          <div class="panel-body">
            <xsl:apply-templates select="(ancestor-or-self::p|ancestor-or-self::h1|ancestor-or-self::h2|ancestor-or-self::h3|ancestor-or-self::h4|ancestor-or-self::h5|ancestor-or-self::h6|ancestor-or-self::li|ancestor-or-self::dt|ancestor-or-self::dd|ancestor-or-self::td|ancestor-or-self::th)[last()]" mode="diff-pop"/>
          </div>
        </div>
      </div>
    </div>

  </xsl:template>

  <xsl:template match="*" mode="diff-pop-list">
    <xsl:value-of select="name()"/>
  </xsl:template>
  
  <xsl:template match="text()" mode="verbatim">
    <xsl:value-of select="."/>
  </xsl:template>
  
  <xsl:template match="*" mode="verbatim">
    <xsl:text disable-output-escaping="yes">&lt;</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:apply-templates select="@*" mode="verbatim"/>
    <xsl:text disable-output-escaping="yes">&gt;</xsl:text>
    <xsl:apply-templates mode="verbatim"/>
    <xsl:text disable-output-escaping="yes">&lt;/</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text disable-output-escaping="yes">&gt;</xsl:text>
  </xsl:template>
  
  <xsl:template match="@*" mode="verbatim">
    <xsl:text disable-output-escaping="yes"> </xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text disable-output-escaping="yes">="</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text disable-output-escaping="yes">"</xsl:text>
  </xsl:template>


  
  <xsl:template name="mark-diff-insert">
    <ins class="diff-insert diff-popup">
      <xsl:call-template name = "popover">
        <xsl:with-param name="color">success</xsl:with-param>
        <xsl:with-param name="content">
          <xsl:apply-templates/>
        </xsl:with-param>
      </xsl:call-template>
    </ins>
  </xsl:template>
      
  <xsl:template name="mark-diff-delete">
    <del class="diff-del diff-popup">
      <xsl:call-template name = "popover">
      <xsl:with-param name="color">danger</xsl:with-param>
        <xsl:with-param name="content">
          <xsl:apply-templates/>
        </xsl:with-param>
      </xsl:call-template>
    </del>
  </xsl:template>

  <xsl:template name="mark-diff-insert-formatting">
    <span class="diff-insert-formatting">
      <xsl:call-template name = "popover">
        <xsl:with-param name="color">success</xsl:with-param>
        <xsl:with-param name="content">
          <xsl:apply-templates/>
        </xsl:with-param>
      </xsl:call-template>
    </span>
  </xsl:template>
  
  <xsl:template name="mark-diff-delete-formatting">
    <span class="diff-delete-formatting">
      <xsl:call-template name = "popover">
        <xsl:with-param name="color">danger</xsl:with-param>        
        <xsl:with-param name="content">
          <xsl:apply-templates/>
        </xsl:with-param>
      </xsl:call-template>
    </span>
  </xsl:template>

  <!-- `diff:insert` and `diff:delete` elements are only placed around
       text. -->
  <xsl:template match="diff:insert">
    <span class="DiffInsert">
      <xsl:call-template name = "popover">
        <xsl:with-param name="color">success</xsl:with-param>
        <xsl:with-param name="content">
          <xsl:apply-templates/>
        </xsl:with-param>
      </xsl:call-template>
    </span>
  </xsl:template>

  <xsl:template match="diff:delete">
    <span class="DiffDelete">
      <xsl:call-template name = "popover">
        <xsl:with-param name="color">danger</xsl:with-param>
        <xsl:with-param name="content">
          <xsl:apply-templates/>
        </xsl:with-param>
      </xsl:call-template>
    </span>
  </xsl:template>

  <!-- If any major paragraph element is inside a diff tag, put the markup
       around the entire paragraph. -->
  <xsl:template match="p|h1|h2|h3|h4|h5|h6">
    <xsl:choose>
      <xsl:when test="ancestor-or-self::*[@diff:insert]">
        <xsl:copy>
          <xsl:call-template name="mark-diff-insert" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="ancestor-or-self::*[@diff:delete]">
        <xsl:copy>
          <xsl:call-template name="mark-diff-delete" />
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates/>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Put diff markup in marked paragraph formatting tags. -->
  <xsl:template match="span|b|i|u|strike|sub|sup">
    <xsl:choose>
      <xsl:when test="@diff:insert">
        <xsl:copy>
          <xsl:call-template name="mark-diff-insert" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="@diff:delete">
        <xsl:copy>
          <xsl:call-template name="mark-diff-delete" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="@diff:insert-formatting">
        <xsl:copy>
          <xsl:call-template name="mark-diff-insert-formatting" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="@diff:delete-formatting">
        <xsl:copy>
          <xsl:call-template name="mark-diff-delete-formatting" />
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates/>
        </xsl:copy>
      </xsl:otherwise>
      </xsl:choose>
  </xsl:template>
  
  <!-- Put diff markup into pseudo-paragraph tags, if they act as paragraph. -->
  <xsl:template match="li|dt|dd|th|td">
    <xsl:variable name="localParas" select="p|h1|h2|h3|h4|h5|h6" />
    <xsl:choose>
      <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:insert]">
        <xsl:copy>
          <p>
            <xsl:call-template name="mark-diff-insert" />
          </p>
        </xsl:copy>
        </xsl:when>
        <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:delete]">
          <xsl:copy>
            <p>
              <xsl:call-template name="mark-diff-delete" />
            </p>
          </xsl:copy>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy>
            <xsl:apply-templates/>
          </xsl:copy>
        </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- popover content -->
  
  <xsl:template name="mark-diff-insert-pop">
    <ins class="diff-insert">
      <xsl:apply-templates mode="diff-pop"/>
    </ins>
  </xsl:template>
      
  <xsl:template name="mark-diff-delete-pop">
    <del class="diff-del">
      <xsl:apply-templates mode="diff-pop"/>
    </del>
  </xsl:template>

  <xsl:template name="mark-diff-insert-formatting-pop">
    <span class="diff-insert-formatting">
      <xsl:apply-templates mode="diff-pop"/>
    </span>
  </xsl:template>
  
  <xsl:template name="mark-diff-delete-formatting-pop">
    <span class="diff-delete-formatting">
      <xsl:apply-templates mode="diff-pop"/>
    </span>
  </xsl:template>

  <!-- `diff:insert` and `diff:delete` elements are only placed around
       text. -->
  <xsl:template match="diff:insert" mode="diff-pop">
    <span class="DiffInsert">
      <xsl:apply-templates mode="diff-pop"/>
    </span>
  </xsl:template>

  <xsl:template match="diff:delete" mode="diff-pop">
    <span class="DiffDelete">
      <xsl:apply-templates mode="diff-pop"/>
    </span>
  </xsl:template>

  <!-- If any major paragraph element is inside a diff tag, put the markup
       around the entire paragraph. -->
  <xsl:template match="p|h1|h2|h3|h4|h5|h6" mode="diff-pop">
    <xsl:choose>
      <xsl:when test="ancestor-or-self::*[@diff:insert]">
        <xsl:copy>
          <xsl:call-template name="mark-diff-insert-pop" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="ancestor-or-self::*[@diff:delete]">
        <xsl:copy>
          <xsl:call-template name="mark-diff-delete-pop" />
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates mode="diff-pop"/>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Put diff markup in marked paragraph formatting tags. -->
  <xsl:template match="span|b|i|u|strike|sub|sup" mode="diff-pop">
    <xsl:choose>
      <xsl:when test="@diff:insert">
        <xsl:copy>
          <xsl:call-template name="mark-diff-insert-pop" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="@diff:delete">
        <xsl:copy>
          <xsl:call-template name="mark-diff-delete-pop" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="@diff:insert-formatting">
        <xsl:copy>
          <xsl:call-template name="mark-diff-insert-formatting-pop" />
        </xsl:copy>
      </xsl:when>
      <xsl:when test="@diff:delete-formatting">
        <xsl:copy>
          <xsl:call-template name="mark-diff-delete-formatting-pop" />
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates mode="diff-pop"/>
        </xsl:copy>
      </xsl:otherwise>
      </xsl:choose>
  </xsl:template>
  
  <!-- Put diff markup into pseudo-paragraph tags, if they act as paragraph. -->
  <xsl:template match="li|dt|dd|th|td" mode="diff-pop">
    <xsl:variable name="localParas" select="p|h1|h2|h3|h4|h5|h6" />
    <xsl:choose>
      <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:insert]">
        <xsl:copy>
          <p>
            <xsl:call-template name="mark-diff-insert-pop" />
          </p>
        </xsl:copy>
        </xsl:when>
        <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:delete]">
          <xsl:copy>
            <p>
              <xsl:call-template name="mark-diff-delete-pop" />
            </p>
          </xsl:copy>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy>
            <xsl:apply-templates mode="diff-pop"/>
          </xsl:copy>
        </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
