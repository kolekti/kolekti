$(document).ready(function() {
    console.log('toclist')
    var create_toc = function(browser, folder, update_function) {
	    var filename = $('#new_name').val();
        console.log('craate')
        console.log(folder)
        var lang = folder.split('/')[2]
        var toc_folder = folder.split('/').splice(4). join('/')
	    $.post(Urls.kolekti_toc_create(kolekti.project, lang, toc_folder + "/" + filename))
	        .success(function() {
                console.log('create done')
		        update_function()
            })
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
                var lang = path.split('/')[3]
                var toc_path = path.split('/').splice(5). join('/')
                console.log(lang, toc_path)
		        document.location.href = Urls.kolekti_toc_edit(kolekti.project, lang, toc_path)
	        })
	    .create(create_toc)
});
