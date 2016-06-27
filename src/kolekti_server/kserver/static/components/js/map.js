$(document).ready(function() {
    console.log('init map componenent');

    $('.section-content.collapse').on('shown.bs.collapse', function(e) {
	if ($(e.target).hasClass('section-content')) {
	    $(e.target).find('.leafletmap').each(function() {
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
	}
	resize();
    })

    var resize =  function() {
	$('.collapse.in').find('.leafletmap').each(function(e,i) {

	    var wwidth = $(this).width();
	    var wheight = (wwidth / 2) + 3;
	    if (wheight > 400)
		wheight = 400;
	    console.log ('map wh   '+ wwidth + 'x' +wheight)
	    $(this).attr('style','width:100%; height:'+ wheight +'px ; position:relative');
	});
    };
    
    $(window).on('resize', resize);
		
})
