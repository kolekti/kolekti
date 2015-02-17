$(document).ready( function () {
    var editor = CKEDITOR.replace( 'editor1', {customConfig: '/static/ckeditor_config_topic.js'});
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
