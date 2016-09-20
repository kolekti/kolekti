	var grades = [
		{val:1,       label:'10<sup>1</sup>',  color:'rgb(255,0,0)'},
		{val:0.1,     label:'10<sup>-1</sup>', color:'rgb(255,255,0)'},
		{val:0.01,    label:'10<sup>-2</sup>', color:'rgb(0,255,0)'},
		{val:0.001,   label:'10<sup>-3</sup>', color:'rgb(0,255,255)'},
		{val:0.00001, label:'10<sup>-5</sup>', color:'rgb(0,0,255)'}
	];
	
	var options1 = {
		gridSize: 1,
		circleRadius: 30,
		grades: grades,
		fillOpacity: 0.8
	};

	var mapDisplay = new MapDisplay('map');
	var map = mapDisplay.map;
	var animatedLayer = new AnimatedLayer(options1);
	var navigationBar = new NavigationBar(animatedLayer);
	
	mapDisplay.addLegend(options1);
	//mapDisplay.addTitle("Title", "Subtitle");		

	var setData = function(data, options) {
		navigationBar.config(data.length);
		animatedLayer.setOptions(options);
		animatedLayer.setData(data);
	};
	
	setData(sampleData1.data, options1);