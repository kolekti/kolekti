$(document).ready(function() {

    kolekti_browser({'root':'/releases',
		     'url':"/browse/releases/",
		     'parent':".browser",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_action_delete':'yes'
		    })
	.select(
	    function(path) {
		document.location.href = '/releases/detail/?release='+path+'&lang='+kolekti.lang
		
/*
		$.get('/releases/detail/',{'path':path})
		    .success(function(data) {
			$('#detail_release').html($(data));
		    })
		//	document.location.href = '/release/detail/?release='+path
*/
	    })
})
