$(document).ready(function() {

    kolekti_browser({'root':'',
		     'parent':".browser",
		     'title':"Selectionnez un objet",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no"
		    })
	.select(
	    function(path) {
		window.open('/static'+path);
	    }
	)
})