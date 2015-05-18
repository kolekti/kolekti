$(document).ready(function() {
    
    kolekti_browser({'root':'/sources/'+kolekti.lang+'/topics',
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
			  window.open('/topics/edit/?topic='+path);
		      }
		  )
		  .create(create_topic);

    $('.browserparent').on('click', '.tpl-item',function(e){
	e.preventDefault();
	$('.label-tpl').html($(this).data('tpl'))
	$('.label-tpl').data('tpl',$(this).data('tpl'));
    })
	

})
