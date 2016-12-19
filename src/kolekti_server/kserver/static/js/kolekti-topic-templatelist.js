$(document).ready(function() {
    
    kolekti_browser({'root':'/sources/'+kolekti.lang+'/templates',
		     'parent':".browserparent",
		     'buttonsparent':".buttons",
		     'mode':"create",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes'
//		     'create_builder':create_builder
		    })
		  .select(
		      function(path) {
			  window.open('/topics/edit/?topic='+encodeURI(path));
		      }
		  );

	

})
