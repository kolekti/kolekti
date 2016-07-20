$(document).ready(function() {
    console.log('init map componenent');

    // display map on report main page for starred topics
    $('.alaune .leafletanimatedheatmap').each(function() {
	if (! $(this).find('div').length) {
	    var geojson = $(this).data('geojson').results.bindings	
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
    
    $("body").trigger( "elocus.graphics.displayed", [ "animated-heatmap" ] );

    var convertdate = function(date) {
	var dt = date.split('_');
	var dcomps = dt[0].split('-');
	var tcomps = dt[1].split(':');
	var d = new Date(parseInt(dcomps[0]),
			 parseInt(dcomps[1]) - 1,
			 parseInt(dcomps[2]),
			 parseInt(tcomps[0]),
			 parseInt(tcomps[1]));
	return d.valueOf()/1000;
    }
    
    // deroulement de la section (affichage des topics)
    $('.section-content.collapse').on('shown.bs.collapse', function(e) {
	if ($(e.target).hasClass('section-content')) {
	    $(e.target).find('.panel .leafletanimatedheatmap').each(function() {
		if (! $(this).find('div').length) {
		    if ($(this).data('geojson').results) {
			var datastr = [];
			var qjson = $(this).data('geojson').results.bindings;	
			$.each(qjson, function(i,item) {
			    var date = item.date.value;
			    var valpoints = []
			    var itemdata = item.list.value.split('###');
			    $.each(itemdata, function(ii,subitem) {
				var subitemdata = JSON.parse(subitem);
				var locpoint = subitemdata.geometry.coordinates[0];
				var freq = subitemdata.properties.stat;
				valpoints.push({
				    "lat":parseFloat(locpoint[1]),
				    "lon":parseFloat(locpoint[0]),
				    "val":parseInt(freq)
				})
			    });
			    datastr.push({'date':convertdate(date),
					  'points':valpoints
					 });
			});
			console.log(JSON.stringify(datastr));
			var grades = [
			    {val:100,       label:'100',  color:'rgb(255,0,0)'},
			    {val:50,     label:'50', color:'rgb(255,255,0)'},
			    {val:20,    label:'20', color:'rgb(0,255,0)'},
			    {val:10,   label:'10', color:'rgb(0,255,255)'},
			    {val:5, label:'5', color:'rgb(0,0,255)'}
			];

			var options1 = {
			    gridSize: 1,
			    circleRadius: 0.2,
			    grades: grades,
			    fillOpacity: 0.8
			};
		
			var mapDisplay = new MapDisplay($(this).attr('id'));
			var map = mapDisplay.map;
			var animatedLayer = new AnimatedLayer(options1, map);
			var navigationBar = new NavigationBar(animatedLayer);
			animatedLayer.setNavigationBar(navigationBar);
			
			mapDisplay.addLegend(options1);
			//mapDisplay.addTitle("Title", "Subtitle");

			var setData = function(data, options) {
			    navigationBar.config(data.length);
			    animatedLayer.setOptions(options);
			    animatedLayer.setData(data);
			};

			setData(datastr, options1);
			
			return;
			       
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
	$(e.target).find('.leafletanimatedheatmappanel').each(function() {
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
	$('.collapse.in').find('.leafletanimatedheatmap, .leafletanimatedheatmappanel').each(function(e,i) {

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
