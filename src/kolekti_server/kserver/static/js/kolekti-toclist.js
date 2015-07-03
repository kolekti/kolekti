$(document).ready(function() {
    var create_toc = function(browser, folder, update_function) {
	var filename = $('#new_name').val();
	$.post('/tocs/create/',
	       {
		   'tocpath': folder + "/" + filename
	       })
	    .success(
		update_function()
	    )
    };

    var create_builder = function(e, path) {
	e.prepend(   
	    ['Nouvelle trame : ',
	     $('<input>',{ 'type':"text",
			   'id':'new_name',
			   'class':"form-control filename"
			 }),
	     $('<br>')
	    ]);	
    };

    kolekti_browser({'root':'/sources/'+kolekti.lang+'/tocs',
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
		document.location.href = '/tocs/edit/?toc='+path
	    })
	.create(create_toc)
});
