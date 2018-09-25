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
    kolekti_browser({
        'root':'/sources/'+kolekti.lang+'/variables',
        'path':path,
		'parent':".browser",
		'title':" ",
		'titleparent':".title",
		'mode':"selectonly",
		'modal':"no",
		'os_actions':'yes',
		'create_actions':'yes'
	}).select(
	    function(path) {
            var lang = path.split('/')[3]
            var variable_path = path.split('/').splice(5). join('/')
		    document.location.href = Urls.kolekti_variable(kolekti.project, lang, variable_path)
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
