$(document).ready(function() {

    var progressHandlingFunction = function(){}


    
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
		     'create_actions':'yes'
//		     'create_builder':upload_variable_builder_builder()
		    })
	.select(
	    function(path) {
		window.location.href = "/variables/detail/?path="+path;
	    })
    	.create(create_varfile) //upload_varfile)
//	.create(upload_varfile)
	.setup_file(setup_varfile);

			
    kolekti_browser({'root':'/sources/share/variables',
		     'parent':".browser_share",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes'//,
		     //'create_builder':upload_variable_builder_builder()
		    })
	.select(
	    function(path) {
		window.location.href = "/variables/detail/?path="+path;
	    }
	)
	.create(create_varfile) //upload_varfile)
	.setup_file(setup_varfile);

    $('.browser_share').on('click',".upload-varfile", upload_varfile_form)
    $('.browser_lang' ).on('click',".upload-varfile", upload_varfile_form)
    $('.doimport').on('click', function(e) {
	upload_varfile()
	$('#uploadmodal').modal('hide');
    });

    
});
