$(document).ready(function() {
    var path = $('.browserparent').data('browserpath')
    
    kolekti_browser({'root':'/sources/'+kolekti.lang+'/topics',
                     'path': path,
		     'parent':".browserparent",
		     'buttonsparent':".buttons",
		     'mode':"create",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes',
		     'create_builder':create_builder
		    })
		  .select(
		      function(path) {
<<<<<<< HEAD
                          var tocpath = path.replace('/' + kolekti.project + '/sources/'+kolekti.lang+'/topics/','')
		          var url= Urls.kolekti_topic_edit(kolekti.project, kolekti.lang, tocpath)
			  window.open(url)
=======
			  window.open('/topics/edit/?topic='+path);
>>>>>>> 80fb374eaff5d3e99cb21f3ff85631908f1b4b9a
		      }
		  )
		  .create(create_topic);

    $('.browserparent').on('click', '.tpl-item',function(e){
	e.preventDefault();
	$('.label-tpl').html($(this).data('tpl'))
	$('.label-tpl').data('tpl',$(this).data('tpl'));
    })
	

})
