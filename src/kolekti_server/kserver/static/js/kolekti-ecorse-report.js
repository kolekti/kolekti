$(document).ready(function() {
    CKEDITOR.disableAutoInline = true;
    // CKEDitor Behavior
    // The "instanceCreated" event is fired for every editor instance created.
    CKEDITOR.on( 'instanceCreated', function ( event ) {
	console.log("ck")
	var editor = event.editor,
	    element = editor.element;
	
	// Customize editors for headers and tag list.
	// These editors do not need features like smileys, templates, iframes etc.
	// Customize the editor configuration on "configLoaded" event,
	// which is fired after the configuration file loading and
	// execution. This makes it possible to change the
	// configuration before the editor initialization takes place.
	editor.on( 'configLoaded', function () {
	    
	    // Remove redundant plugins to make the editor simpler.
	    editor.config.removePlugins = 'colorbutton,find,flash,font,' +
		'forms,iframe,newpage,removeformat,' +
		'smiley,specialchar,stylescombo,templates';
	    
	    // Rearrange the toolbar layout.
	    editor.config.toolbarGroups = [
		{ name: 'editing', groups: [ 'basicstyles', 'links', 'image' ] },
		{ name: 'undo' },
		{ name: 'clipboard', groups: [ 'selection', 'clipboard' ] },
		{ name :"paragraph", groups :['list','blocks']},
		{ name: 'about' }
	    ];
	    
	    editor.config.removeButtons='Strike,Anchor,Styles,Specialchar,CreateDiv,SelectAll'
	} );
	editor.on('change', function() {
	    editor.ecorse_state = true
	});
	editor.on( 'blur', function () {
	    if (editor.ecorse_state) {
		var release = $('.report').data('release')
		var topicid = $(editor.element.$).closest('.topic').attr('id')
		var data = editor.getData()
		$.ajax({
		    url:"/ecorse/report/analysis",
		    method:'POST',
		    data:$.param({
			'release': release,
			'topic' : topicid,
			'data':data
		    })
		}).done(function(data) {
		    if (data.status == 'ok') {
			console.log('saved')
			editor.ecorse_state = false;
		    }
		}).fail(function(data) {
		});
		
	    }
	});
    } );
    

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
    
    // collapse : initialisation CKEditor sur déroulé
    $('.collapseAnalyse').on('shown.bs.collapse', function () {
	var editor, edid = $(this).find('.anaeditor').attr('id')
	if (CKEDITOR.instances[edid] == undefined)
	    editor = CKEDITOR.inline(edid,{startupFocus : true})
	else {
	    editor = CKEDITOR.instances[edid]
	    editor.focus()
	}
	editor.ecorse_state = false
    })
    
    // affichage diagrammes
    Chart.defaults.global.responsive = true;
    var chartcolors = ['220,51,51', '51,51,220', '51,220,61'];
    
    var make_chart  = function(canvas, kind, data) {
        for (s=0; s < data['seriescount']; s++) {
 	    data['datasets'][s]["fillColor"] = "rgba("+chartcolors[s]+",0.5)";
  	    data['datasets'][s]["strokeColor"] = "rgba("+chartcolors[s]+",0.8)";
	    data['datasets'][s]["highlightFill"] = "rgba("+chartcolors[s]+",0.75)";
	  data['datasets'][s]["highlightStroke"] = "rgba("+chartcolors[s]+",1)";
        }
        var ctx = document.getElementById(canvas).getContext("2d");
	var myNewChart = new Chart(ctx)[kind](data);
    }

    
    $('.kolekti-sparql-result-chartjs').each(function() {
	var data = $(this).data('chartjs-data')
	var kind = $(this).data('chartjs-kind')
	var canvas   = $(this).find('canvas').attr('id')
	make_chart(canvas, kind, data);
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
    });

    // actions
    
    // Creation nouveau rapport
    
/*
    $('.ecorse-action-create-report').on('click', function() {
	$('#modal_create').show()
	$('.typeahead').typeahead()
    })
*/

    // typeahead
    $('#modal_create').on('shown.bs.modal', function () {
	$('#titre_rapport').focus()
	$.get('/ecorse/communes').done(function(data) {
	    communes = data
	    $('.typeahead').typeahead({source:data})
	    
	})

    })

    $('#modal_create_ok').on('click', function () {
	console.log('ok')
	var title = $('#titre_rapport').val()
	var commune1 = $('#commune1').typeahead("getActive")
	var commune2 = $('#commune2').typeahead("getActive")
	var commune3 = $('#commune3').typeahead("getActive")
	if (!commune1)
	    commune1 = {'id':''}
	if (!commune2)
	    commune2 = {'id':''}
	if (!commune3)
	    commune3 = {'id':''}
	
	console.log(title)
	console.log(commune1)
	console.log(commune2)
	console.log(commune3)
	
	$.ajax({
	    url:"/ecorse/report/publish",
	    method:'POST',
	    data:$.param({
		'title': title,
		'commune1':commune1.id,
		'commune2':commune2.id,
		'commune3':commune3.id
	    })
	}).done(function(data) {
	    console.log(data)
	    if (data.status == 'ok') {
		window.location.url = '?release='+data.release
	    }
	}).fail(function(data) {
	});
    })
			     
    // Action globales sur le rapport
    // Actualisation des données
    $('.ecorse-action-update-data').on('click', function() {
	var release = $('.report').data('release')
	$.ajax({
	    url:"/ecorse/report/update",
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
	
    })
    $('.ecorse-action-dl-word').on('click', function() {
	
    })
    $('.ecorse-action-dl-presentation').on('click', function() {
	
    })
    $('.ecorse-action-dl-html').on('click', function() {
	
    })

    // Actions sur les indicateurs
    // A la une (star)
    $('.ecorse-action-star').on('click', function() {
	var topic = $(this).closest('.topic')
	var state = !$(this).hasClass('btn-warning')
	var release = $('.report').data('release')
	var btn = $(this)
	$.ajax({
	    url:"/ecorse/report/star",
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
	    url:"/ecorse/report/hide",
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

	// selection graphique
    var ecorse_set_chart = function(charttype){
	return 
    }
    
    $('.ecorse-action-chart').on('click', function() {
	if(!$(this).find('i').length) {
	    var btn = $(this)
	    var charttype = $(this).attr('data-chart-type')
	    var topic = $(this).closest('.topic')
	    var release = $('.report').data('release')
	    
	    $.ajax({
		url:"/ecorse/report/charttype",
		method:'POST',
		data:$.param({
		    'release': release,
		    'topic': topic.attr('id'),
		    'charttype': charttype
	    })
	    }).done(function(data) {
		
		if (data.status == 'ok') {
		    btn.closest('ul').find('i').remove();
		    btn.append('<i>', { 'class':'fa fa-icon-ok'});
		    var chart = btn.closest('.thumbnail').find('.kolekti-sparql-result-chartjs')
		    chart.attr('data-chartjs-kind',charttype)
		    var data = chart.data('chartjs-data')
		    var canvas   = chart.find('canvas').attr('id')
		    make_chart(canvas, charttype, data);
		    
		}
	    }).fail(function(data) {
	    });
	    
	}
    })
    
})
		  
