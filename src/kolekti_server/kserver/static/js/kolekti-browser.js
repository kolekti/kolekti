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
                  var project_path = '/' + path.split('/').slice(2).join('/');
			      window.opener.CKEDITOR.tools.callFunction( funcNum, project_path );
			      window.close();
		      }
		  )
    ;


})
