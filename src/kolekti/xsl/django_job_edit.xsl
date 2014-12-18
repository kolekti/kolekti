<?xml version="1.0" encoding="ISO-8859-1"?>
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
  xmlns:kf="kolekti:extensions:functions:publication"
  extension-element-prefixes="kf"
  exclude-result-prefixes="kf html"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"/>

  <xsl:param name="path"/>

  <xsl:template match="/">
    <h2><span id="job_id"><xsl:value-of select='job/@id'/></span>
	<span class="pull-right">
	  <button type="button" class="btn btn-default disabled hidden" id="btn_save" data-path="{$path}">
	    Enregistrer
	  </button>
	</span>

    </h2>
    <xsl:apply-templates select="/job/criteria"/>
    <xsl:apply-templates select="/job/profiles"/>
    <xsl:apply-templates select="/job/scripts"/>
  </xsl:template>

  <xsl:template match="dir"/>
<!--
  <xsl:template match="dir">
    <div class="form-group">
      <label for="jobdirectory">Dossier de publication</label>
      <input type="text" class="form-control" id="jobdirectory" placeholder="Dossier" />
    </div>
  </xsl:template>
-->

  <xsl:template match="/job/criteria">
    <div class="panel panel-default">
      <div class="panel-heading"><h4>Préfiltrage<!--Filtres à l'assemblage--></h4></div>
      <div class="panel-body" id="crit_assembly">
	<xsl:apply-templates select="/job/settings/criteria">
	  <xsl:with-param name="profile" select="''"/>
	</xsl:apply-templates>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="/job/profiles">
    <div class="panel panel-default">
      <div class="panel-heading"><h4>Profils de publication</h4></div>
      <div class="panel-body">
	<xsl:apply-templates/>
	<button class="btn btn-default btn-sm" id="btn_add_profil">Ajouter un profil</button>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="/job/scripts">
    <div class="panel panel-default">
      <div class="panel-heading"><h4>Scripts de publication</h4></div>
      <div class="panel-body">
	<div class="form-group">
	  <xsl:apply-templates/>
	</div>
	<div class="btn-group">
	  <button class="btn btn-default btn-sm dropdown-toggle" id="btn_add_script" data-toggle="dropdown" aria-expanded="false">
	    Ajouter un script
	    <span class="caret"/>
	  </button>
	  <ul class="dropdown-menu" role="menu">
	    <xsl:apply-templates select="/job/settings/scripts"/>
	  </ul>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="pubscript">
    <li><a href="#"><xsl:value-of select="name"/></a></li>
  </xsl:template>

  <xsl:template match="profile">
    <div class="job-comp profile">
      <div class="row">
	<div class="col-sm-3 col-xs-12">Profil</div>
	<div class="col-sm-6 col-xs-12">
	  <input type="text" name="profile_name" class="profile-name" value="{label}"/>
	</div>
	<div class="col-sm-3 col-xs-12">
	  <button class="btn btn-default btn-xs suppr">Supprimer</button>
	</div>
      </div>
      <div class="row">
	<div class="col-sm-3 col-xs-12">Dossier</div>
	<div class="col-sm-6 col-xs-12">
	  <input type="text" name="profile_dir" class="profile-dir" value="{dir/@value}"/>
	</div>
	<div class="col-sm-3 col-xs-12">
	  <input type="checkbox">
	    <xsl:if test="@enabled='1'">
	      <xsl:attribute name="checked">checked</xsl:attribute>
	    </xsl:if>
	  </input>
	  <xsl:text> Activé</xsl:text>

	</div>
	
      </div>
      <h5>Filtres à la publication</h5>
      <xsl:variable name="profile" select="label"/>
      <xsl:apply-templates select="/job/settings/criteria">
	<xsl:with-param name="profile" select="$profile"/>
      </xsl:apply-templates>
      <hr/>
    </div>
  </xsl:template>

  <xsl:template match="settings/criteria/criterion">
    <xsl:param name="profile"/>
    <div class="row kolekti-crit">
      <div class="col-sm-3 col-xs-12 kolekti-crit-code">
	<xsl:value-of select="@code"/>
      </div>
      <div class="col-sm-9 col-xs-12">
	<div class="btn-group">
	  <button type="button" class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
	    <span class="kolekti-crit-value-menu">
	      <xsl:choose>
		<xsl:when test="$profile = ''">
		  <xsl:choose>
		    <xsl:when test="/job/profiles/profile[label=$profile]/criteria/criterion[@code=current()/@code]/@value">
		      <xsl:value-of select="/job/profiles/profile[label=$profile]/criteria/criterion[@code=current()/@code]/@value"/>
		    </xsl:when>
		    <xsl:otherwise>non filtré</xsl:otherwise>
		  </xsl:choose>
		</xsl:when>
	      <xsl:otherwise>
		<xsl:choose>
		  <xsl:when test="/job/profiles/profile[label=$profile]/criteria/criterion[@code=current()/@code]/@value">
		    <xsl:value-of select="/job/profiles/profile[label=$profile]/criteria/criterion[@code=current()/@code]/@value"/>
		  </xsl:when>
		    <xsl:otherwise>non filtré</xsl:otherwise>
		  </xsl:choose>
	      </xsl:otherwise>
	    </xsl:choose>
	    </span>
	    <xsl:text> </xsl:text>
	    <span class="caret"/>
	  </button>
	  <ul class="dropdown-menu" role="menu">
	    <xsl:apply-templates>
	      <xsl:with-param name="profile" select="$profile"/>
	    </xsl:apply-templates>
	    <li class="divider"></li>
	    <li><a href="#" class="crit-val-menu-entry">non filtré</a></li>
	  </ul>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="settings/criteria/criterion/value">
    <li><a href="#" class="crit-val-menu-entry"><xsl:value-of select="."/></a></li>
  </xsl:template>

  <xsl:template match="script">
    <div class="job-comp script" data-kolekti-script-id="{/job/settings/scripts/pubscript[@id=current()/@name]/@id}">
      <div class="row">
	<div class="col-sm-9 col-xs-12">
	  <h5><xsl:value-of select="/job/settings/scripts/pubscript[@id=current()/@name]/name"/></h5>
	</div>
	<div class="col-sm-3 col-xs-12">
	  <button class="btn btn-default btn-xs suppr" id="btn_add_profil">Supprimer</button>
	</div>
      </div>
      <div class="row">
	<div class="col-sm-3 col-xs-12">Suffixe</div>
	<div class="col-sm-6 col-xs-12"><input type="text" name="script_suffix" class="script-suffix" value="{suffix}"/></div>
	<div class="col-sm-3 col-xs-12">
	  <input type="checkbox">
	    <xsl:if test="@enabled='1'">
	      <xsl:attribute name="checked">checked</xsl:attribute>
	    </xsl:if>
	  </input>
	  <xsl:text> Activé</xsl:text>
	</div>
      </div>
      <xsl:apply-templates select="parameters"/>
      <hr/>
    </div>
  </xsl:template>

  <xsl:template match="script/parameters/parameter">
    <xsl:apply-templates select="/job/settings/scripts/pubscript[@id=current()/ancestor::script/@name]/parameters/parameter[@name = current()/@name]">
      <xsl:with-param name="value" select="@value"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="pubscript/parameters/parameter">
    <xsl:param name="value"/>

    <div class="row script-parameter" data-script-param-name='{@name}' data-script-param-type='{@type}'>
      <div class="col-sm-3 col-xs-12">
	<xsl:value-of select="@label"/>
      </div>
      <div class="col-sm-9 col-xs-12">
	<xsl:choose>
	  <xsl:when test="@type='filelist'">
	    <div class="btn-group">
	      <button type="button" class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
		<span class="kolekti-crit-value-menu">
		  <xsl:value-of select="$value"/>
		</span>
		<xsl:text> </xsl:text>
		<span class="caret"/>
	      </button>
	      <ul class="dropdown-menu" role="menu">
		<xsl:for-each select="kf:listdir(string(@dir),string(@ext))">
		  <li><a href="#"><xsl:value-of select="."/></a></li>
		</xsl:for-each>
	      </ul>
	    </div>
	  </xsl:when>
	  <xsl:when test="@type='boolean'">
	    <input type="checkbox" class="kolekti-crit-value">
	      <xsl:if test="$value='yes'">
		<xsl:attribute name="checked">checked</xsl:attribute>
	      </xsl:if>
	    </input>
	    <xsl:value-of select="label"/>
	  </xsl:when>
	  <xsl:when test="@type='text'">
	    <input type="text" class="kolekti-crit-value" value="{$value}"/>
	  </xsl:when>
	</xsl:choose>
      </div>
    </div>
  </xsl:template>
</xsl:stylesheet>
