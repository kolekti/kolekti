
progressHandlingFunction = function(){}

var create_varfile = function(browser, folder, update_function) {
    var filename = $(browser).find('#new_name').val();
    $.post('/variables/create/',
	   {
	       'path': folder + "/" + filename
	   })
	.done(
	    function(topicpath) {
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
//	    update_function()
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


var setup_varfile = function(browser, file_element, dir, filename){
    $(file_element).find('.kolekti-browser-item-action').append(
	[
	$('<a>', {'href':"/variables/ods?path="+dir+'/'+filename,
		  'title':'générer fichier ods',
		  'class':'btn btn-xs btn-primary',
		  'html':[
		      $('<span>', {'class':"glyphicon glyphicon-export",
				   'aria-hidden':"true"}),
		      $('<span>', {'class':'label ',
				   'html':'exporter ods'
				  })]
		 }),
	    "&nbsp;",
	    $('<a>', {'href':"#",
		      'title':'dépposer fichier ods',
		      'data-path':dir+'/'+filename,
		      'class':'btn btn-xs btn-primary upload-varfile',
		      'html':[
			  $('<span>', {'class':"glyphicon glyphicon-import",
				       'aria-hidden':"true"}),
			  $('<span>', {'class':'label ',
				       'html':'importer ods'
				      })]
		     })
	]
	);
    
};
