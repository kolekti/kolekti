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

  <xsl:output  method="html" 
               indent="yes"/>

  <xsl:param name="path"/>

  <xsl:template match="/">
    <h4>Paramètres de publication</h4>
    <h2><span id="job_id"><xsl:value-of select='job/@id'/></span></h2>
    <div id="job_body">
      <xsl:apply-templates select="/job/criteria"/>
      <xsl:apply-templates select="/job/profiles"/>
      <xsl:apply-templates select="/job/scripts"/>
    </div>
    <div class="job-templates hidden">
      <xsl:call-template name="profil"/>
      <xsl:call-template name="pubscripts"/>
    </div>
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
      <div class="panel-heading">
	<a class="collapsed" data-toggle="collapse" href="#collapse_{generate-id()}">
	  <small data-ui="yes">
	    <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
	    <span class="glyphicon glyphicon-chevron-down" aria-hidden="false"></span>
	  </small>
	  <strong>Filtrage avant assemblage</strong>
	</a>
      </div>

      <div class="panel-collapse collapse" id="collapse_{generate-id()}">
	<div class="panel-body" id="crit_assembly">
	  <div class="form form-horizontal">
	    <xsl:apply-templates select="/job/settings/criteria">
	      <xsl:with-param name="profile" select="''"/>
	    </xsl:apply-templates>
	  </div>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="/job/profiles">
    <div class="panel panel-default">
      <div class="panel-heading">
	<a data-toggle="collapse" href="#collapse_{generate-id()}">
	  <small data-ui="yes">
	    <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
	    <span class="glyphicon glyphicon-chevron-down" aria-hidden="false"></span>
	  </small>
	  <strong>Profils</strong>
	</a>
      </div>
      <div class="panel-collapse collapse in" id="collapse_{generate-id()}">
	<div class="panel-body">
	  <div id="job_profiles">
	    <xsl:apply-templates/>
	  </div>
	  <button class="btn btn-default btn-sm" id="btn_add_profil">Ajouter un profil</button>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="/job/scripts">
    <div class="panel panel-default">
      <div class="panel-heading">
	<a data-toggle="collapse" href="#collapse_{generate-id()}">
	  <small data-ui="yes">
	    <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
	    <span class="glyphicon glyphicon-chevron-down" aria-hidden="false"></span>
	  </small>
	  <strong>Sorties</strong>
	</a>
      </div>
      <div class="panel-collapse collapse in" id="collapse_{generate-id()}">
	<div class="panel-body">
	  <div id="job_scripts">
	    <xsl:apply-templates/>
	  </div>
	  <div class="btn-group">
	    <button class="btn btn-default btn-sm dropdown-toggle" id="btn_add_script" data-toggle="dropdown" aria-expanded="false">
	      Ajouter une sortie
	      <span class="caret"/>
	    </button>
	    <ul class="dropdown-menu" role="menu">
	      <xsl:apply-templates select="/job/settings/scripts" mode="scripts_menu"/>
	    </ul>
	  </div>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="pubscript" mode="scripts_menu">
    <li><a href="#" class="script-menu-item" data-kolekti-script-id="{@id}"><xsl:value-of select="name"/></a></li>
  </xsl:template>

  <xsl:template match="profile" name="profil">
    <div class="panel panel-default job-comp profile">
      <div class="panel-body">
	<div class="row">
	  <div class="col-sm-6 col-xs-12">
	    <div class="row">
	      <div class="col-sm-6 col-xs-12">
		<label for="profil_name_{generate-id()}"><strong>Nom du profil</strong></label>
	      </div>
	      <div class="col-sm-6 col-xs-12">
		<input type="text" name="profile_name" class="profile-name" value="{label}" id="profil_name_{generate-id()}"/>
	      </div>
	      <div class="col-sm-6 col-xs-12">
		<label for="profil_dir_{generate-id()}">Dossier</label>
	      </div>
	      <div class="col-sm-6 col-xs-12">
		<input type="text" name="profile_dir" class="profile-dir" value="{dir/@value}" id="profil_dir_{generate-id()}" />
	      </div>
	    </div>
	  </div>
	  <div class="col-sm-6 col-xs-12">
	    <div class="checkbox">
	      <label>
		<input type="checkbox" class="profile-enabled">
		  <xsl:if test="@enabled='1'">
		    <xsl:attribute name="checked">checked</xsl:attribute>
		  </xsl:if>
		</input>
		<xsl:text> Profil actif</xsl:text>
	      </label>
	    </div>
	  </div>
	</div>
	<h5>Filtres à la publication</h5>
	<xsl:variable name="profile" select="label"/>
	<xsl:apply-templates select="/job/settings/criteria">
	  <xsl:with-param name="profile" select="$profile"/>
	  <xsl:with-param name="template" select="local-name() != 'profile'"/>
	</xsl:apply-templates>
	<hr/>
	<div class="pull-right">
	  <button class="btn btn-default btn-xs suppr">Supprimer</button>
	</div>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template name="criterion-value">
    <xsl:param name="profile"/>
    <xsl:param name="nofilter" select="'Pas de filtrage'"/>
    <xsl:param name="userselect" select="'Sélection utilisateur'"/>
    <xsl:choose>
      <xsl:when test="$profile = ''">
	<xsl:choose>
	  <xsl:when test="/job/criteria/criterion[@code=current()/@code]">
	    <xsl:value-of select="/job/criteria/criterion[@code=current()/@code]/@value"/>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="$nofilter"/>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:otherwise>
	<xsl:choose>
	  <xsl:when test="/job/profiles/profile[label=$profile]/criteria/criterion[@code=current()/@code]/@value">
	    <xsl:value-of select="/job/profiles/profile[label=$profile]/criteria/criterion[@code=current()/@code]/@value"/>
	  </xsl:when>
	  <xsl:when test="/job/profiles/profile[label=$profile]/criteria/criterion[@code=current()/@code]">
	    <xsl:value-of select="$userselect"/>
	  </xsl:when>
	  <xsl:otherwise><xsl:value-of select="$nofilter"/></xsl:otherwise>
	</xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="settings/criteria/criterion">
    <xsl:param name="profile"/>
    <xsl:param name="template" select="false()"/>
    <div class="row kolekti-crit" data-kolekti-crit-code="{@code}">
      <xsl:attribute name="data-kolekti-crit-value">
	<xsl:call-template name="criterion-value">
	  <xsl:with-param name="profile" select="$profile"/>
	  <xsl:with-param name="nofilter" select="''"/>
	  <xsl:with-param name="userselect" select="'*'"/>
	</xsl:call-template>
      </xsl:attribute>
      <div class="col-sm-3 col-xs-12 kolekti-crit-code">
	<xsl:value-of select="@code"/>
      </div>
      <div class="col-sm-9 col-xs-12">
	<div class="btn-group">
	  <button type="button" class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
	    <span class="kolekti-crit-value-menu">
	      <xsl:call-template name="criterion-value">
		<xsl:with-param name="profile" select="$profile"/>
	      </xsl:call-template>
	    </span>
	    <xsl:text> </xsl:text>
	    <span class="caret"/>
	  </button>
	  <ul class="dropdown-menu" role="menu">
	    <xsl:apply-templates>
	      <xsl:with-param name="profile" select="$profile"/>
	    </xsl:apply-templates>
	    <li class="divider"></li>
	    <xsl:if test="$template or $profile != ''">
	      <li><a href="#" class="crit-val-menu-entry" data-kolekti-crit-value="*">Sélection utilisateur</a></li>
	      <li class="divider"></li>
	    </xsl:if>
	    <li><a href="#" class="crit-val-menu-entry" data-kolekti-crit-value="">Pas de filtrage</a></li>
	  </ul>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="settings/criteria/criterion/value">
    <li><a href="#" class="crit-val-menu-entry" data-kolekti-crit-value="{.}"><xsl:value-of select="."/></a></li>
  </xsl:template>





  <xsl:template match="script">
    <div class="panel panel-default job-comp script {@name}" data-kolekti-script-id="{@name}">
      <div class="panel-body">
	<div class="row">
	  <div class="col-sm-9 col-xs-12">
	    <h5><strong><xsl:value-of select="/job/settings/scripts/pubscript[@id=current()/@name]/name"/></strong></h5>	    
	  </div>
	</div>

	<div class="row">
	  <div class="col-sm-6 col-xs-12">
	    <div class="row">
	      <div class="col-sm-6 col-xs-12">
		<label for="script_filename_{generate-id()}">Nom des fichier publiés</label>
	      </div>
	      <div class="col-sm-6 col-xs-12">
		<input type="text" name="script_filename" class="script-filename" id="script_filename_{generate-id()}" value="{filename}"/>
	      </div>
	    </div>
	  </div>
	  <div class="col-sm-6 col-xs-12">
	    <div class="checkbox">
	      <label>
		<input type="checkbox" class="script-enabled">
		  <xsl:if test="@enabled='1'">
		    <xsl:attribute name="checked">checked</xsl:attribute>
		  </xsl:if>
		</input>
		<xsl:text> Sortie active</xsl:text>
	      </label>
	    </div>
	  </div>
	</div>
	<xsl:apply-templates select="parameters"/>
	<hr/>
	<div class="pull-right">
	  <button class="btn btn-default btn-xs suppr">Supprimer</button>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="script/parameters/parameter">
    <xsl:apply-templates select="/job/settings/scripts/pubscript[@id=current()/ancestor::script/@name]/parameters/parameter[@name = current()/@name]">
      <xsl:with-param name="value" select="@value"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template name="pubscripts">
    <xsl:apply-templates select="/job/settings/scripts/pubscript"/>
  </xsl:template>

  <xsl:template match="pubscript"> <!-- template for new scripts -->
    <div class="panel panel-default job-comp script {@id}" data-kolekti-script-id="{@id}">
      <div class="panel-body">
	<div class="row">
	  <div class="col-sm-9 col-xs-12">
	    <h5><strong><xsl:value-of select="name"/></strong></h5>
	  </div>
	</div>
	
	<div class="row">
	  <div class="col-sm-6 col-xs-12">
	    <div class="row">
	      <div class="col-sm-6 col-xs-12">
		<label for="script_filename_{generate-id()}">Nom des fichier publiés</label>
	      </div>
	      <div class="col-sm-6  col-xs-12">
		<input type="text" name="script_filename" class="script-filename" id="script_filename_{generate-id()}" value=""/>
	
	      </div>
	    </div>
	  </div>
	  <div class="col-sm-6 col-xs-12">
	    <div class="checkbox">
	      <label>
		<input type="checkbox" class="script-enabled" checked="checked"/>
		<xsl:text> Sortie active</xsl:text>
	      </label>
	    </div>
	  </div>
	</div>
	<xsl:apply-templates select="parameters/parameter"/>
	<hr/>
	<div class="pull-right">
	  <button class="btn btn-default btn-xs suppr">Supprimer</button>
	</div>
      </div>
    </div>
  </xsl:template>



  <xsl:template match="pubscript/parameters/parameter">
    <xsl:param name="value" select="''"/>

    <div class="row script-parameter" data-script-param-name='{@name}' data-script-param-type='{@type}' data-kolekti-param-value="{$value}">
      <div class="col-sm-3 col-xs-12">
	<label for="script-param_{generate-id()}">
	  <xsl:value-of select="@label"/>
	</label>
      </div>
      <div class="col-sm-9 col-xs-12">
	<xsl:choose>
	  <xsl:when test="@type='filelist'">
	    <div class="btn-group kolekti-param-menu">
	      <button type="button" class="btn btn-default btn-sm dropdown-toggle kolekti-param" data-toggle="dropdown" aria-expanded="false">
		<span class="kolekti-param-value-menu">
		  <xsl:value-of select="$value"/>
		  <xsl:text> </xsl:text>
		</span>
		<xsl:text> </xsl:text>
		<span class="caret"/>
	      </button>
	      <ul class="dropdown-menu" role="menu">
		<xsl:for-each select="kf:listdir(string(@dir),string(@ext))">
		  <li><a href="#" class="script-param-menu-entry" data-kolekti-param-value="{.}"><xsl:value-of select="."/></a></li>
		</xsl:for-each>
	      </ul>
	    </div>
	  </xsl:when>
	  <xsl:when test="@type='boolean'">
	    <input type="checkbox" class="kolekti-crit-value" id="script-param_{generate-id()}">
	      <xsl:if test="$value='yes'">
		<xsl:attribute name="checked">checked</xsl:attribute>
	      </xsl:if>
	    </input>
	  </xsl:when>
	  <xsl:when test="@type='text'">
	    <input type="text" class="kolekti-crit-value" value="{$value}" id="script-param_{generate-id()}"/>
	  </xsl:when>
	</xsl:choose>
      </div>
    </div>
  </xsl:template>
</xsl:stylesheet>
