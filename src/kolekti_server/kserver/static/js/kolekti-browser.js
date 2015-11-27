$(document).ready(function() {
    var funcNum = $('.browserparent').data('funcnum');
    var path = $('.browserparent').data('path');

    kolekti_browser({'root':'/sources',
		     'path':path,
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
			  window.opener.CKEDITOR.tools.callFunction( funcNum, path );
			  window.close();
		      }
		  )
    ;


})
