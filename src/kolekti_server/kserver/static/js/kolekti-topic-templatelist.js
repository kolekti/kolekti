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
                  var tocpath = path.replace('/' + kolekti.project + '/sources/'+kolekti.lang+'/topics/','')
		          var url= Urls.kolekti_topic_edit(kolekti.project, kolekti.lang, tocpath)
			      window.open(url);
		      }
		  );

	

})
