$(document).ready(function() {
    var path = $('.browserparent').data('browserpath')

    kolekti_browser({'root':'/kolekti/publication-parameters/',
		     'parent':".browser",
		     'buttonsparent':".buttons",
		     'os_actions':'yes',
		     'modal':"no",
		     'create_actions':'yes'
		    })
	.select(
		    function(path) {
                var job_path = path.replace('/' + kolekti.project + '/kolekti/publication-parameters/','')
		        var url = Urls.kolekti_job_edit(kolekti.project, job_path)
			    document.location.href = url
	    }
	)
	.create(function(browser,folder, update_function){
	    var filename = $('.filename').val();
        $.post(Urls.kolekti_job_create(kolekti.project),
		   {'path':folder + "/" + filename})
		.success(update_function)
	});
})
