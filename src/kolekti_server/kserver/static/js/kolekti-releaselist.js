$(document).ready(function() {

    kolekti_browser({'root':'/releases',
		     'parent':".browser",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no"
		    })
	.select(
	    function(path) {
		document.location.href = '/releases/detail/?release='+path
/*
		$.get('/releases/detail/',{'path':path})
		    .success(function(data) {
			$('#detail_release').html($(data));
		    })
		//	document.location.href = '/release/detail/?release='+path
*/
	    })
})