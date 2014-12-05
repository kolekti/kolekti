$(document).ready(function() {

    $('#btn_create').on("click", function(e) {
	var folder = $('.browserparent').data('path');
	var file = $('#new_name').val()
	$.post('/topics/create/',
	       {'modelpath': $('#template').data('path'),
		'topicpath': folder + "/" + file
	       })
	    .success(
		window.location.reload()
	    )
    })
    
    $('#template').append();

    kolekti_browser({'root':'/sources/'+kolekti.lang+'/topics',
		     'parent':".browserparent",
		     'buttonsparent':".buttons",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes'
		    })
	.select(
	    function(path) {
		window.open('/topics/edit/?topic='+path);
	    }
	)
})