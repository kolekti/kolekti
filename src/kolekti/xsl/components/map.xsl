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
    xmlns="http://www.w3.org/1999/xhtml" 
    exclude-result-prefixes="html"
    version="1.0">
  
  <xsl:template match="/libs">
    <libs>
      <css>
	<link rel="stylesheet" type="text/css" href="/static/components/css/map.css"/>
	<!--<link href="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css" rel="stylesheet"/>-->
	<link rel="stylesheet" href="https://npmcdn.com/leaflet@0.7.7/dist/leaflet.css" />
	
      </css>
      <scripts>
<!--	<script src="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js"></script>-->
	<script src="https://npmcdn.com/leaflet@0.7.7/dist/leaflet.js"></script>

<!--	  <script src="/static/leaflet.min.js"/>-->
	<script src="/static/components/js/map.js"/>
      </scripts>
    </libs>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-component-map']" mode="topictitle"/>
  <xsl:template match="html:div[@class='kolekti-component-map']" mode="topicbody">
    <div class="lfcontainer">
      <div class="leafletmap" data-geojson="{string(.//html:div[@class='kolekti-sparql-result-json'])}"  style="width: 100%; height: 245px">
      </div>
      
    </div>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-map']" mode="topicpanelinfo">
    <div class="lfcontainer">
      <div class="leafletmappanel" data-geojson="{string(.//html:div[@class='kolekti-sparql-result-json'])}"  style="width: 100%; height: 245px">
      </div>
      
    </div>
  </xsl:template>
  <xsl:template match="html:div[@class='kolekti-component-map']" mode="topicpanelaction"/>
  <xsl:template match="html:div[@class='kolekti-component-map']" mode="topicpanelbutton"/>
  <xsl:template match="html:div[@class='kolekti-component-map']" mode="topicpanelbody"/>

</xsl:stylesheet>
