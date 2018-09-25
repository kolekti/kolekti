$(document).ready(function() {
    
    var path = $('.browserparent').data('browserpath')
    
    kolekti_browser({'root':'/sources/'+kolekti.lang+'/topics/',
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
                var lang = path.split('/')[3]
                var topic_path = path.split('/').splice(5). join('/')
		        var url= Urls.kolekti_topic_edit(kolekti.project, lang, topic_path)
			    window.open(url)
		    }
		)
		.create(create_topic);

    $('.browserparent').on('click', '.tpl-item',function(e){
	    e.preventDefault();
	    $('.label-tpl').html($(this).data('tpl'))
	    $('.label-tpl').data('tpl',$(this).data('tpl'));
    })
    
})
