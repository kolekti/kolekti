var mapsreg = {}
var register_map = function(map, id) {
    mapsreg[id] = map
}

var get_map = function(id) {
    return mapsreg[id]
}

$(document).ready(function() {

    if ($('.alaune .leafletmap').length) {
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
		map.fitBounds(myLayer.getBounds());
		register_map(map, $(this).attr('id'));
	    }
	});
        $(".alaune").trigger( "elocus.graphics.displayed", [ "map" ] );
    }
    
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
			register_map(map, $(this).attr('id'));
		    }
		}
	    });
	}
	resize();
    })
    
    $('.modal-topic-details').on('shown.bs.modal', function(e) {
	$(e.target).find('.leafletmappanel').each(function() {
	    $(this).attr('style','width:100%; height:400px ; position:relative');
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
		register_map(map, $(this).attr('id'));
	    }
	})
    })
   
    var resize =  function() {
	$('.collapse.in').find('.leafletmap, .leafletmappanel').each(function(e,i) {

	    var wwidth = $(this).width();
	    var wheight = (wwidth / 2) + 3;
	    if (wheight > 400)
		wheight = 400;
	    $(this).attr('style','width:100%; height:'+ wheight +'px ; position:relative');
	    var map = get_map($(this).attr('id'));
	    map.invalidateSize();
	});
	
	$(".collapse.in").trigger( "elocus.graphics.displayed", [ "map" ] );

    };
    
    $(window).on('resize', resize);
    $(window).on('redraw.elocus.topics', function(){
	$('.collapse.in').find('.leafletmap, .leafletmappanel').each(function(e,i) {
	    var map = get_map($(this).attr('id'));
	    map.invalidateSize();
	});
    });


    
})
