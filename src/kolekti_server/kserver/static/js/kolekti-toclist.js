$(document).ready(function() {

    kolekti_browser({'root':'/sources/'+kolekti.lang+'/tocs',
		     'parent':".browser",
		     'title':"Selectionnez une trame",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no"
		    })
	.select(
	    function(path) {
		document.location.href = '/tocs/edit/?toc='+path
	    }
	)
})