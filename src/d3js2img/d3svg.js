var d3 = require('d3');
var jsdom = require('jsdom');

var kolekti_srcurl = 'http://localhost:8082/static/';
var chartWidth = 500, chartHeight = 500;

var stdin = process.stdin,
    stdout = process.stdout,
    inputChunks = "";
stdin.resume();
stdin.setEncoding('utf8');

stdin.on('data', function (chunk) {
    inputChunks += chunk;
});

stdin.on('end', function () {
    jsdom.env({
	html:inputChunks,
	scripts:[
	    //	    "jquery-1.5.min.js",
	    kolekti_srcurl + 'jquery.js',
	    kolekti_srcurl + 'd3.min.js',
//	    kolekti_srcurl + 'map.js',
	    kolekti_srcurl + 'components/js/chart_functions.js',
	],
	features:{ QuerySelector:true }, //you need query selector for D3 to work
	done:function(errors, window){
	    var svg = d3.select(window.document.body).select('div')
	    var svglist = window.document.getElementsByTagName('div')
	    
	    window.drawchart(svglist[0], false, 725);
	    stdout.write(svg.html())
	}
    });
});

