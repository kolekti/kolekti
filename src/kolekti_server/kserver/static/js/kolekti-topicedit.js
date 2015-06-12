$(document).ready( function () {
    
    var editor = CKEDITOR.replace( 'editor1', {
	autoGrow_onStartup : true,
	contentsCss : '/criteria.css',
	extraPlugins : 'codemirror,textselection,conditions',
	extraAllowedContent : 'span *(*)',
	entities : false,
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
	event.editor.execCommand( 'maximize'); 
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
})
