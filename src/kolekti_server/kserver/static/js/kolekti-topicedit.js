$(document).ready( function () {
    var editor = CKEDITOR.replace( 'editor1', {customConfig: '/static/ckeditor_config_topic.js'});
    editor.on( 'instanceReady', function(event){ 					
	event.editor.execCommand( 'maximize'); 
    });
    editor.on( 'save', function(event){ 
	$.ajax({
	    url:window.location.pathname+window.location.search,
	    type:'POST',
	    data:event.editor.getData(),
	    contentType:'text/plain'
	}).success(function(data) {
	    console.log('save ok')
	});

	event.cancel();
    });
})
