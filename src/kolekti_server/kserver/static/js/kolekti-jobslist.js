$(document).ready(function() {

    $('#btn_create').on("click", function(e) {
	var folder = $('.browserparent').data('path');
	var file = $('#new_name').val()
	$.post('/settings/jobs/create/',
	       {
		   'path': folder + "/" + file
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
		location.assign('/settings/job?path='+path);
	    }
	)
})