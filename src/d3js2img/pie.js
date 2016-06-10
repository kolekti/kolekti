var d3 = require('d3');
var jsdom = require('jsdom');

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
	html:inputChuncks,
	features:{ QuerySelector:true }, //you need query selector for D3 to work
	done:function(errors, window){
	    stdout.write(window.d3.select('.container').html())
	}
    });
}

