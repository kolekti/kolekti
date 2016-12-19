$(document).ready(function() {

    kolekti_browser({'root':'/kolekti/publication-templates',
		     'parent':".browser",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'drop_files':'yes',
		     'create_actions':'no'
//		     'create_builder':create_builder
		    })
/*
	.select(
	    function(path) {
		document.location.href = '/tocs/edit/?toc='+path
	    })
	.create(create_toc)
*/
});
