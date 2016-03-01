$(document).ready( function () {

    $('.btn-lang').click(function() {
	var lang = $(this).data('lang')
	var release = $('#main').data('release')
	window.location.href = "/releases/detail/?release="+release+"&lang="+lang;
    })
    
/*

Initialize ck editor for assembly editing 
Defines events for languages and release state in toolbar

*/
    
/*
    var editor = CKEDITOR.replace( 'editor1', {
	autoGrow_onStartup : true,
	height:"600px",
	contentsCss : '/criteria.css',
	extraPlugins : 'codemirror,textselection,conditions',
	extraAllowedContent : 'var ins span *(*)',
	entities : false,
	filebrowserBrowseUrl: '/browse/ckbrowser',
	filebrowserImageBrowseUrl: '/browse/ckbrowser?path=/sources/'+kolekti.lang+'/pictures/',
	filebrowserLinkBrowseUrl: '/browse/ckbrowser?path=/sources/'+kolekti.lang+'/topics/',
//	filebrowserUploadUrl: '/browse/ckupload',
//	filebrowserImageUploadUrl: '/browse/ckupload?type=Images',
	
	toolbar_Full : [
	    { name: 'document',    groups: [ 'mode', 'document', 'doctools' ], items: [ 'Save', 'Preview', 'Source', 'Print' ] },
	    { name: 'clipboard',   groups: [ 'clipboard', 'undo' ], items: [ 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 'Undo', 'Redo' ] },
	    { name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ], items: [ 'Find', 'Replace', 'SelectAll', 'Scayt' ] },
	    { name: 'insert', items: [ 'Image', 'Table', 'HorizontalRule', 'SpecialChar' ] },
	    { name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
	    { name: 'about', items: [ 'About' ] },
	    '/',
	    { name: 'tools', items: [ 'ShowBlocks' ] },
	    { name: 'styles', items: [ 'Format' ] },
	    { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ], items: [ 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', 'RemoveFormat' ] },
	    { name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align' ], items: [ 'NumberedList', 'BulletedList', 'CreateDiv', 'conditions'] }
	],
	toolbar:"Full"


    });

    //	customConfig: '/static/ckeditor_config_topic.js'});
    
    var savestate = 0;

    editor.on( 'instanceReady', function(event){ 					
//	event.editor.execCommand( 'maximize'); 
	event.editor.commands.save.disable();
    });
    
    editor.on( 'save', function(event){ 
	$.ajax({
	    url:window.location.pathname+window.location.search,
	    type:'POST',
	    data:event.editor.getData(),
	    contentType:'text/plain'
	}).success(function(data) {
	    savestate = 0;
	    event.editor.commands.save.disable();
//	    console.log('save ok')
	});

	event.cancel();
    });

    editor.on( 'change', function( event ) {
	event.editor.commands.save.enable();
	savestate = 1;
    });

    $( window ).on('beforeunload', function() {
	var e = $.Event('webapp:page:closing');
	$(window).trigger(e); // let other modules determine whether to prevent closing
	if(e.isDefaultPrevented()) {
            // e.message is optional
            return e.message || 'le document a été modifié, voulez vous réélement quitter sans enregistrer ?';
	}
    });

    $(window).on('webapp:page:closing', function(e) {
	if(savestate) {
            e.preventDefault();
            e.message = 'le document a été modifié, voulez vous réélement quitter sans enregistrer ?';
	}
    });
*/
/*

	if (savestate) {
	    if(! confirm('')) {
		return "
	    
	return "ko";
    });
*/
    
    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').removeClass('hidden');
	$('#btn_save').addClass('btn-warning');
    };

    $(window).on('beforeunload', function(e) {
	if($('#btn_save').hasClass('btn-warning')) {
            return 'Version non enregistrée';
	}
    });


    
    // Kolekti Release toolbar

    $('.nav-tabs .active .state.lead ').on('click', function() {
	var tab = $(this).closest('a');
	has_focus = tab.hasClass('focus');
	$.ajax({
	    url:"/releases/focus/",
	    method:'POST',
	    data:$.param({
		'release': $('#main').data('release'),
		'lang'   : $('#main').data('lang'),
		'state'  : !has_focus
	    })
	}).done(function(data) {
	    if (data.status='OK')
	    {
		if (has_focus)
		    tab.removeClass('focus');
		else
		    tab.addClass('focus');
	    }
	});
    })

    
    $('.release-state').on('click', function() {
	var lang = $(this).closest('ul').data('target-lang');
	var oldstate = $('.btn-lang-menu-'+lang).data('state')
	var newstate = $(this).data('state')
	var labelstate = $(this).find('span').html()
	$('.btn-lang-menu-'+lang).removeClass('btn-lang-menu-'+oldstate)
	enable_save()
	$('#release_tabs .active img').attr('src','/static/img/release_status_'+newstate+'.png')
	$('.btn-lang-menu-'+lang).addClass('btn-lang-menu-'+newstate)
	$('.btn-lang-menu-'+lang+' .state').html(labelstate);

	$('#main').data('state', newstate)
	$('#main').attr('data-state', newstate)

	
    });
	
    $('#btn_assembly').on('click', function() {
	$('#preview').parent().addClass('hidden');
	$('.btn-release-pane').removeClass('active')
	$(this).addClass('active')
	$('.release-panel-part').addClass('hidden')
	$('#content_pane').removeClass('hidden')
    })

    $('#btn_illust').on('click', function() {
	$('.btn-release-pane').removeClass('active')
	$(this).addClass('active')
	$('.release-panel-part').addClass('hidden')
	$('#illust_pane').removeClass('hidden')
	console.log($('#main').data('release'))
	kolekti_browser({'root':$('#main').data('release')+'/sources/'+$('#main').data('lang')+'/pictures',
			 'parent':"#illust_pane",
			 'title':" ",
			 'titleparent':".title",
			 'mode':"selectonly",
			 'modal':"no",
			 'drop_files':true,
			 'os_actions':'yes',
			 'create_actions':'yes',
			 'create_builder':upload_image_builder_builder()
			})
	    .select(
		function(path) {
		    $.get('/images/details?path='+path)
			.done(
			    function(data) {
				$('#preview').html([
				    $('<h4>',{'html':displayname(path)}),
				    data
				]);
				$('#preview img').attr('src',path);
				$('#preview').parent().removeClass('hidden');
			    }
			)
		})
	    .create(upload_image)
	
    })

    $('#btn_variables').on('click', function() {
	$('#preview').parent().addClass('hidden');
	$('.btn-release-pane').removeClass('active')
	$(this).addClass('active')
	$('.release-panel-part').addClass('hidden')
	$('#variables_pane').removeClass('hidden')
	kolekti_browser({'root':$('#main').data('release')+'/sources/'+$('#main').data('lang')+'/variables',
		     'parent':"#variables_pane",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes',
		     'create_builder':upload_variable_builder_builder()
		    })
	.select(
	    function(path) {
		
	    })
	.create(upload_varfile)
	.setup_file(setup_varfile);
    })

    $('#btn_save').on('click', function() {
	$.ajax({
	    url:"/releases/state/",
	    method:'POST',
	    data:$.param({
		'release': $('#main').data('release'),
		'state' :  $('#main').data('state'),
		'lang'  :  $('#main').data('lang')
	    })
	}).done(function(data) {
	    $('#btn_save').addClass('disabled');
	    $('#btn_save').addClass('btn-default');
	    $('#btn_save').removeClass('btn-warning');
	    kolekti_recent(displayname($('#main').data('release')), 'version', '/releases/detail/?release=' + $('#main').data('release') + '&lang=' + $('#main').data('lang'))
	});
    })

    var get_publish_languages = function(all_languages) {
	if (all_languages) {
	    var langs = []
	    $('#kolekti_tools .btn-lang-menu-publication').each( function() {
		langs.push($(this).prev().first().data('lang'));
	    });
	    return langs;
	} else {
	    return [ $('#release_tabs .active a').first().data('lang') ]
	}
    }

    $('.upload_form').on('submit', function(e) {
	kolekti_recent(displayname($('#main').data('release')), 'version', '/releases/detail/?release=' + $('#main').data('release') + '&lang=' + $('#main').data('lang'))
    })
			 
    
    /*
    $('#release_tabs a').click(function (e) {

	e.preventDefault()
	var lang  = $(this).data('lang');
	var state = $(this).data('state');
	if (state != "unknown") {
	    $('#main').data('lang', lang)
	    load_assembly();
	    $('#panel_download').show()
	} else {
	    $('#panel_download').hide()
	}
    })
	*/

    // content loading function
    var load_assembly = function() {
	$.get('/releases/assembly',{
	    'release':$('#main').data('release'),
	    'lang':$('#main').data('lang')
	}).success(function(data) {
	    $('#content_pane').html(data)
	})
    }
    
    load_assembly();




    
    // publication button

    $('.btn_publish').on('click', function() {
	var url='/releases/publish/'

	$('.modal-body').html('<div id="pubresult"></div>');
	$('.modal-title').html('Publication');
	$('.modal-footer button').html('fermer');
	$('.modal').modal();
	$('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Publication de la version</h4></div><div class="panel-body"><div class="progress" id="pub_progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Publication in progress</span></div></div><div id="pub_results"></div><div id="pub_end" class="alert alert-info" role="alert">Publication terminée</div></div></div>').appendTo($('#pubresult'));
	//params = get_publish_params(job)

	$('#pub_end').hide();
	
	var params = {}
	var release = $('#main').data('release')
	params['release']=release;
	var alllang = ($(this).attr('id') == "btn_publish_all")
	params['langs']= get_publish_languages(alllang);
	var streamcallback = function(data) {
	    $("#pub_results").html(data);
	}
	
	$.ajaxPrefilter("html streamed", function(){return "streamed"});
	streamedTransport(streamcallback);
	$.ajax({
	    url:url,
	    type:'POST',
	    data:params,
	    dataType:"streamed",
	    beforeSend:function(xhr, settings) {
		ajaxBeforeSend(xhr, settings);
		settings.xhr.onreadystatechange=function(){
		    console.log(xhr.responseText);
		}
	    }
	}).done(function(data) {
	    $("#pub_results").html(data);
	}).fail(function(jqXHR, textStatus, errorThrown) {
	    $('#pub_results').html([
		$('<div>',{'class':"alert alert-danger",
			   'html':[$('<h5>',{'html':"Erreur"}),
				   $('<p>',{'html':"Une erreur inattendue est survenue lors de la publication"})
				   
				  ]}),
		$('<a>',{
		    'class':"btn btn-primary btn-xs",
		    'data-toggle':"collapse",
		    'href':"#collapseStacktrace",
		    'aria-expanded':"false",
		    'aria-controls':"collapseStracktrace",
		    'html':'Détails'}),
		$('<div>',{'class':"well",
			   'html':[
			       $('<p>',{'html':textStatus}),
			       $('<p>',{'html':errorThrown}),
			       $('<pre>',{'html':jqXHR.responseText})]
			  })
	    ]);
	}).always(function() {
	    $('#pub_progress').remove();
	    $('#pub_end').show();
	});
    })

    

})
