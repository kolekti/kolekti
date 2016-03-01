$(document).ready( function () {
    
    var editor = CKEDITOR.replace( 'editor1', {
	autoGrow_onStartup : true,
	fullPage:true,
	contentsCss : '/criteria.css',
	skin : 'moonocolor',
	extraPlugins : 'codemirror,textselection,conditions,docprops',
	allowedContent:true,
	//	extraAllowedContent : 'var ins dl dt dd span *(*)',
	entities : false,
	fillEmptyBlocks: false,
	filebrowserBrowseUrl: '/browse/ckbrowser',
	filebrowserImageBrowseUrl: '/browse/ckbrowser?path=/sources/'+kolekti.lang+'/pictures/',
	filebrowserLinkBrowseUrl: '/browse/ckbrowser?path=/sources/'+kolekti.lang+'/topics/',
	
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
	    { name: 'styles', items: [ 'Format' ] },
	    { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ], items: [ 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', 'RemoveFormat' ] },
	    { name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align' ], items: [ 'NumberedList', 'BulletedList', 'CreateDiv','RemoveDiv'] }
	],
	toolbar:"Full"


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
	    savestate = 0;
	    event.editor.commands.save.disable();
	    //	    console.log('save ok')
	    kolekti_recent(displayname(window.location.search),'module',window.location.pathname+window.location.search);
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
})
