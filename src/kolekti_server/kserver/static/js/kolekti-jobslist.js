$(document).ready(function() {

    $('#btn_create').on("click", function(e) {
	var folder = $('.browserparent').data('path');
	var file = $('#new_name').val()
	$.post('/jobs/create/',
	       {'modelpath': $('#template').data('path'),
		'topicpath': folder + "/" + file
	       })
	    .success(
		window.location.reload()
	    )
    })
    

    kolekti_browser({'root':'/kolekti/publication-parameters',
		     'parent':".browserparent",
		     'buttonsparent':".buttons",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes'
		    })
	.select(
	    function(path) {
		window.open('/settings/job?path='+path);
	    }
	)
})