$(document).ready(function() {


    // drag and drop files
    var parent = $('.release')

    $(parent).on('dragenter', '.panel-upload', function() {
        $(this).addClass('panel-danger');
	$(this).addClass('drop');
        return false;
    });
	
    $(parent).on('dragover', '.panel-upload', function(e){
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('panel-danger');
	$(this).addClass('drop');
	return false;
    });
    
    $(parent).on('dragleave', '.panel-upload', function(e) {
        e.preventDefault();
        e.stopPropagation();
	$(this).removeClass('panel-danger');
	$(this).removeClass('drop');
        return false;
    });
	
    $(parent).on('drop', '.panel-upload', function(e) {
	var release_elt = $(this).closer('.release');
        if(e.originalEvent.dataTransfer){
	    if(e.originalEvent.dataTransfer.files.length) {
                // Stop the propagation of the event
                e.preventDefault();
                e.stopPropagation();
		$(this).removeClass('panel-danger');		
		$(this).removeClass('drop');
                // Main function to upload
                upload_translation(release_elt, e.originalEvent.dataTransfer.files);
            }
	}
        else {
	    $(this).removeClass('drop');
	    $(this).removeClass('panel-danger');		
        }
        return false;
    });

    $('.upload-status-close').click(function() {
	var release_elt = $(this).closest('.release')
	$(release_elt).find('.form-upload-translation').removeClass('hidden')
	$(release_elt).find('.upload-error').addClass('hidden')
	$(release_elt).find('.upload-success').addClass('hidden')
    })
    
    var update = function(release_elt, statusdata, lang) {
	console.log('update')
	console.log(statusdata)
	if (statusdata.status == "error") {
	    $(release_elt).find('.form-upload-translation').addClass('hidden')
	    $(release_elt).find('.upload-error').removeClass('hidden')
	    $(release_elt).find('.upload-error .alert-content').html(statusdata.message)
	} else if (statusdata.status == "success") {
	    $(release_elt).find('.form-upload-translation').addClass('hidden')
	    $(release_elt).find('.upload-success').removeClass('hidden')
	    $(release_elt).find('.upload-success .alert-content').html(statusdata.message)
            republish_documents(release_elt, {
                'always': function(){
                    update_releases_langs(release_elt, lang)
                }
	    })
	}
	
    }
    

    $("form.form-upload-translation").submit(function(e) {
	console.log('upload')
	e.preventDefault();
        var release=$(this).data('release');
        var project=$(this).data('project');
	var release_elt=$('.release').filter(function(i,e) {
            return $(e).data('project')==project && $(e).data('release')==release
        }).first();
        console.log('release elt', release_elt)
	var formUrl = $(this).attr('action');
	var formData = new FormData($(this)[0]);
        $('#uploadModal').modal('hide')
	$(release_elt).find('.processing-upload').removeClass('hidden')
	$.ajax({
	    url: formUrl,
	    type: 'POST',
	    data: formData,
	    async: true,
	    cache: false,
	    contentType: false,
	    processData: false
	}).success(function (data) {
	    console.log('success')
	    update(release_elt, JSON.parse(data),formData.get('lang'))
	}).error(function(x,e) {
	    console.log('rror')
	    console.log(e)
	}).always(function(){
	    console.log('always')	
	    $(release_elt).find('.processing-upload').addClass('hidden')
	});
	
    })
})
    

		 
