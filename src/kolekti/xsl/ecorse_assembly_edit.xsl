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

  
  <xsl:output  method="html" 
               indent="yes"
	       omit-xml-declaration="yes"
	       />

  <xsl:param name="path"/>
  <xsl:param name="section" select="''"/>
  <xsl:param name="share" select="'False'"/>

  <xsl:include href="ecorse_components.xsl"/>
  
  <xsl:template match="text()|@*">
    <xsl:copy/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="*[namespace-uri(self::*)='http://www.w3.org/1999/xhtml']" priority="-10">
    <xsl:element name="{local-name()}" namespace="">
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  

  <xsl:template match="html:h1">
    <xsl:element name="h{count(ancestor::html:div[@class='section']) + 1}" namespace="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match = "html:div[@class='section']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="html:h1"/>
      <div class="section-content niv{count(ancestor::html:div[@class='section']) + 1}" id="section_{@id}" aria-multiselectable="true">
	  <xsl:apply-templates select="html:div"/>
      </div>
    </xsl:copy>
  </xsl:template>

  <xsl:template match = "html:div[@class='section'][count(ancestor::html:div[@class='section']) = 0]">
    <xsl:copy>
      <xsl:apply-templates select="@id"/>
      <div>
	<xsl:apply-templates select="html:h1"/>
      </div>
      <p></p>
      <div class="panel-group" role="tablist" id="section_{@id}" aria-multiselectable="false">
	<xsl:apply-templates select="html:div"/>
      </div>
    </xsl:copy>
  </xsl:template>

  <xsl:template match = "html:div[@class='section'][count(ancestor::html:div[@class='section'])=1]">
    <xsl:if test="$share='False' or html:div[@class='topic'][not(@data-hidden='yes')]">
      <div class="panel panel-default" id="{@id}">
	<div class="panel-heading" role="tab" id="heading_{@id}">
	  <h3 class="panel-title {html:h1/@class}">
	    <a data-toggle="collapse" href="#collapse_section_{@id}" aria-controls="collapse_section_{@id}" data-parent="#section_{ancestor::html:div[@class='section']/@id}">
	      <xsl:apply-templates select="html:h1/node()"/>
	    </a>
	  </h3>
	</div>
	<div  class="panel-collapse collapse section-content" role="tabpanel" aria-labelledby="heading_{@id}" id="collapse_section_{@id}">
	  <div class="panel-body">
	    <xsl:apply-templates select="html:div"/>
	  </div>
	</div>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="node()|@*" mode="topicbody">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>



  
  <xsl:template match = "html:div[@class='topic']">
    <xsl:if test="$share='False' or not(@data-hidden='yes')">
      <div class="col-sm-12 col-lg-6">
	<xsl:copy>
	  <xsl:apply-templates select="@*"/>
	  <xsl:attribute name="class">
	    <xsl:text>topic</xsl:text>
	    <xsl:if test="@data-hidden = 'yes'">
	      <xsl:text> disabled</xsl:text>
	    </xsl:if>
	  </xsl:attribute>
	  
	  <div class="panel panel-default">
	    <div class="panel-heading">
	      <xsl:apply-templates mode="topictitle"/>
	    </div>
	    
	    <div class="panel-body">
	      
	      <!-- création du corps du topic -->
	      <xsl:apply-templates mode="topicbody"/>
	    </div>
	    <!-- pied de topic : collapse / boutons action-->
	    <div class="panel-footer">
	      <p>&#xA0;
	      <xsl:call-template name="topic-controls"/>
	      </p>
	    </div>
	  </div>
	  <div class="modal fade modal-topic-details">
	    <div class="modal-dialog modal-lg">
	      <div class="modal-content">
		<div class="modal-header">
		  <h4 class="modal-title">
		    <xsl:apply-templates mode="topictitle"/>
		  </h4>
		</div>
		<div class="modal-body">
		  <div class="row">
		    <div class="col-md-4">
		      <xsl:apply-templates mode="topicpanelinfo"/>
		      <xsl:if test="$share='False'">
			<hr/>
			
			<h5>Actions</h5>
			<xsl:apply-templates mode="topicpanelaction"/>
		      </xsl:if>
		    </div>
		    <div class="col-md-8">
		      <xsl:apply-templates mode="topicpanelbutton"/>
		      <xsl:apply-templates mode="topicpanelbody"/>
		    </div>
		  </div>
		</div>
		<div class="modal-footer">
		  <xsl:choose>
		    <xsl:when test="$share='True'">
		      <button type="button" class="btn btn-default" data-dismiss="modal">Fermer</button>
		    </xsl:when>
		    <xsl:otherwise>
		      <button type="button" class="btn btn-primary modal-topic-details-ok">Valider</button>
		      <button type="button" class="btn btn-default" data-dismiss="modal">Annuler</button>
		    </xsl:otherwise>
		  </xsl:choose>
		</div>
	      </div><!-- /.modal-content -->
	    </div><!-- /.modal-dialog -->
	  </div><!-- /.modal -->
	</xsl:copy>
      </div>
    </xsl:if>
  </xsl:template>


  


  <xsl:template name="topic-controls">
    <!--
	<span class="btn-group">
      <xsl:apply-templates  select="html:div[starts-with(@class,'kolekti-component-')]"
				   mode="topicpanelbutton"/>
	       
    </span>
    -->
    <span class="pull-right">
      <span class="btn-group hide-topicdetails">
	<xsl:if test="$share='False'">
	  <button title="A la une">
	    <xsl:attribute name="class">
	      <xsl:text>btn btn-xs btn-default  ecorse-action-star </xsl:text>
	      <xsl:choose>
		<xsl:when test="ancestor-or-self::html:div[@class='topic'][@data-star]">btn-warning</xsl:when>
		<xsl:otherwise>btn-default</xsl:otherwise>
	      </xsl:choose>
	    </xsl:attribute>
	    
	    
	    <i class="fa fa-star-o"></i>
	  </button>
	  
	  <button title="Supprimer">
	    <xsl:attribute name="class">
	      <xsl:text>btn btn-xs ecorse-action-hide </xsl:text>
	      <xsl:choose>
		<xsl:when test="@data-hidden = 'yes'">
		  <xsl:text>btn-primary ishidden</xsl:text>
		</xsl:when>
		<xsl:otherwise>
		  <xsl:text>btn-default</xsl:text>
		</xsl:otherwise>
	      </xsl:choose>
	    </xsl:attribute>
	    <i class="fa fa-trash-o"></i>
	  </button>
	</xsl:if>
	
	<button title="Détails" class="btn btn-xs btn-default  ecorse-action-showdetails">
	  <i class="fa fa-info"></i><xsl:text> Détails</xsl:text>
	</button>
	<!--
	    <xsl:apply-templates select="html:div[starts-with(@class,'kolekti-component-')]"
	    mode="topicpanelaction"/>
	-->
      </span>
    </span>
  </xsl:template>

<!--
  <xsl:template match="html:div[@class='kolekti-sparql-foreach-results']">
    <div class="collapse collapseDetails collapseTopic" id="collapseDetails{ancestor::html:div[@class='topic']/@id}" role="tabpanel">
      <div class="well">
	<table class="table">
	  <xsl:apply-templates/>
	</table>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template name="topic-analyse">
    <div class="collapse collapseAnalyse collapseTopic" id="collapseAnalyse{@id}"  role="tabpanel">
      <div class="well">
	<div id="editor{@id}" class="anaeditor" contenteditable="true">
	  <xsl:copy-of select="html:div[@class='analyse']"/>
	</div>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template name="topic-visuels">
    <div class="collapse collapsePictures collapseTopic" id="collapsePictures{@id}"  role="tabpanel">
      <div class="well">
	<xsl:copy-of select="div[@class='visuels']"/>
      </div>
    </div>
  </xsl:template>


  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']">
    <tr>
      <xsl:apply-templates mode="tpl"/>
    </tr>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']//html:span" mode="tpl">
    <td>
      <xsl:apply-templates/>
    </td>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']//html:span[@class='tplvalue']" mode="tpl">
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="html:p[@class='kolekti-sparql-result-chartjs']">
    <div class="kolekti-sparql-result-chartjs" data-chartjs-data='{.}' id="chart_{ancestor::html:div[@class='topic']/@id}">
      <xsl:copy-of select='@data-chartjs-kind'/>
      <div class="legend">
      </div>
    </div>
  </xsl:template>
-->
  
  <xsl:template match="html:img/@src">
    <xsl:attribute name="src">
      <xsl:value-of select="$path"/>
      <xsl:value-of select="."/>
    </xsl:attribute>
  </xsl:template>
      


  
  
</xsl:stylesheet>
