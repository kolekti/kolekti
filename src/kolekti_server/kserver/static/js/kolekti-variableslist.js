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

    var path = $('.browser').data('browserpath')
    kolekti_browser({'root':'/sources/'+kolekti.lang+'/variables',
                     'path':path,
		     'parent':".browser",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes',
		     'create_actions':'yes'
		    })
	.select(
	    function(path) {
                var variable_path = path.replace('/' + kolekti.project + '/sources/'+kolekti.lang+'/variables/','')
		document.location.href = Urls.kolekti_variable_details(kolekti.project, kolekti.lang, variable_path)
	    })
    	.create(create_varfile) 
	.setup_file(setup_varfile);


    $('.browser_share').on('click',".upload-varfile", upload_varfile_form)
    $('.browser_lang' ).on('click',".upload-varfile", upload_varfile_form)
    $('.doimport').on('click', function(e) {
	upload_varfile()
	$('#uploadmodal').modal('hide');
    });

    
});
