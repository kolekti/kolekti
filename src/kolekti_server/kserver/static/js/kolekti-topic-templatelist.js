$(document).ready(function() {

    var create_template = function(browser, folder, update_function) {
        var filename = $(browser).find('#new_name').val();
	    $.post(
            Urls.kolekti_topic_template_edit(kolekti.project, kolekti.lang, folder + "/" + filename)
        ).done(
		    function(templatepath) {
		        update_function()
		    }
	    )
    };

    
    kolekti_browser({'root':'/sources/'+kolekti.lang+'/templates/',
		     'parent':".browser",
		     'buttonsparent':".buttons",
		     'mode':"create",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'files'
//		     'create_builder':create_builder
		    })
		  .select(
		      function(path) {
                  var lang = path.split('/')[3]
                  var template_path = path.split('/').splice(5). join('/')
		          var url= Urls.kolekti_topic_template_edit(kolekti.project, kolekti.lang, template_path)
			      window.open(url);
		      }
		  )
    	.create(create_template);

	

})
