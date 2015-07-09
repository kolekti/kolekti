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

/*

	if (savestate) {
	    if(! confirm('')) {
		return "
	    
	return "ko";
    });
*/

    // Kolekti Release toolbar

    $('.btn-lang-copy').on('click', function() {
	var state = $(this).data('state');
	var lang  = $(this).data('lang');
	$('#modalform').attr('action','/releases/copy/'+window.location.search);
	$('#modalform input[name=release_lang]').attr('value',lang);
	$('.modal').modal();
    });

    $('.release-state').on('click', function() {
	var targetlang = $(this).closest('ul').data('target-lang');
	$.ajax({
	    url:"/releases/state/"+window.location.search,
	    method:'POST',
	    data:$.param({
		'state' : $(this).data('state'),
		'targetlang'  : targetlang
	    })
	}).done(function(data) {
	    $('.btn-lang-menu-'+targetlang+' img').attr('src','/static/img/release_status_'+data+'.png')
	})
	
    })

    var get_publish_langs = function(what) {
	if (what == "all") {
	} else {
	    
	}
    }

    // publication button
    $('.btn_publish').on('click', function() {
	var url='/releases/publish/'

	$('.modal-body').html('<div id="pubresult"></div>');
	$('.modal-title').html('Publication');
	$('.modal-footer button').html('fermer');
	$('.modal').modal();
	$('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Lancement '+job+'</h4></div><div class="panel-body"><div class="progress" id="pub_progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Publication in progress</span></div></div><div id="pub_results"></div></div></div>').appendTo($('#pubresult'));
	//params = get_publish_params(job)
	
	var release = $('#main').data('release')
	params['release']=release;
	params['langs']= ??;
	    
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
	});
    })

})
