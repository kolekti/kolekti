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
	if (!ref_parameters.hasOwnProperty(ref)) {
	    $('#create_form_parameters').html('');
	    $("#create_form_parameters_loading").show();
	    $.get('/elocus/refparameters',{'referentiel':ref})
		.done(function(data) {
		    ref_parameters[ref] = data;
		    build_create_fields();
		})
		.always(function() {
		    $("#create_form_parameters_loading").hide();
		});
	}
	else
	    build_create_fields();
	
    }

    var check_selected_parameters = function() {
	var ref = $("#ecorse_select_referentiel").val();
	var parameters =  {};
	$.map(ref_parameters[ref], function(v) {
	    var val = $('#'+v.id).typeahead("getActive")
	    if (typeof val != 'undefined') parameters['uservar_'+v.id] = val;
	})
	return Object.keys(parameters).length > 0;
    }
    
    var get_selected_parameters = function() {
	var ref = $("#ecorse_select_referentiel").val();
	var parameters =  {};
	$.map(ref_parameters[ref], function(v) {
	    var val = $('#'+v.id).typeahead("getActive")
	    if (typeof val == 'undefined')
		parameters['uservar_'+v.id] = {'id':'',name:''};
	    else
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
/*    
    $('.typeahead_').typeahead({source:function(query, process) {
	var ref = $("#ecorse_select_referentiel").val();
	if (ref_communes.hasOwnProperty(ref))
	    return process(ref_communes[ref]);
	else {
	    return process([]);
	}
    }})
*/
    
    $('#ecorse_select_referentiel').on('change', function() {
	$('.typeahead').val('')
	get_ref_parameters();
    });
    
    // typeahead

    var reset_errors = function() {
	$("#create_form_parameters_loading").hide();
	$("#create_form_parameters_error").hide();
	$("#create_form_parameters").removeClass("has-error")
	$(".form-group").removeClass('has-error');
	$("#create_title_field span.help-block").remove();
    }	
    
    $('#modal_create').on('show.bs.modal', function () {
	reset_errors();
	$('#titre_rapport').val('')
    })

    
    $('#modal_create').on('shown.bs.modal', function (e) {
	// recupere la liste des referentiels
	$.get('/elocus/referentiels')
	    .done(function(data) {
		$('#ecorse_select_referentiel').find('option').remove()
		$(data).each(function(i,v) {
		    $('#ecorse_select_referentiel').append(
			$('<option>',{'value':v, 'html':v.replace('.html','')})
		    );
		});
		get_ref_parameters();
	    });
	$('.typeahead').each(function(){
	    $(this).val('')
	});
	$('#ecorse_select_referentiel').focus();
    });
	
    $(".ecorse-action-create-report-project").on('click', function() {
	var project = $(this).data('project');
	var dialog = $(this).data('target');
	project_url = '/projects/activate?project='+project;
	$.get(project_url)
	    .done(function(data) {
		$(dialog).modal();
		$(dialog).trigget('shown.bs.modal');
	    });
    })
    
			  
    $('#modal_create_ok').on('click', function () {
	reset_errors();
	var referentiel = $("#ecorse_select_referentiel").val();
	var title = $('#titre_rapport').val()
	if (title =="") {
	    $("#create_title_field").addClass('has-error')
	    $("#create_title_field").find('input').after($('<span>',{
		"class":"help-block",
		"html":'Ce champ est obligatoire'}))
	    return;
	}
	
	if(!check_selected_parameters()) {
	    $("#create_form_parameters_error").show();
	    $("#create_form_parameters .form-group").addClass('has-error');
	    return
	}

	var params = get_selected_parameters();
	
	params['title'] = title;
	params['toc'] = referentiel;
	
	$('#modal_create').modal('hide');
	$('#modal_create_processing').modal('show');
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
	    $('#modal_create_processing').hide()
	});
    })



    
    // Action globales sur le rapport
    // Actualisation des données
    $('.ecorse-action-update-data').on('click', function() {
	var release = $('.report').data('release')
	$('#modal_update_processing').modal('show')
	$.ajax({
	    url:"/elocus/report/update",
	    method:'POST',
	    data:$.param({
		'release': release
	    })
	}).done(function(data) {
	    $('#modal_update_processing').modal('hide');
	    if (data.status == 'ok') {
		window.location.reload(true)
	    } else {
		$('#modal_error')
		    .find('.errortitle').html("Une erreur s'est produite lors de l'actualisation des données");
		$('#modal_error')
		    .find('.errormessage').html(data.msg)	    
		$('#modal_error').modal('show');
	    }
	}).fail(function(data) {
	    $('#modal_update_processing').modal('hide')
	    $('#modal_error')
		.find('.errortitle').html("Une erreur s'est produite lors de l'actualisation des données");
	    $('#modal_error')
		.find('.errormessage').html("Coupure de la communication avec le serveur");	    
	    $('#modal_error').modal('show');
	});	       
    });

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
	$("#modal_export_processing").modal("show")
	$.ajax({
	    url:"/elocus/report/publish",
	    method:'POST',
	    data:$.param({
		'release': release,
		'script': 'odt'
	    })
	}).done(function(data) {
	    
	    $.each(data, function(i,v) {
		if (v.event == 'result')
		    window.location.replace(window.location.origin + v.docs[0].url)
	    })
	}).fail(function(data) {
	}).always(function() {
	    $("#modal_export_processing").modal("hide")
	})

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
	var release = $('.report').data('release')
	$.ajax({
	    url:"/elocus/report/sharelink",
	    method:'GET',
	    data:$.param({
		'release': release,
	    })
	}).done(function(data) {
	    $("#modal_share #ecorse_share_url").val(data.url);
	    $("#modal_share #ecorse_share_link").attr('href',data.url);
	    $("#modal_share").modal("show")
	}).fail(function(data) {
	});
	
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
		    btn.addClass('btn-primary')
		} else {
		    topic.removeClass("disabled")
		    btn.removeClass('ishidden')
		    btn.addClass('btn-default')
		    btn.removeClass('btn-primary')
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
	modal.data('elocus_params', {})
	
	modal.trigger('confirm.bs.modal');
	$.ajax({
	    url:"/elocus/topic/save",
	    method:'POST',
	    data:$.param(modal.data('elocus_params'))
	}).done(function(data) {
	    console.log('topic post done')
	    if (data.status == 'ok') {
		modal.trigger('confirmed.bs.modal');
		console.log('topic post ok')		
	    } else {
		console.log(data)
	    }
	}).fail(function(data) {
	    console.log('chart post fail')
	});
	
	modal.modal('hide');
    });
    
})
		  
