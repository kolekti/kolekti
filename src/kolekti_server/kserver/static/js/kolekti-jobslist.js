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
		     'os_actions':'yes',
		     'modal':"no",
		     'create_actions':'yes'
		    })
	.select(
	    function(path) {
		location.assign('/settings/job?path='+path);
	    }
	)
	.create(function(folder, update_function){
	    var filename = $('.filename').val();
	    $.post('/settings/jobs/create/',
		   {'path':folder + "/" + filename})
		.success(update_function)
	});
})