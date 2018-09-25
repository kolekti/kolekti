$(document).ready(function() {
    
    $('#btn_img_lang').change(function(e) {
	$('#browser_lang').collapse('show');
	$('#browser_share').collapse('hide');
	var path =  '/sources/'+kolekti.lang+'/pictures';
	window.history.pushState({'path':path},document.title,'?path='+path)
    });

    $('#btn_img_share').change(function(e) {
	$('#browser_lang').collapse('hide');
	$('#browser_share').collapse('show');
	var path =  '/sources/share/pictures';
	window.history.pushState({'path':'/sources/share/pictures'},document.title,'?path='+path)
    });			       

    var path = $('.browser').data('browserpath')
    console.log(path)
    kolekti_browser({'root':'/sources/'+kolekti.lang+'/pictures',
                     'path':path,
		             'parent':".browser",
		             'title':" ",
		             'titleparent':".title",
		             'mode':"selectonly",
		             'modal':"no",
		             'os_actions':'yes',
		             'drop_files':'yes',
		             'create_actions':'yes',
		             'create_builder':upload_image_builder_builder()
		            })
	.select(
	    function(path) {
            var lang = path.split('/')[3]
            var pic_path = path.split('/').splice(5). join('/')
            var url = Urls.kolekti_picture_details(kolekti.project, lang, pic_path)
		$.get(url)
		    .done(
			function(data) {
			    $('#preview').html([
				$('<h4>',{'html':displayname(path)}),
				data
			    ]);
			    $('#preview img').attr('src',path);

			}
		    )
	    })
	.create(upload_image)
	.remove(function(e, path) {
	    $('#preview').html('')
	})
    
/*
			
    kolekti_browser({'root':'/sources/share/pictures',
		     'parent':".browser_share",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'drop_files':'yes',
		     'os_actions':'yes',
		     'create_actions':'yes',
		     'create_builder':upload_image_builder_builder()
		    })
	.select(
	    function(path) {
		$.get('/images/details?path='+path)
		    .done(
			function(data) {
			    $('#preview').html([
				$('<h4>',{'html':displayname(path)}),
				data
			    ]);
			}
		    )
	    }
	)
	.create(upload_image)
    	.remove(function(e, path) {
	    $('#preview').html('')
	});
*/			      		       
    var selBrowser = function(path) {
	if (path.substring(0, 14) == '/sources/share') {
	    $('#browser_lang').collapse('hide');
	    $('#browser_share').collapse('show');
	} else {
	    $('#browser_lang').collapse('show');
	    $('#browser_share').collapse('hide');
	}
    }
			       
    var currentState = window.history.state;
    if(currentState && currentState.path) {
	selBrowser(currentState.path)
    };

    window.onpopstate = function(event) {
	if(event.state && event.state.path) {
	    selBrowser(event.state.path)
	} else {
	    selBrowser('/sources/'+kolekti.lang+'/pictures')
	}
    };			       
			       
});
