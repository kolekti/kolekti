$(document).ready( function () {

    
	
    var make_editor = function(templates, buttons) {
	console.log(templates)
	var editor = CKEDITOR.replace( 'editor1', {
	    autoGrow_onStartup : true,
	    fullPage:true,
	    contentsCss : '/criteria.css',
	    skin : 'moonocolor',
	    extraPlugins : 'codemirror,textselection,conditions,docprops,htmlbuttons',
	    allowedContent:true,
	    //	extraAllowedContent : 'var ins dl dt dd span *(*)',
	    entities : false,
	    fillEmptyBlocks: false,
	    filebrowserBrowseUrl:      Urls.kolekti_ckbrowser(kolekti.project),
	    filebrowserImageBrowseUrl: Urls.kolekti_ckbrowser(kolekti.project)+'?path=/sources/'+kolekti.lang+'/pictures/',
	    filebrowserLinkBrowseUrl:  Urls.kolekti_ckbrowser(kolekti.project)+'?path=/sources/'+kolekti.lang+'/topics/',
	    
	    //	filebrowserUploadUrl: '/browse/ckupload',
	    //	filebrowserImageUploadUrl: '/browse/ckupload?type=Images',
	    
	    toolbar_Full : [
		{ name: 'document',    groups: [ 'mode', 'document', 'doctools' ], items: [ 'Save', 'Preview', 'Source', 'Print' , 'DocProps'] },
		{ name: 'clipboard',   groups: [ 'clipboard', 'undo' ], items: [ 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 'Undo', 'Redo' ] },
		{ name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ], items: [ 'Find', 'Replace', 'SelectAll', 'Scayt' ] },
		{ name: 'insert', items: [ 'Image', 'Table', 'HorizontalRule', 'SpecialChar' ] },
		{ name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
		{ name: 'about', items: [ 'About' ] },
		    '/',
		{ name: 'tools', items: [ 'ShowBlocks', 'editCondition', 'removeCondition' ] },
		{ name: 'styles', items: [ 'Styles', 'Format' ] },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ], items: [ 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', 'RemoveFormat' ] },
		{ name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align' ], items: [ 'NumberedList', 'BulletedList', 'CreateDiv','RemoveDiv'] },
		{ name: 'templates', items: buttons }		
		],
	    toolbar:"Full",
	    contentCss:Urls.kolekti_project_static(kolekti.project,'kolekti/edition-templates/styles.css'),
	    stylesSet:[],
	    htmlbuttons : templates
	});
	
	    //	customConfig: '/static/ckeditor_config_topic.js'});
	
	var savestate = 0;
	
	editor.on( 'instanceReady', function(event){ 					
	    event.editor.execCommand( 'maximize'); 
	    event.editor.commands.save.disable();
	});
	
	editor.on( 'save', function(event){ 
	    var doc = editor.document;
	    /*
	      var nkeys = doc.getCustomData('nbmeta')
	      var meta = []
	      for (var index = 0; index < nkeys; index++) {
	      var n = doc.getCustomData( 'metaname'+index);
	      var v = doc.getCustomData( 'metavalue'+index);
	      meta.push(n+':'+v)
	      }
	      headers= {'METADATA':meta.join(';')}
	    */
	    $.ajax({
		url:window.location.pathname+window.location.search,
		type:'POST',
		//	    headers:headers,
		data:event.editor.getData(),
		contentType:'text/plain'
	    }).success(function(data) {
		if (data.status == 'ok') {
		    savestate = 0;
		    event.editor.commands.save.disable();
		    kolekti_recent(displayname(decodeURI(window.location.search)),'module',window.location.pathname+window.location.search);
		} else {
		    $('#error_msg').html(data.msg);
		    $('#error_modal').modal({
			backdrop: false
		    });
		    $('#error_modal').modal('show');
		}
	    });
	    
	    event.cancel();
	});
	
	editor.on( 'change', function( event ) {
	    event.editor.commands.save.enable();
	    savestate = 1;
	});
    }
    $( window ).on('beforeunload', function() {
	var e = $.Event('webapp:page:closing');
		$(window).trigger(e); // let other modules determine whether to prevent closing
	if(e.isDefaultPrevented()) {
	    // e.message is optional
	    return e.message || 'le document a été modifié, voulez vous réellement quitter sans enregistrer ?';
	}
    });
    
    $(window).on('webapp:page:closing', function(e) {
	if(savestate) {
	    e.preventDefault();
	    e.message = 'le document a été modifié, voulez vous réellement quitter sans enregistrer ?';
	}
    });

    $.getJSON("/kolekti/edition-stylesheets/templates.json")
	.done(function(data) {
	    var buttons = $.map(data, function(item) { return item.name })
	    make_editor(data, buttons)
	})
	.fail(function(why) {
	    make_editor([], [])
	})
})
