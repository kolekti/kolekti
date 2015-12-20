$(document).ready(function() {
    

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
    var chartcolors = ['220,51,51', '51,51,220', '51,220,61'];
    
    var make_chart  = function(chartid, kind, data) {
	var chart = document.getElementById(chartid)
	var canvasid = 'canvas_' + chartid
	$(chart).find('canvas').remove()
	if (data != 'no data') {
	    $(chart).prepend($('<canvas>', {'id':canvasid}))
	
            for (s=0; s < data['seriescount']; s++) {
		data['datasets'][s]["highlightStroke"] = "rgba("+chartcolors[s]+",1)";
  		data['datasets'][s]["strokeColor"] = "rgba("+chartcolors[s]+",0.8)";
		if (kind == "Bar") {
		    data['datasets'][s]["highlightFill"] = "rgba("+chartcolors[s]+",0.75)";
 		    data['datasets'][s]["fillColor"] = "rgba("+chartcolors[s]+",0.5)";
		}
		if (kind == "Line") {
		    data['datasets'][s]["highlightFill"] = "rgba("+chartcolors[s]+",0.2)";
 		    data['datasets'][s]["fillColor"] = "rgba("+chartcolors[s]+",0.1)";
		}
	    }
            var ctx = document.getElementById(canvasid).getContext("2d");
	    var myNewChart = new Chart(ctx)[kind](data);
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
	    url:"/ecorse/report/publish",
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
	    url:"/ecorse/report/publish",
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
	    url:"/ecorse/report/publish",
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
	var release = $('.report').data('release')
	$.ajax({
	    url:"/ecorse/report/publish",
	    method:'POST',
	    data:$.param({
		'release': release,
		'script': 'web'
	    })
	}).done(function(data) {

	}).fail(function(data) {
	});
	
    })
    
})
		  
