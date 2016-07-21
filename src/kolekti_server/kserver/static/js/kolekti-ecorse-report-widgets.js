$(function() {
    // jQuery for page scrolling feature - requires jQuery Easing plugin
    $('a.page-scroll').bind('click', function(event) {
	var $anchor = $(this);
	$('html, body').stop().animate({
	    scrollTop: $($anchor.attr('href')).offset().top
	}, 1500, 'easeInOutExpo');
	event.preventDefault();
    });
    
    // fonctions pour harmoniser les hauteurs aprés un changement de taille d'écran
    var mapsReady = ($(".leafletmap").length == 0);
    var chartsReady = ($(".ecorse-chart").length == 0);
//    doResizeActions($('body'));

    equalizePanelHeadings($('.accueil.sections'));
    
    $('body').on("displayed.elocus.topics", function(e, component) { //evt déclarés dans chart.js et map.js
	if(component == 'map') mapsReady = true;
	if(component == 'chart') chartsReady = true;					
	//	doResizeActions(e.target);
//	console.log(e.target)
	equalizeTopics(e.target);						
	if(mapsReady && chartsReady) {
	    doOpenTopic();
	}
    });
    
    $( window ).resize(function() {
	equalizePanelHeadings($('.accueil.sections'));
    });
    
    
    //pour ouverture accordéon quand on suit un lien d'indicateur à la une
    var doOpenTopic = function() {
	var pageUrl = window.location.href;
	var hasEltIdInPageUrl = pageUrl.indexOf("#"); 
	if (hasEltIdInPageUrl != -1) {
	    if (!$('body').data('opened')) {
		var eltIdInPageUrl = '#' + pageUrl.split('#')[1];
//		console.log($(eltIdInPageUrl).closest(".section-content.collapse"));
		
		$(eltIdInPageUrl).parents().collapse('show');
		$(eltIdInPageUrl).closest(".section-content.collapse").trigger("shown.elocus.section");
		
		$('html, body').animate({
		    scrollTop: $(eltIdInPageUrl).offset().top - 60
		}, 1000);
	    }
	}
	$('body').data('opened',true);
    }    
});

function doResizeActions(elt) {
//    console.log ("doResizeActions (mapsReady:" + mapsReady + ", chartsReady:" + chartsReady + ")");
    
    if(mapsReady && chartsReady) {
	$('.accueil.sections').each(function(){
	    equalizePanelHeadings(this);						
	});
	$('.accueil.alaune .panel-body').each(function(){
	    equalizeTopics(this);						
	});
	$('.panel-collapse.in').each(function(){
	    equalizeTopics(this);						
	});
		
    }
}

function equalizePanelHeadings(elt) {
    var maxHeight = 0;
    var panelHeadings = $('.panel .panel-heading', elt);
    //on enlève la spécification assignée par un appel précédent à cette fonction
    $(panelHeadings).css('height', 'inherit');
    // Select and loop the elements you want to equalise
    $(panelHeadings).each(function(){
	if($(this).height() > maxHeight) {
	    maxHeight = $(this).height(); 
	}
    }); 
    // Set the height of all those children to whichever was highest 
    $(panelHeadings).height(maxHeight);
}

function equalizeTopics(elt) {
    var maxHeightHeadings = 0;
    var panelHeadings = $('.topic .panel .panel-heading', elt);
    //on enlève la spécification assignée par un appel précédent à cette fonction
    $(panelHeadings).css('height', 'inherit');
    // Select and loop the elements you want to equalise
    $(panelHeadings).each(function(){
//	console.log(this)
	if($(this).height() > maxHeightHeadings) {
	    maxHeightHeadings = $(this).height(); 
	}
    }); 
    // Set the height of all those children to whichever was highest 
    $(panelHeadings).height(maxHeightHeadings);
    
    var maxHeightBodys = 0;
    var panelBodys = $('.topic .panel .panel-body',elt);
    //on enlève la spécification assignée par un appel précédent à cette fonction
    $(panelBodys).css('height', 'inherit');
    // Select and loop the elements you want to equalise
    $(panelBodys).each(function(){
	if($(this).height() > maxHeightBodys) {
	    maxHeightBodys = $(this).height(); 
	}
    }); 
    // Set the height of all those children to whichever was highest 
    $(panelBodys).height(maxHeightBodys);
}
