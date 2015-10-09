$(document).ready(function() {
    
    $('#btn_img_lang').change(function(e) {
	$('#browser_lang').collapse('show');
	$('#browser_share').collapse('hide');
    });

    $('#btn_img_share').change(function(e) {
	$('#browser_lang').collapse('hide');
	$('#browser_share').collapse('show');
    });


    kolekti_browser({'root':'/sources/'+kolekti.lang+'/pictures',
		     'parent':".browser_lang",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes',
		     'create_builder':upload_image_builder_builder()
		    })
	.select(
	    function(path) {
		$.get('/images/details?path='+path)
		    .done(
			function(data) {
/*
			    $('.modal-title').html(displayname(path));
			    $('.modal-body').html(data);
			    $('.modal').modal();
*/
			    $('#preview').html([
				$('<h4>',{'html':displayname(path)}),
				data
			    ]);
			    $('#preview img').attr('src',path);

			}
		    )
	    })
	.create(upload_image)


			
    kolekti_browser({'root':'/sources/share/pictures',
		     'parent':".browser_share",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes',
		     'create_builder':upload_image_builder_builder()
		    })
	.select(
	    function(path) {
		$.get('/images/details?path='+path)
		    .done(
			function(data) {
/*
			    $('.modal-title').html(displayname(path));
			    $('.modal-body').html(data);
			    $('.modal').modal();
*/
			    $('#preview').html([
				$('<h4>',{'html':displayname(path)}),
				data
			    ]);
			}
		    )
	    }
	)
	.create(upload_image);

    
});
