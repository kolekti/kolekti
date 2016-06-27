var ajaxBeforeSend = function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
} ;

$.ajaxSetup({ 
    beforeSend: ajaxBeforeSend
});

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
/*
		if (yunit == "%") {
		    tv = 100 * tickValue;
		    tickString = tv.toFixed(0) + " %";
		} else {
*/
		    var numDecimal = -1 * Math.floor(logDelta);
		    numDecimal = Math.max(Math.min(numDecimal, 20), 0); // toFixed has a max of 20 decimal places
		    tickString = tickValue.toFixed(numDecimal);
/*		} */
		if (yunit == "€" || yunit == "%") {
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
/*	$(this).closest('.topicCollapses').find('.collapseTopic').each(function(){
	    if ($(this).attr('class') != current) {
		$(this).removeClass('in')
	    }
	})
*/ 
   })

    //collapse : highlight button
    $(".ecorse-action-collapse").on('click', function() {
	$(this).closest('.topicCollapses').find('.ecorse-action-collapse').removeClass('active')
	$(this).addClass('active')
    })
    
/*    
    // affichage diagrammes
    Chart.defaults.global.responsive = true;
    
    Chart.defaults.global.legend.position = 'bottom';
//    Chart.defaults.global.scaleBeginAtZero = false;
    
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
*/

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
    
    // Creation nouveau rapport
    
/*
    $('.ecorse-action-create-report').on('click', function() {
	$('#modal_create').show()
	$('.typeahead').typeahead()
    })
*/

    var ref_parameters = {}

    var get_ref_communes = function() {
	var ref = $("#ecorse_select_referentiel").val();
	if (!ref_communes.hasOwnProperty(ref))
	    $.get('/elocus/communes',{'referentiel':ref})
	    .done(function(data) {
		ref_communes[ref] = data;
	    })
    }
    
    var get_ref_parameters = function() {
	var ref = $("#ecorse_select_referentiel").val();
	if (!ref_parameters.hasOwnProperty(ref))
	    $.get('/elocus/refparameters',{'referentiel':ref})
	    .done(function(data) {
		ref_parameters[ref] = data;
		build_create_fields();
	    })
	else
	    build_create_fields();
	
    }

    var get_selected_parameters = function() {
	var ref = $("#ecorse_select_referentiel").val();
	var parameters =  {};
	$.map(ref_parameters[ref], function(v) {
	    var val = $('#'+v.id).typeahead("getActive")
	    if (!val) val = {'id':''}
	    parameters['uservar_'+v.id] = val;
	})
	return parameters;
    }
    
    var build_create_fields = function() {
	var ref = $("#ecorse_select_referentiel").val();
	$('#create_form_parameters').html('')
	$.map(ref_parameters[ref], function(v) {
	    var input = $('<input>',{
		'name':v.id,
		'id':v.id,
		'type':"text",
		'class':"form-control typeahead",
		'data-provide':"typeahead"})
	    
	    $('<div>', {
		'class':"form-group",
		'html':[
		    $('<label>', {
			'for':v.id,
			'class':"col-sm-2 control-label",
			'html':v.label}),
		    $('<div>',{
			'class':"col-sm-10",
			'html':input
		    })
		]
	    }).appendTo('#create_form_parameters')
	    input.typeahead({source:function(query, process) {
		return process(v.values)
	    }})
	})
    }
    
    $('.typeahead_').typeahead({source:function(query, process) {
	var ref = $("#ecorse_select_referentiel").val();
	if (ref_communes.hasOwnProperty(ref))
	    return process(ref_communes[ref]);
	else {
	    return process([]);
	    /*
	    $.get('/ecorse/communes',{'referentiel':ref})
		.done(function(data) {
		    ref_communes[ref] = data;
		    return process(data)
		})
	    */
	}
    }})

    $('#ecorse_select_referentiel').on('change', function() {
	$('.typeahead').val('')
//	get_ref_communes();
	get_ref_parameters();
    });
    
    // typeahead
    $('#modal_create').on('shown.bs.modal', function () {
	// recupere la liste des referentiels
	$.get('/elocus/referentiels').done(function(data) {
	    $('#ecorse_select_referentiel').find('option').remove()
	    $(data).each(function(i,v) {
		$('#ecorse_select_referentiel').append(
		    $('<option>',{'value':v, 'html':v.replace('.html','')})
		);
	    });
   //	    get_ref_communes();
	    get_ref_parameters();
	});
	$('.typeahead').each(function(){
	    $(this).val('')
	})
	$('#ecorse_select_referentiel').focus();

    })

    $('#modal_create_ok').on('click', function () {
	var referentiel = $("#ecorse_select_referentiel").val();
	var title = $('#titre_rapport').val()
	var params = get_selected_parameters();
	params['title'] = title;
	params['toc'] = referentiel; 
	$('#modal_create').hide()
	$('#modal_create_processing').show()
	$.ajax({
	    url:"/elocus/report/create",
	    method:'POST',
	    data:$.param(params)
	}).done(function(data) {
	    if (data.length) {
		var url = window.location.origin + window.location.pathname + '?release=/releases/' + data[0].releasename 
		window.location.replace(url)
	    }
	}).fail(function(data) {
	});
    })



    
    // Action globales sur le rapport
    // Actualisation des données
    $('.ecorse-action-update-data').on('click', function() {
	var release = $('.report').data('release')
	$('#modal_update_processing').show()
	$.ajax({
	    url:"/elocus/report/update",
	    method:'POST',
	    data:$.param({
		'release': release
	    })
	}).done(function(data) {
	    if (data.status == 'ok') {
		window.location.reload(true)
	    }
	}).fail(function(data) {
	});
    })

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

    // Actions sur les indicateurs
    // A la une (star)
    $('.ecorse-action-star').on('click', function() {
	var topic = $(this).closest('.topic')
	var state = !$(this).hasClass('btn-warning')
	var release = $('.report').data('release')
	var btn = $(this)
	$.ajax({
	    url:"/elocus/report/star",
	    method:'POST',
	    data:$.param({
		'release': release,
		    'topic': topic.attr('id'),
		    'state': state
		})
	}).done(function(data) {
	    
	    if (data.status == 'ok') {
		if (state) {
		    btn.addClass('btn-warning')
		    btn.removeClass('btn-default')
		} else {
		    btn.addClass('btn-default')
		    btn.removeClass('btn-warning')
		}
	    }
	}).fail(function(data) {
	});
    })
    
    // masquer
    $('.ecorse-action-hide').on('click', function() {
	var topic = $(this).closest('.topic')
	var state = !$(this).hasClass('ishidden')
	var release = $('.report').data('release')
	var btn = $(this)
	$.ajax({
	    url:"/elocus/report/hide",
	    method:'POST',
	    data:$.param({
		'release': release,
		'topic': topic.attr('id'),
		'state': state
	    })
	}).done(function(data) {
	    
	    if (data.status == 'ok') {
		if (state) {
		    topic.addClass("disabled")
		    btn.addClass('ishidden')
		    btn.removeClass('btn-default')
		} else {
		    topic.removeClass("disabled")
		    btn.addClass('ishidden')
		    btn.removeClass('btn-warning')
		}
	    }
	}).fail(function(data) {
	});
    })

    // bouton détail d'un topic
    
    $('.ecorse-action-showdetails').on('click', function() {
	var topic = $(this).closest('.topic');
	$(topic).addClass('edition')
		
	var modal = $(topic).find('.modal-topic-details');
	modal.modal()
		
    });
    
    $('.modal-topic-details-ok').on('click', function(e) {
	console.log('modal ok')
	var modal = $(this).closest('.modal');
	modal.trigger('confirm.bs.modal');
	modal.modal('hide');
    });
    
})
		  
