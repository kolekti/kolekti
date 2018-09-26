
progressHandlingFunction = function(){}

var create_varfile = function(browser, folder, update_function) {
    var filename = $(browser).find('#new_name').val();
    var path = folder + filename;
//    console.log(path)
    var lang = path.split('/')[2]
    var variable_path = path.split('/').splice(4). join('/')
    
    $.post(
	    Urls.kolekti_variable_create(kolekti.project, lang, variable_path)
    ).done(
	    function() {
		    update_function()
	    }
	)
};


var upload_varfile_form = function(e) {
    var path = $(this).data('path');
    $('#variable_file_path').val(path)
    $('#uploadmodal').modal('show');
}

var upload_varfile = function(e) {    
    var thisform = $('form#uploadform');
    var formData = new FormData(thisform.get()[0]);
    $.ajax({
        url: Urls.kolekti_variable_upload(kolekti.project, kolekti.lang, path),
//        url: '/variables/upload',  //server script to process data
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
//	    update_function()
	},
        error: errorHandler = function(jqXHR,textStatus,errorThrown) {
//	    console.log(textStatus);
//	    console.log(errorThrown);
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

var upload_variable_builder_builder = function() {
    return upload_builder = function(e, path) {
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


var setup_varfile = function(browser, file_element, path, filename){
//    console.log(path.split('/'), filename)
    var lang = path.split('/')[2]
    var variable_path = path.split('/').splice(4).join('/') + filename

    $(file_element).find('.kolekti-browser-item-action').append(
	[
	    $('<a>', {'href':Urls.kolekti_variable_ods(kolekti.project, lang, variable_path),
		  'title':'générer fichier ods',
		  'class':'btn btn-xs btn-default',
		  'html':[
		      $('<span>', {'class':"glyphicon glyphicon-export",
				   'aria-hidden':"true"}),
		      $('<span>', {
				   'html':' exporter ods'
				  })]
		 }),
	    "&nbsp;",
	    $('<a>', {'href':"#",
		      'title':'dépposer fichier ods',
		      'data-path':path + filename,
		      'class':'btn btn-xs btn-default upload-varfile',
		      'html':[
			  $('<span>', {'class':"glyphicon glyphicon-import",
				       'aria-hidden':"true"}),
			  $('<span>', {
				       'html':' importer ods'
				      })]
		     })
	]
	);
    
};
