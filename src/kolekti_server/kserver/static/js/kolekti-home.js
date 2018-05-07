$(document).ready(function() {
    var list_main=[];
    var list_side=[];
    var widgets = [];
    // global variable for time range in graph
    var timegraph = {
	period : "month",
    }
	
    var widget = function(wdef, wname, wcol) {
	wwidth = 4* (wdef.width || 1)
	var w = $('<div>', {
	    "class":"col-lg-" + wwidth,
	    "data-widget":wname,
	    "html":$('<div>', {
		"class":"panel panel-default",
		"html":[
		    $('<div>', {
			"class":"panel-heading",
			"html":wdef.title
		    }),
		    $('<div>', {
			"class":"panel-body",
		    })
		]
	    })
	})
	$('#widgets_main').append(w);
	w.find('div.panel-body').html(wdef.content())
	
//	$('#col_'+wcol).append(w);
	wdef.render && wdef.render(w)
	return w
    }

    var widget_loader = function(url, wdiv) {
	var wdiv = $('<div>', {
	    "class":"widget",
	    "html":	$('<span>',{
		'class':'spinner',
		'html':[
		    $('<i>', {
			'class':'fa fa-spin fa-spinner'
		    }),
		    ' Chargement...']
		
	    })

	});
	$.get(url, function(data) {
	    wdiv.html(data)
	})
	return wdiv;
    }

    var graph_widget_loader = function() {
	wdiv  = $('<div>', {
	    "class":"widget",
	    "html":[
		$('<div>', {
		    "class":"col-md-8",
		    "id":"mychart"
		}),
		$('<div>', {
		    "class":"col-md-4 history",
		    "id":"mychartdetails"
		})
	    ]
	});
	return wdiv;
    }


    
	/* Now we can specify multiple responsive settings that will override the base settings based on order and if the media queries match. In this example we are changing the visibility of dots and lines as well as use different label interpolations for space reasons. */
    var graph_widget_render = function(w, url) {


	// Parse the date / time
	var fmtDate = d3.time.format("%Y-%m-%d");
	
	var compute_timegraph = function() {
	    timegraph.end = d3.time.week.offset(d3.time.week(new Date()), 1);
	    timegraph.start = d3.time.month.offset(timegraph.end, -2);
	}
	
	var render_timegraph = function() {
	    var wwidth = $(w).width()
	    if ($('body').width() > 980)
		wwidth = wwidth/ 3 * 2;
	    var wheight = wwidth / 2;
	    if (wheight > 400)
		wheight = 400;
	    
	    var margin = {top: 20, right: 40, bottom: 150, left: 20},
		width = wwidth - margin.left - margin.right,
		height = wheight - margin.top - margin.bottom;
	    
	    var barWidth = (width / 60) -2;

	    $('#mychartdetails').css('max-height', wheight)
	    var div = d3.select("#mychart")
		.append("div")  // declare the tooltip div
		.attr("class", "tooltip")              // apply the 'tooltip' class
		.style("opacity", 0);
            
	    
	    var svg = d3.select("#mychart").append('svg')
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform",
		      "translate(" + margin.left + "," + margin.top + ")");

	    var x = d3.time.scale()
		.rangeRound([0, width - margin.left - margin.right]);
	    
	    var y = d3.scale.linear().range([height, 0]);

	    // set range of time
	    
	    x.domain([timegraph.start, timegraph.end])

	    y.domain([0, d3.max(timegraph.commitsByDay, function(d) { return d.values; })]);
	    
	    var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom")
		.ticks(d3.time.mondays, 1)
		.tickFormat(d3.time.format("%e %b"))
	    
	    
	    svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis)
		.selectAll("text")
		.style("text-anchor", "end")
	    	.style("font-size", "80%")
		.attr("dx", ".5em")
		.attr("dy", "1em")
		.attr("transform", "rotate(-30)");

	    var area = d3.svg.area()
	        .x(function(d) {
		    return x(fmtDate.parse(d.key));
		})
	        .y0(height)
	        .y1(function(d) {
		    return y(d.values);
		});

	    
	    
	    svg.append("path")
	        .datum(timegraph.commitsByDay)
	        .attr("class", "area")
	        .attr("d", area)
/*	    return
	    svg.selectAll("bar")
		.data(timegraph.commitsByDay)
	    	.enter()
		.append("rect")
	       	.filter(function(d) {return x(fmtDate.parse(d.key))>=0})
		.attr("class", "value")
		.attr("x", function(d) { return x(fmtDate.parse(d.key)); })
		.attr("width", barWidth)
		.attr("y", function(d) { return y(d.values); })
		.attr("height", function(d) { return height - y(d.values); })
		.attr('title',function(d) {return d3.time.format("%e %b %Y")(fmtDate.parse(d.key))} )
*/
	    var currentDay, selectedDay;
	    
	    svg.append("rect")
		.attr('class','eventrect')
		.attr('x', 0)
	    	.attr('width', width)
		.attr('y', 0)
		.attr('height', height )
		.on('mousemove', function(){
		    var mouse = d3.mouse(this);
		    var mouseDay = d3.time.day(x.invert(mouse[0]));
		    dMouseDay = fmtDate(mouseDay)
		    if (dMouseDay != currentDay) {
			var commits = timegraph.data.filter(function(d) {
			    return (fmtDate(new Date(d.date * 1000)) == dMouseDay)?this:null})
			if(commits.length) {
			    selectedDay = dMouseDay;
			    valueline
				.attr('x1', x(mouseDay))
				.attr('x2', x(mouseDay))
			}
		    }
		    currentDay = dMouseDay;
		})
		// .on("mouseover", function(d) {
		//     var mouse = d3.mouse(this);
		//     var mouseDate = x.invert(mouse[0]);
		    
		//     div.transition()
		// 	.duration(500)
		// 	.style("opacity", 0);
		//     div.transition()
		// 	.duration(200)
		// 	.style("opacity", .9);
		//     div.html(
		// 	'<span>' +
		// 	    fmtDate(mouseDate) +
		// 	    "</span>")
		// 	.style("left", (d3.event.pageX) + "px")
		// 	.style("top", (d3.event.pageY - 28) + "px");
	    // })
	    
		.on('mousedown', function(){
		    $('#mychartdetails').html('')
		    var div = d3.select('#mychartdetails').selectAll('div')
			.data(timegraph.data.filter(function(d) {
			    return (fmtDate(new Date(d.date * 1000)) == selectedDay)?this:null}))
			.enter()
			.append('div')
		    	.attr('class','record')
		    var pinfo = div.append('p')
			.attr('class','commitinfo')
		    pinfo.append('span')
		    	.attr('class', 'rev label label-info')
			.text(function(d) { return d.rev });
		    pinfo.append('span')
			.attr('class','date')
			.text(function(d) {return d3.time.format('%d/%m/%Y %H:%M')(new Date(d.date * 1000))});
		    pinfo.append('span')
		    	.attr('class','author pull-right')
		    	.text(function(d) {return d.user});
		    div.append('p')
			.attr('class', 'msg')
			.text(function(d) {return d.message});
		    div.append('p')
			.attr('class', 'link')
			.append('a')
			.attr('href', function(d) { return '/sync/revision/'+d.rev+'/'})
			.text('details')
		    
		})
	    
	    var valueline = svg.append('line')
		.attr('class', "valueline")
		.attr('x1', 0)
	    	.attr('x2', 0)
		.attr('y1', 0)
		.attr('y2', height)
	};

	$(window).on('resize', function() {
	    $("#mychart").html('')
	    render_timegraph()
	}) 
	
    	d3.json(url, function(error, data) {
	    timegraph.data = data
	    var commitsByDay = d3.nest()
		.key(function(d) { return fmtDate(d3.time.day(new Date(d.date * 1000))); })
		.rollup(function(v) { return v.length })
		.entries(data);
	    timegraph.commitsByDay = commitsByDay
	    compute_timegraph()
	    render_timegraph()
	});

    };



    var localstorage_widget_builder = function(name) {
	var wdiv = $('<div>', {
	    "class":"widget",
	});
	if (localStorage) {
	    var storedref = JSON.parse(localStorage.getItem(name));
	    if (storedref == null)
		storedref = []
	    var seen = []
	    $.each(storedref, function(i,filepath) {
		if (seen.indexOf(filepath.url)<0) {
		    seen.push(filepath.url);
		    wdiv.append($('<div>', {
			"class":"widget-group-item record",
			"html":[
			    $('<p>',{
			    'html':[
				$('<span>',{
				    'class':"rev label label-info",
				    'html':filepath.info
				}),
				$('<span>',{
				    'class':"info",
				    'html': $('<a>',{'href':filepath.url,
						     'html':filepath.name})
				}),
				$('<span>',{
				    'class':'author pull-right',
				    'html':formatTime(filepath.time)
				    
				})
			    ]
			    })
			    
			]}))
		}
		
	    });
	};
	return wdiv;
    };

    
    var publication_widget_builder = function(url) {
	var wdiv = $('<ul>', {
	    "class":"list-group panel-body ",
	});
	$.getJSON(url, function(data) {
	    $.each(data.publications, function( i, pub ) {
		wdiv.append($('<li>', {
		    "class":"list-group-item",
		    "html":[
			$('<h4>',{'html':pub.path}),
			$('<p>',{html:formatTime(pub.time)}),
			$('<div>',{
			    html:
			    $.map(pub.content, function(ev, iev) {
				if (ev.event == "error")
				    return $('<div>', {
					"class" : "panel panel-alert",
					"html": ev.msg
				    });
				if (ev.event == "lang") 
				    return $('<h4>', {
					"html":$('<em>',{
					    "html":ev.label
					})
				    });
				if (ev.event == "toc" && pub.event == "publication") 
				    return $('<p>', {"html": "Trame : " + ev.file});
				if (ev.event == "job" && pub.event == "publication") 
				    return $('<p>', {"html": "Parametres : " + ev.label});
				if (ev.event == "profile" && pub.event == "publication")
				    return $('<h5>', {"html": "Profil " + ev.label});
				if (ev.event == "result") 
				    return $('<ul>', {
					"html":$.map(ev.docs, function(doc) {
					    return $('<li>', {
						'html': [$('<span>', {"class" : "padright",
								      'html':doc.type + ' :'}),
							 $('<a>', {
							     'href': doc.url,
							     'target':"_blank",
							     'html': doc.label
							 })
							]
					    })
					})
				    })
			    })
			})
		    ]
		}));
	    });
	})
	return wdiv;
    }
    



    var widgets_definitions = {
        'search': { 'title':'Recherche',
                    'content':function() {
                        return widget_loader('/widgets/search/')
                    }
                  },
        'publish_archive': { 'title':'Publier une version archivée',
                    'content':function() {
                        return widget_loader('/widgets/publish_archive/')
                    }
                  },
	'recent':{'title':'Vos modifications',
		  'content':function() {
			 return localstorage_widget_builder('kolekti-recent-'+window.kolekti.project);
			}
		    },
	'history':{'title':'Historique du projet',
			   'content':function() {
			       return widget_loader('/widgets/project-history/')
			   }
			 },
	'_history':{'title':'Dernières modifications',
		   'content':function() {
		       return widget_loader('kolekti-history');
		   }
		  },
	'publications':{'title':'Dernières publications',
			'content':function() {
			    return widget_loader('/widgets/publications/');
			}
		       },
	'_releases':{'title':'Dernières versions',
		    'content':function() {
			return publication_widget_builder('/releases/publications/list.json')
		    }
		   },
	'releases':{'title':'Dernières versions',
		    'content':function() {
			return widget_loader('/widgets/releasepublications/')
		    }
		   },
	'activity':{'title':'Activité du projet',
			       'width':2,
 			       'content':function() {
				   return graph_widget_loader('/project/history/')
			       },
 			       'render':function(w) {
				   return graph_widget_render(w,'/project/history/')
			       }
			  }
    }

    var store_widgets = function() {
	if (localStorage) {
	    var sto_widgets = []
	    $('#col1').each(function(){
		var col = []
		$(this).find('>div').each(function() {
		    col.push($(this).attr('data-widget'))
		});
	    });
	    localStorage.setItem("widgets_main", sto_widgets);
	}
    }
    
    if (localStorage) {
	var sto_widgets = localStorage.getItem("widgets_main")
	if (sto_widgets == null)
	    sto_widgets = [['recent','history','publications'],['activity', 'releases', 'search']];

	    sto_widgets = [['recent','history','publications'], ['publish_archive']];

	$.each(sto_widgets, function(i,wlist) {
	    $.each(wlist, function(j, wn) {
		widget(widgets_definitions[wn],wn,i+1)
	    });
	});
	store_widgets()
	
    }
})



	    
