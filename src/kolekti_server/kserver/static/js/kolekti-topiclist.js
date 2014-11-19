$(document).ready(function() {

    kolekti_browser({'root':'/sources/'+kolekti.lang+'/topics',
		     'parent':".browser",
		     'title':"Selectionnez un module",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no"
		    })
	.select(
	    function(path) {
		window.open('/topics/edit/?topic='+path);
	    }
	)
})