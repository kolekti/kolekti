$(document).ready(function() {

    kolekti_browser({'root':'/releases',
		     'parent':".browser",
		     'title':"Selectionnez un assemblage",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no"
		    })
	.select(
	    function(path) {
		$.get('/releases/detail/',{'path':path})
		    .success(function(data) {
			$('#detail_release').html($(data));
		    })
		//	document.location.href = '/release/detail/?release='+path
	    })
})