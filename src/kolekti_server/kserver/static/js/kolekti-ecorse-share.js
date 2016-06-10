$(document).ready(function() {
    
    var chartoptions = function(kind, yunit) {

	var cb = function (tickValue, index, ticks) {
	    //return "Foof"
	    var delta = ticks[1] - ticks[0];
	    
	    // If we have a number like 2.5 as the delta, figure out how many decimal places we need
	    if (Math.abs(delta) > 1) {
		if (tickValue !== Math.floor(tickValue)) {
		    // not an integer
		    delta = tickValue - Math.floor(tickValue);
		}
	    }
	    
	    var logDelta = Chart.helpers.log10(Math.abs(delta));
	    var tickString = '';
	    
	    if (tickValue !== 0) {
		var numDecimal = -1 * Math.floor(logDelta);
		numDecimal = Math.max(Math.min(numDecimal, 20), 0); // toFixed has a max of 20 decimal places
		tickString = tickValue.toFixed(numDecimal);
		if (yunit == "€"  || yunit == "%") {
		    tickString = tickString + " " + yunit;
		}
	    } else {
		tickString = '0'; // never show decimal places for 0
	    }

	    return tickString;
	    
	}
	
	var _chartoptions = {
	    'Line':{
		'scales':{'yAxes':[{
		    'ticks':{
			
			'userCallback': cb
		    }
		}]}
	    },
	    'Bar':{
		'scales':{'yAxes':[{
		    'ticks':{
			'suggestedMin':0,
			'userCallback': cb
		    }
		}]}
	    }
	};

	if (yunit != "%" && yunit != "€") {
	    _chartoptions[kind].scales['yAxes'][0].scaleLabel={
		"display":true,
		"labelString": yunit
	    }
	}
	
	return _chartoptions[kind];
    }


    // collapse : close open collapse when an otherone is open
    $(".collapseTopic").on('show.bs.collapse', function() {
	var current = $(this).attr('class')
	$(this).closest('.topicCollapses').find('.collapseTopic').removeClass('in')
   })

    //collapse : highlight button
    $(".ecorse-action-collapse").on('click', function() {
	$(this).closest('.topicCollapses').find('.ecorse-action-collapse').removeClass('active')
	$(this).addClass('active')
    })
    
    
    // affichage diagrammes
    Chart.defaults.global.responsive = true;

    Chart.defaults.global.legend.position = 'bottom';
    var chartcolors = ['220,51,51', '51,51,220', '51,220,61'];

    var make_chart  = function(chartid, kind, data) {
	var chart = document.getElementById(chartid)
	var canvasid = 'canvas_' + chartid
	chart.Chart && chart.Chart.destroy()
	//$(chart).find('canvas').remove()
	
	if (data != 'no data') {
	    if($(chart).find('canvas').length == 0)
		$(chart).prepend($('<canvas>', {'id':canvasid}))
	
            for (s=0; s < data['seriescount']; s++) {
		data['datasets'][s]["borderColor"] = "rgba("+chartcolors[s]+",1)";
		if (kind == "Bar") {
		    data['datasets'][s]["backgroundColor"] = "rgba("+chartcolors[s]+",0.75)";
		}
		if (kind == "Line") {
		    data['datasets'][s]["backgroundColor"] = "rgba("+chartcolors[s]+",0.2)";
		}
	    }
            var ctx = document.getElementById(canvasid).getContext("2d");

	    //	    var myNewChart = new Chart(ctx)[kind](data, chartoptions[kind]);
	    chart.Chart = new Chart(ctx, {
		type: kind.toLowerCase(),
		data:data,
		options:chartoptions(kind, data['unit'])});
	}
    }


    $('.section-content.collapse').on('shown.bs.collapse', function(e) {
	if ($(e.target).hasClass('section-content'))
	    $(this).find('.kolekti-sparql-result-chartjs').each(function() {
		var data = $(this).data('chartjs-data')
		var kind = $(this).closest('.topic').data('chart-kind')
		var parent   = $(this).attr('id')
		make_chart(parent, kind, data);
	    });
    })
    
    $('.kolekti-sparql-result-chartjs').each(function() {
	var data = $(this).data('chartjs-data')
	if (data == "no data") {
	    $(this).find('.legend').append($('<p class="error">Aucune donnée pour cet indicateur</p>'))
	}else{
	    return;
	    $(this).find('.legend').append(
	    
	    $.map(data.datasets, function(s,i) {
		return $('<p>', {
			'class':'legendtiem',
		    'html':[
			$('<span>', {
			    'class':"legendcolor",
			    'html':$('<i>',{
				'class':"fa fa-square",
				'style':'color:rgba('+chartcolors[i]+',1)'
				
			    })
			}),
			$('<span>', {
			    'class':"legendtext",
			    'html':s.label
			})
		    ]
		} )
	    })
	    )
	}
    });

    // actions
    

    // Téléchargement (publication kolekti)
    $('.ecorse-action-dl-pdf').on('click', function() {
	var release = $('.report').data('release')
	$.ajax({
	    url:"/elocus/report/publish",
	    method:'POST',
	    data:$.param({
		'release': release,
		'script': 'pdf'
	    })
	}).done(function(data) {
	}).fail(function(data) {
	});
	
    })
    $('.ecorse-action-dl-word').on('click', function() {
	var release = $('.report').data('release')
	$.ajax({
	    url:"/elocus/report/publish",
	    method:'POST',
	    data:$.param({
		'release': release,
		'script': 'odt'
	    })
	}).done(function(data) {
	    console.log(data)
	    $.each(data, function(i,v) {
		console.log(v)
		if (v.event == 'result')
		    window.location.replace(window.location.origin + v.docs[0].url)
	    })
	}).fail(function(data) {
	});
	
    })
    $('.ecorse-action-dl-presentation').on('click', function() {
	var release = $('.report').data('release')
	$.ajax({
	    url:"/elocus/report/publish",
	    method:'POST',
	    data:$.param({
		'release': release,
		'script': 'ppt'
	    })
	}).done(function(data) {
	}).fail(function(data) {
	});
	
    })
    $('.ecorse-action-dl-html').on('click', function() {
	$("#modal_share").modal("show")
    })
    
})
		  
