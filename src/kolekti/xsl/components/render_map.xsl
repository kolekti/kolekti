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
  
  <xsl:include href="map.xsl"/>
  
  <xsl:template match="/html:div">
    <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;</xsl:text>
    <html>
      <head>
	<title>Leaflet</title>
	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>

	<link rel="stylesheet" href="{$static}/leaflet/leaflet.css" />	  
	<link rel='stylesheet' type="text/css" link="{$static}/components/css/map.css"/>
	<script src="{$static}/jquery.js"> </script>
	<script src="{$static}/leaflet/leaflet.js"> </script>
	<script src="{$static}/components/js/map_functions.js"> </script>
      </head>
      <body>
	<div class="leafletmap" data-geojson="{string(.//html:div[@class='kolekti-sparql-result-json'])}" style="width: 600px; height: 400px"></div>
<!--
	<script>
	  $(function() {
	  var maplist = $('div');
	  console.log($('div'));
	  window.drawmap(maplist.get(0), function() {
	  console.log("done");
	  });
	  });
	</script>
-->
      </body>
    </html>
  </xsl:template>
  
</xsl:stylesheet>
