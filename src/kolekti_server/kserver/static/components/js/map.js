$(document).ready(function() {
    console.log('init map componenent');

    // display map on report main page for starred topics
    $('.alaune .leafletmap').each(function() {
	if (! $(this).find('div').length) {
	    var geojson = $(this).data('geojson').results.bindings[0].geojson.value	
	    var geodata = JSON.parse(geojson)
	    
	    var map = L.map($(this).get(0));
	    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
		maxZoom: 18,
		attribution: 'Map data ©<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
		    '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
		    'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		id: 'mapbox.streets'
	    }).addTo(map);
	    
	    var myLayer = L.geoJson(geodata);
	    myLayer.addTo(map) ;
	    map.fitBounds(myLayer.getBounds()) ;
	}
    });
    
    $("body").trigger( "elocus.graphics.displayed", [ "map" ] );
    
    // deroulement de la section (affichage des topics)
    $('.section-content.collapse').on('shown.bs.collapse', function(e) {
	if ($(e.target).hasClass('section-content')) {
	    $(e.target).find('.panel .leafletmap').each(function() {
		if (! $(this).find('div').length) {
		    if ($(this).data('geojson').results) {
			
			var geojson = $(this).data('geojson').results.bindings[0].geojson.value	
			var geodata = JSON.parse(geojson)
		    
			var map = L.map($(this).get(0));
			L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			    maxZoom: 18,
			    attribution: 'Map data ©<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
				'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
				'Imagery © <a href="http://mapbox.com">Mapbox</a>',
			    id: 'mapbox.streets'
			}).addTo(map);
		    
			var myLayer = L.geoJson(geodata);
			myLayer.addTo(map) ;
			map.fitBounds(myLayer.getBounds()) ;
			
		    }
		}
	    });
	}
	resize();
    })
    
    $('.modal-topic-details').on('shown.bs.modal', function(e) {
	console.log('show modal');
	$(e.target).find('.leafletmappanel').each(function() {
	    if (! $(this).find('div').length) {
		var geojson = $(this).data('geojson').results.bindings[0].geojson.value	
		var geodata = JSON.parse(geojson)
		
		var map = L.map($(this).get(0));
		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
		    maxZoom: 18,
		    attribution: 'Map data ©<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
			'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		    id: 'mapbox.streets'
		}).addTo(map);
		
		var myLayer = L.geoJson(geodata);
		myLayer.addTo(map) ;
		map.fitBounds(myLayer.getBounds()) ;
	    }
	    $(this).attr('style','width:100%; height:240px ; position:relative');

	})
    })
   
    var resize =  function() {
	$('.collapse.in').find('.leafletmap, .leafletmappanel').each(function(e,i) {

	    var wwidth = $(this).width();
	    var wheight = (wwidth / 2) + 3;
	    if (wheight > 400)
		wheight = 400;
	    $(this).attr('style','width:100%; height:'+ wheight +'px ; position:relative');
	});
	$("body").trigger( "elocus.graphics.displayed", [ "map" ] );
    };
    
    $(window).on('resize', resize);
		
})
