var drawmap = function(root, cb) {
    console.log(root);
    if ($(root).data('geojson').results) {

	
	var geojson = $(root).data('geojson').results.bindings[0].geojson.value	
	var geodata = JSON.parse(geojson)
	var map = L.map($(root).get(0))
	    .setView([42.444508, -76.499491], 12);
	console.log(map);
	map.invalidateSize();
	var tiles = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    
	    maxZoom: 18,
	    attribution: 'Map data ©<a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
		'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
		'Imagery © <a href="http://mapbox.com">Mapbox</a>',
	    id: 'mapbox.streets'
	});
	
	console.log(tiles.on);
	
	tiles.on("load", function() {
	    console.log('tiles loaded')
	    cb();
	})

	tiles.addTo(map);
	
	var myLayer = L.geoJson(geodata);
	myLayer.addTo(map) ;
	var bounds = myLayer.getBounds();
	console.log('got bounds')
	console.log(bounds)
	map.fitBounds(bounds, { padding: [20, 20] });
/*	myLayer.on("load", function() {
	    cb();
	})
*/
	console.log('drawmap done');
	
	window.setTimeout(function () {
            cb();
        }, 2000);
//    cb();
    }

}
