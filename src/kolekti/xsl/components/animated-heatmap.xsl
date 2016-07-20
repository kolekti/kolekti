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
	<link rel="stylesheet" type="text/css" href="/static/components/css/animated-heatmap.css"/>
	<link href="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css" rel="stylesheet"/>
	<link href='https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css' rel='stylesheet' />

      </css>
      <scripts>
	  <script src="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js"></script>
	  <script src="/static/leaflet.min.js"/>
	  <script src='https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js'></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/jslib/webgl-heatmap.js"></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/jslib/webgl-heatmap-leaflet.js"></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/js/map/rec-layer.js"></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/js/map/map-display.js"></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/js/map/animated-layer.js"></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/js/map/data-layer.js"></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/js/navigation-bar.js"></script>
	  <script src="/static/Leaflet_Animated_Data_Layer/js/app.js"></script>
	  <script src="/static/components/js/animated-heatmap.js"/>
      </scripts>
    </libs>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-component-animated-heatmap']" mode="topictitle"/>
  <xsl:template match="html:div[@class='kolekti-component-animated-heatmap']" mode="topicbody">
    <div class="lfcontainer">
      <div class="leafletanimatedheatmap"
	   id = "{generate-id()}"
	   data-geojson="{string(.//html:div[@class='kolekti-sparql-result-json'])}"  style="width: 100%; height: 1245px">
      </div>
      <div id="navigation">
	<fieldset>
	  <legend>Animate</legend>
	  <button id="button_start">Start</button>
	  <button id="button_pause" disabled="disabled">Pause</button>
	  |
	  <label for="input_date">Date</label>
	  <input type="text" id="input_date" disabled="disabled" />
	  |
	  <label for="select_data">Data</label>
	  <select id="select_data" disabled="disabled">
	    <option value="sampleData1">Data 1</option>
	    <option value="sampleData2">Data 2</option>
	  </select>
	  </fieldset>
	  <fieldset>
	    <legend>Animation settings</legend>
	    <label for="checkbox_loop">Loop</label>
	    <input type="checkbox" id="checkbox_loop" />
	    |
	    <label for="select_visualization">Visualization</label>
	    <select id="select_visualization">
	      <option value="circle">Circle</option>
	      <option value="rectangle">Rectangle</option>
	      <option value="dot">Dot</option>
	      <option value="heatmap">Heatmap (WebGL)</option>
	      <option value="rec">Rec</option>
	    </select>
	    |
	    <label for="select_speed">Speed</label>
	    <select id="select_speed">
	      <option value="1">Super slow (1fps)</option>
	      <option value="5">Slow (5fps)</option>
	      <option value="10" selected="yes">Medium (10fps)</option>
	      <option value="15">Fast (15fps)</option>
	      <option value="1000">No limit</option>
	    </select>
	  </fieldset>
	  <input type="range" id="slider_date" min="0" step="1"  value="0"/>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-animated-heatmap']" mode="topicpanelinfo">
    <div class="lfcontainer">
      <div class="leafletanimatedheatmappanel" data-geojson="{string(.//html:div[@class='kolekti-sparql-result-json'])}"  style="width: 100%; height: 245px">
      </div>
      
    </div>
  </xsl:template>
  <xsl:template match="html:div[@class='kolekti-component-animated-heatmap']" mode="topicpanelaction"/>
  <xsl:template match="html:div[@class='kolekti-component-animated-heatmap']" mode="topicpanelbutton"/>
  <xsl:template match="html:div[@class='kolekti-component-animated-heatmap']" mode="topicpanelbody"/>

</xsl:stylesheet>
