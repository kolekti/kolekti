$(document).ready(function() {
    var create_toc = function(browser, folder, update_function) {
	var filename = $('#new_name').val();
	$.post(Urls.kolekti_toc_create(folder + "/" + filename))
	    .success(
		update_function()
	    )
    };

    var create_builder = function(e, path) {
	e.prepend(   
	    [gettext('Nouvelle trame : '),
	     $('<input>',{ 'type':"text",
			   'id':'new_name',
			   'class':"form-control filename"
			 }),
	     $('<br>')
	    ]);	
    };

    var path = $('.browser').data('browserpath')
    kolekti_browser({'root': "/sources/" + kolekti.lang + '/tocs',
                     'path': path,
                     'urlname': 'kolekti_tocs_browse',
		             'parent':".browser",
		             'title':" ",
		             'titleparent':".title",
		             'mode':"selectonly",
		             'modal':"no",
		             'os_actions':'yes',
		             'create_actions':'yes',
		             'create_builder':create_builder
		            })
	    .select(
	        function(path) {
                console.log(path)
                var tocpath = path.replace('/' + kolekti.project + '/sources/'+kolekti.lang+'/tocs/','')
		        document.location.href = Urls.kolekti_toc_edit(kolekti.project, kolekti.lang, tocpath)
	        })
	    .create(create_toc)
});
