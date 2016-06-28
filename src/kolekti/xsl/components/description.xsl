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
	<link rel="stylesheet" type="text/css" href="/static/components/css/description.css"/>
      </css>
      <scripts>
	<script src="/static/ckeditor/ckeditor.js"/>
	<script src="/static/components/js/description.js"/>
      </scripts>
    </libs>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-component-description']" mode="topictitle"/>

  <xsl:template match="html:div[@class='kolekti-component-description']" mode="topicbody">
    <xsl:apply-templates mode="topicbody"/>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-description']" mode="topicpanelaction"/>

  <xsl:template match="html:div[@class='kolekti-component-description']" mode="topicpanelbutton">
    <a aria-controls="collapseAnalyse{ancestor::html:div[@class='topic']/@id}"
       aria-expanded="false"
       href="#collapseAnalyse{ancestor::html:div[@class='topic']/@id}"
       data-toggle="collapse"
       role="button" class="btn btn-default btn-xs ecorse-action-collapse"><i class="fa fa-pencil"></i> Description</a>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-description']" mode="topicpanel">
    <div role="tabpanel" id="collapseDescription{ancestor::html:div[@class='topic']/@id}"
	 class="collapseDescription collapseTopic collapse">
      <div class="well">
	<div contenteditable="true" class="anaeditor" id="editor{ancestor::html:div[@class='topic']/@id}" >
	  <xsl:apply-templates/>
	</div>
      </div>
    </div>
  </xsl:template>

</xsl:stylesheet>
