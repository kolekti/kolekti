$(document).ready(function() {

    var progressHandlingFunction = function(){}

    var upload_image = function(browser, folder, update_function) {
	var thisform = browser.find('form.upload_form');
        var formData = new FormData(thisform[0]);
        $.ajax({
            url: '/images/upload',  //server script to process data
            type: 'POST',
            xhr: function() {  // custom xhr
                myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){ // if upload property exists
                    myXhr.upload.addEventListener('progress', progressHandlingFunction, false); // progressbar
                }
                return myXhr;
            },
            //Ajax events
            success: function() {
		update_function()
	    },
            error: errorHandler = function(jqXHR,textStatus,errorThrown) {
		console.log(textStatus);
		console.log(errorThrown);
                alert("Erreur lors de l'ajout de l'image");
            },
            // Form data
            data: formData,
            //Options to tell JQuery not to process data or worry about content-type
            cache: false,
            contentType: false,
            processData: false
        }, 'json');
    };

    var upload_builder_builder = function(path) {
	return upload_builder = function(e) {
	    e.prepend(   
		['Transférer une image : ',
		 $('<form>', {'class':"upload_form",'enctype':"multipart/form-data",
			      "html":[$('<input>',{ 'type':"file",
						    'id':'upload_file',
						    'name':'upload_file',
						    'class':"form-control upload"
						  }),
				      $('<input>',{ 'type':"hidden",
						    'name':'path',
						    'value':path,
						  })
				     ]
			     }),
		 $('<br>')
		]);
	}
    };


    kolekti_browser({'root':'/sources/'+kolekti.lang+'/pictures',
		     'parent':".browser_lang",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes',
		     'create_builder':upload_builder_builder('/sources/'+kolekti.lang+'/pictures')
		    })
	.select(
	    function(path) {
		$.get('/images/details?path='+path)
		    .done(
			function(data) {
			    $('.modal-title').html(displayname(path));
			    $('.modal-body').html(data);
			    $('.modal').modal();
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
		     'create_builder':upload_builder_builder('/sources/share/pictures')
		    })
	.select(
	    function(path) {
		$.get('/images/details?path='+path)
		    .done(
			function(data) {
			    $('.modal-title').html(displayname(path));
			    $('.modal-body').html(data);
			    $('.modal').modal();
			}
		    )
	    }
	)
	.create(upload_image)
});