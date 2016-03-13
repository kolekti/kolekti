$(document).ready(function() {

    $('.section-content.collapse').on('hidden.bs.collapse', function(e) {
	if ($(e.target).hasClass('section-content')) {
	    $(e.target).find('.ecorse-chart').each(function() {
		$(this).html('');
	    });
	}
    });
    
    $('.section-content.collapse').on('shown.bs.collapse', function(e) {
	if ($(e.target).hasClass('section-content')) {
	    $(e.target).find('.ecorse-chart').each(function() {
		drawchart(this, true)
	    });
	}
    });
    
    var drawchart = function(elt, anim) {
	var data = $(elt).data('chartdata').results.bindings;
	//var series = [
	
	var by_year = d3.nest()
	    .key(function(d) { return d.year.value; })
	    .sortKeys(d3.ascending)
	    .entries(data);

	var by_place = d3.nest()
	    .key(function(d) { return d.placeURI.value; })
	    .entries(data);
	
	var places = by_place.map(function(item) {
	    return item.values[0].placeLabel.value;
	})

	var wwidth = $(elt).width()
	/*
	if ($('body').width() > 980)
	    wwidth = wwidth/ 3 * 2;
*/
	var wheight = wwidth / 2;
	if (wheight > 400)
	    wheight = 400;
	
	
	var margin = {top: 20, right: 20, bottom: 30+(20*places.length), left: 60},
	    width = wwidth - margin.left - margin.right,
	    height = wheight - margin.top - margin.bottom;
	
	// Parse the date / time
	varparseDate = d3.time.format("%Y-%m").parse;
	
	var y = d3.scale.linear().range([height, 0]);
	var datadomains = data.slice(0)
	datadomains.push({"xapprox":{"value":0}})
	
	y.domain([
	    d3.min(datadomains, function(d) {
		return parseFloat(d.xapprox.value);
	    }),
	    d3.max(datadomains, function(d) {
		return parseFloat(d.xapprox.value);
	    })
	]);
	
	
	var color = d3.scale.ordinal()
	    .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);
	
	
	var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left")
	    .ticks(10);
	
	var chart = d3.select(elt).append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	    .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	chart.append('line')
	    .attr("class", "zeroaxis")
	    .attr("x1", 0)
	    .attr("x2", width)
	    .attr("y1", function() {return y(0)})
	    .attr("y2", function() {return y(0)})
	
	chart.append("g")
	    .attr("class", "y axis")
	    .call(yAxis)
	    .append("text")
	    .attr("transform", "rotate(-90)")
		    .attr("y", 6)
	    .attr("dy", ".71em")
	    .style("text-anchor", "end")
	    .text(data[0].valueLabel.value);
	

	var barchart = function() {
	    var x0 = d3.scale.ordinal().rangeRoundBands([0, width], .05);
	    var x1 = d3.scale.ordinal()
	    x0.domain(by_year.map(function(d) {
		return d.key;
	    }));
	    
	    x1.domain(places).rangeRoundBands([0, x0.rangeBand()]);
	    
	    var xAxis = d3.svg.axis()
		.scale(x0)
		.orient("bottom")
	    
	    chart.append("g")
		.attr("class", "x axis hiddenaxis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);
	    
	    
	    var year = chart.selectAll(".year")
		.data(by_year)
		.enter().append("g")
		.attr("class", "year")
		.attr("transform", function(d) {
		    return "translate(" + x0(d.key) + ",0)";
		});
	    
	    
	    
	    var rect = year.selectAll("rect")
		.data(function(d) {
		    return d.values.map(function(i) {
			return {
			    'name':i.placeLabel.value,
			    'value':i.xapprox.value
			};
		    });
		})
		.enter().append("rect")
		.style("fill", function(d) { return color(d.name); })
		.attr("width", x1.rangeBand())
		.attr("x", function(d) {
		    return x1(d.name);
		})

	    if (anim)
		rect.attr("y", function(d) {return y(0)})
		.attr("height", function(d) { return 0})
		.transition()
		.duration(500)
		.attr("y", function(d) {
		    return d3.min([y(d.value),y(0)]);
		})		
		.attr("height", function(d) { return Math.abs(y(0) - y(d.value)); });
	    else
		rect.attr("y", function(d) {
		    return d3.min([y(d.value),y(0)]);
		})		
		.attr("height", function(d) { return Math.abs(y(0) - y(d.value)); });
	}
	
	var linechart = function() {
	    var x = d3.scale.ordinal()
		.range([0, width]);
	    
	    x.domain(by_year.map(function(d) {
		return d.key;
	    }));
	    
	    var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");
	    
	    chart.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);
	    
	    var line = d3.svg.line()
		.interpolate("basis")
		.x(function(d) {
		    return x(d.year.value);
		})
		.y(function(d) {
		    return y(d.xapprox.value);
		});
	    
	    var place = chart.selectAll(".place")
		.data(by_place)
		.enter().append("g")
		.attr("class", "place");
	    
	    place.append("path")
		.attr("class", "line")
		.attr("d", function(d) {
		    return line(d.values);
		})
		.style("stroke", function(d) { return color(d.name); });
	    
	}

	if ($(elt).attr("data-chartkind")=="bar")
	    barchart();
	if ($(elt).attr("data-chartkind")=="line")
	    linechart();
	
	var legend = chart.selectAll(".legend")
	    .data(places.slice())
	    .enter().append("g")
	    .attr("class", "legend")
	    .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });
	
	legend.append("rect")
	    .attr("x", 0)
	    .attr("y", height + 22)
	    .attr("width", 18)
	    .attr("height", 18)
	    .style("fill", color);
	
	legend.append("text")
	    .attr("x", 24)
	    .attr("y", height + 22)
	    .attr("dy", "1.2em")
	    .style("text-anchor", "start")
	    .text(function(d) { return d; });
    };


    $(window).on('resize', function() {
	$('.collapse.in').find('.ecorse-chart').each(function() {
	    $(this).html('')
	    drawchart(this, false)
	});

    })
    

    
    // menu selection graphique
    $('.ecorse-action-chart').on('click', function(e) {
	e.preventDefault()
	if(!$(this).find('i').length) {
	    var btn = $(this)
	    var chartkind = $(this).attr('data-chartkind')
	    var topic = $(this).closest('.topic')
	    var chart = topic.find('.ecorse-chart')
	    var release = $('.report').data('release')
	    
	    $.ajax({
		url:"/ecorse/report/chart",
		method:'POST',
		data:$.param({
		    'release': release,
		    'topic': topic.attr('id'),
		    'chartkind': chartkind
	    })
	    }).done(function(data) {
		
		if (data.status == 'ok') {
		    btn.closest('ul').find('i').remove();
		    btn.append($('<i>', { 'class':'fa fa-check'}));
		    chart.attr('data-chartkind',chartkind)
		    chart.html('')
		    drawchart(chart.get(0), true);
		}
	    }).fail(function(data) {
	    });
	    
	}
    })

})
