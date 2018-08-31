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
                  var topicpath = path.replace('/' + kolekti.project + '/sources/'+kolekti.lang+'/templates/','')
		          var url= Urls.kolekti_topic_template_edit(kolekti.project, kolekti.lang, topicpath)
			      window.open(url);
		      }
		  )
    	.create(create_template);

	

})
