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
  exclude-result-prefixes="kf"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"/>

  <xsl:template match="/">
   <div class="panel panel-default">
     <form role="form" id="formjob" class="form-horizontal">
       <xsl:apply-templates/>
     </form>
   </div>
  </xsl:template>

  <xsl:template match="dir">
    <div class="form-group">
      <label for="jobdirectory">Dossier de publication</label>
      <input type="text" class="form-control" id="jobdirectory" placeholder="Dossier" />
    </div>
  </xsl:template>

  <xsl:template match="/job/criteria">
    <div class="form-group">
      <h2>Filtres à l'assemblage</h2>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="/job/profiles">
    <div class="form-group">
      <h2>Profils de publication</h2>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="criteria">
    
  </xsl:template>

  <xsl:template match="profile">
    
  </xsl:template>

  <xsl:template match="scripts">
    <div class="form-group">
      <h2>Scripts de publication</h2>
      <xsl:apply-templates/>
    </div>
  </xsl:template>


</xsl:stylesheet>
