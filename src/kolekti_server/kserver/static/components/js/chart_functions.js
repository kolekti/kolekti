var locale_fr = {
    "decimal": ",",
    "thousands": " ",
    "grouping": [3],
    "currency": ["€", ""],
    "dateTime": "%a %b %e %X %Y",
    "date": "%d/%m/%Y",
    "time": "%H:%M:%S",
    "periods": ["AM", "PM"],
    "days": ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"],
    "shortDays": ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"],
    "months": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Decembre"],
    "shortMonths": ["Jan", "Fev", "Mar", "Avr", "Mai", "Jui", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"]
};



var drawchart = function(elt, anim, windowwidth) {
    var data = $(elt).data('chartdata')['results']['bindings'];
	//var series = [

    var fr = d3.locale(locale_fr);
    
    var by_year = d3.nest()
	    .key(function(d) { return d.year.value; })
	    .sortKeys(d3.ascending)
	    .entries(data);

	var by_place = d3.nest()
	    .key(function(d) { return d.placeURI.value; })
	    .sortValues(function(a,b) {
		return b.year.value < a.year.value ? -1 : b.year.value > a.year.value ? 1 : b.year.value >= a.year.value ? 0 :NaN
	    })
	    .entries(data);
	
	var places = by_place.map(function(item) {
	    return item.values[0].placeLabel.value;
	})

    var wwidth = windowwidth?windowwidth:$(elt).width();
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
	
	
    var seriescolor = d3.scale.ordinal()
	.range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);
    
    
    var colorscale = d3.scale.ordinal()
	.domain(by_place.map(function(d) {
	    return d.key;
	}))
	.rangeRoundBands([0, places.length]);
    
    var yAxis = d3.svg.axis()
	.scale(y)
	.orient("left")
	.ticks(10)
	.tickFormat(fr.numberFormat(",.0f"))
    ;
    
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
	.attr("y", 12)
	.style("text-anchor", "end")
	.text(data[0].valueLabel.value);

	
    var barchart = function() {
	var x0 = d3.scale.ordinal().rangeRoundBands([0, width], .05, .2);
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
	    .call(xAxis)
	    .selectAll("text")
	    .attr("dy", "8");
	
	    
	var year = chart.selectAll(".year")
	    .data(by_year)
	    .enter().append("g")
	    .attr("class", "year")
	    .attr("transform", function(d) {
		return "translate(" + x0(d.key) + ",0)";
	    })
	
	    
	    
	var rect = year.selectAll("rect")
	    .data(function(d) {
		return d.values.map(function(i) {
		    return {
			'name':i.placeLabel.value,
			'place':i.placeURI.value,
			'value':i.xapprox.value
		    };
		});
	    })
	    .enter().append("rect")
	    .style("fill", function(d) { return seriescolor(colorscale(d.place)); })
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
	    
	if (anim)
	    year.append("rect")
	    .attr('class','eventrect')
	    .attr('x', 0)
	    .attr('width', x0.rangeBand())
	    .attr('y', 0)
	    .attr('height', height )
	
	    .on("mouseover", function(d){
		var mouse = d3.mouse(this);
		
		tooltip(d.key, x0(d.key), mouse[1]);
		chart.select('.charttooltip').style("visibility", "visible");
	    })
	    .on("mousemove", function(d){
		var mouse = d3.mouse(this);
		tooltip(d.key, x0(d.key), mouse[1]);
	    })
	
	    .on("mouseout", function(){
		chart.select('.charttooltip').style("visibility", "hidden");
	    });
	

    } // barchart
	
    var linechart = function() {


	var x0 = d3.scale
	    .ordinal()
	    .domain(by_year.map(function(d) {
		return d.key;
	    }))
	    .rangeRoundPoints([0, width]);
	
	    
	var xAxis = d3.svg.axis()
	    .scale(x0)
	    .orient("bottom");
	
	
	chart.append("g")
	    .attr("class", "x axis")
	    .attr("transform", "translate(0," + height + ")")
	    .call(xAxis);
	
	
	var area = d3.svg.line()
	    .interpolate("linear")
	    .x(function(d) {
		return x0(d.year.value);
	    })
	//	    	.y(function(d) {return y(0)})
	    .y(function(d) {
		return y(d.xapprox.value);
	    });
	    
	var place = chart.selectAll(".place")
	    .data(by_place)
	    .enter()
	    .append("g")
	    .attr("class", "place");
	
	place.append("path")
	    .attr("class", "area")
	    .attr("d", function(d) {
		return area(d.values);
	    })
	    .style("stroke", function(d) {
		return seriescolor(colorscale(d.key));
	    })
	
	    .style("fill", function(d) { return seriescolor(d.name); })
	
	// dots
	place.selectAll(".dot")
	    .data(function(d){
		return d.values.map(function(i) {
		    return {'year':i.year.value,'place':i.placeURI.value, 'value':i.xapprox.value}
		})
	    })
	    .enter()
	    .append("circle")
	    .attr("class","dot")
	    .attr("r", 3.5)
	    .attr("cx", function(d) {
		return x0(d.year);
	    })
	    .attr("cy", function(d) { return y(d.value); })
	    .style("fill",function(d) {
		return seriescolor(colorscale(d.place));
	    })
	
	place.selectAll(".tipdot")
	    .data(function(d){
		return d.values.map(function(i) {
		    return {'year':i.year.value,'place':i.placeURI.value, 'value':i.xapprox.value}
		    })
	    })
	    .enter().append("circle")
	    .attr("class","tipdot eventrect")
	    .attr("r", 20)
	    .attr("cx", function(d) {
		return x0(d.year);
	    })
	    .attr("cy", function(d) { return y(d.value); })
	    .on("mouseover", function(d){
		var mouse = d3.mouse(this);
		tooltip(d.year, x0(d.year) - 40, mouse[1]);
		chart.select('.charttooltip').style("visibility", "visible");
	    })
	
	    .on("mouseout", function(){
		chart.select('.charttooltip').style("visibility", "hidden");
	    });
	
	
	
    } // linechart
    
    
    if ($(elt).attr("data-chartkind")=="bar")
	barchart();
    if ($(elt).attr("data-chartkind")=="line")
	linechart();
    
    // adds legend
	
    var legend = chart.selectAll(".legend")
	.data(by_place)
	.enter().append("g")
	.attr("class", "legend")
	.attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });
	
    legend.append("rect")
	.attr("x", 0)
	.attr("y", height + 22)
	.attr("width", 18)
	.attr("height", 18)
	.style("fill", function(d){return(seriescolor(colorscale(d.key)))});
    
    legend.append("text")
	.attr("x", 24)
	.attr("y", height + 22)
    //	.attr("dy", "1.2em")
    	.attr("dy", "14")
	.style("text-anchor", "start")
	.text(function(d) { return d.values[0].placeLabel.value; });

	// overlay for tooltips interactivity

    if (anim) {
	var tooltipelt = chart.append("g")
	    .attr("class", "charttooltip")
    
	tooltipelt.append('rect')
	    .attr("x",1)
	    .attr("y",0)
	    .attr("rx",3)
	    .attr("ry",3)
	    .attr("width",80)
	    .attr("class","tooltipbg")
	
	var tooltipyear;
	var tooltip = function(year, xpos, ypos) {
	    var values = by_year.filter(function(d) { return d.key == year})[0].values
	    tooltipelt.attr("transform", "translate(" + xpos + "," + (ypos - ((values.length + 1) * 20))  + ")")
	    
	    tooltipelt.select('.tooltipbg').attr("height",3+((values.length ) * 20) )
	    
	    
	    if (year == tooltipyear)
		return
	    tooltipyear = year;
	    var tipdata = values.map(function(d,i) { return {"key":d.placeURI.value, "value":d.xapprox.value}})
	    tooltipelt.selectAll('.tip').remove()
	    var tips = tooltipelt.selectAll('.tip')
		.data(tipdata)
	    
	    var tipline = tips.enter()
		.append('g')
		.attr("class","tip")
		.attr("transform", function(d, i) { return "translate(3," + (i-1) * 20 + ")"; });
	
		tipline.append("rect")
		.attr("x", 0)
		.attr("y", 22)
		.attr("width", 18)
		.attr("height", 18)
		.style("fill", function(d){return(seriescolor(colorscale(d.key)))})
	
		tipline.append("text")
		.attr("x", 24)
		.attr("y", 22)
		.attr("dy", "1.2em")
		.style("text-anchor", "start")
		.text(function(d) { return d.value; });
	}
	    
    }	
    
}; // drawchart
