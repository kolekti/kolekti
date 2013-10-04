$(function() {

    var selector = 'div[contenteditable="true"]';

    $(selector).focusout(function(e) {
	console.log('focusout');
	if ($(this).data('content') == $(this).html()) {
	    console.log('not modified');
	    return;
	}
    });

    // initialize the "save" function
    $(selector).focus(function(e) {
	$(this).data('content', $(this).html());	
	console.log('focus');
    });
    
    var toolbar = function(editable) {
    }

});