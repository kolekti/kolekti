$(document).ready(function() {

    var progressHandlingFunction = function(){}

    var upload_varfile = function(browser, folder, update_function) {
	var thisform = browser.find('form.upload_form');
        var formData = new FormData(thisform[0]);
        $.ajax({
            url: '/variables/upload',  //server script to process data
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
                alert("Erreur lors du transfert");
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
		['Transférer un fichier de variables ods : ',
		 $('<form>', {'class':"upload_form",
			      'enctype':"multipart/form-data",
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


    var setup_varfile = function(browser, file_element, dir, filename){
	$(file_element).find('.kolekti-browser-item-action').append(
	    $('<a>', {'href':"/variables/ods?path="+dir+'/'+filename,
		      'class':'btn btn-xs btn-primary',
		      'html':[
		      $('<span>', {'class':"glyphicon glyphicon-download-alt",
				   'aria-hidden':"true"}),
		      $('<span>', {'class':'label ',
				   'html':'ods'
				  })]
		     }));
				   
    };

    
    $('#btn_var_lang').change(function(e) {
	$('#browser_lang').collapse('show');
	$('#browser_share').collapse('hide');
    });

    $('#btn_var_share').change(function(e) {
	$('#browser_lang').collapse('hide');
	$('#browser_share').collapse('show');
    });


    kolekti_browser({'root':'/sources/'+kolekti.lang+'/variables',
		     'parent':".browser_lang",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes',
		     'create_builder':upload_builder_builder('/sources/'+kolekti.lang+'/variables')
		    })
	.select(
	    function(path) {
		$.get('/variable/details?path='+path)
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
	.create(upload_varfile)
	.setup_file(setup_varfile);

			
    kolekti_browser({'root':'/sources/share/variables',
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
		$.get('/varaibles/edit?path='+path)
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
	.create(upload_varfile)
	.setup_file(setup_varfile);
    
    
});
