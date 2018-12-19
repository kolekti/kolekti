
// 

var update_documents = function(project, release, lang, container, statecell, status ) {
    /* updates the document table for a relase, lang couple
       project : the project to which the release belongs
       release : the release to be updated
       lang :    the language to be updated
       container:the element to contain the documents (tbody) 
       statecell:the <td/th> element to contain controls for all the documents in the lang
       status  : the release status for this lang (validation / publication / translation)
    */
    var time = new Date().getTime();

    // perform ajax request to get the documents statuses
	$.getJSON(
        Urls.translators_documents(project, release, lang)
	).success(function(data) {
       	console.log(data)
        console.log(container)
        console.log(statecell)
        console.log(status)
        
		var refresh = false;

        // if no row inserted ... create table rows
        if(container.is(':empty')) {
            $.each(data, function(index, docs) {
                container.append($('<tr>', {
                    'class':'t'+index,
                    'html':$('<th>', {
                        html:docs[0]
                    })
                }))
            });
        }
        
        var can_validate_all = (status == 'translation')
        
        $.each(data, function(index, docs) {
            var row = container.find('tr.t'+index)
            var doclink;
//            console.log(docs)
            if(!docs[3].length) can_validate_all = false
            if (docs[2]) {
                // the document [pdf...] exists on the server

                var certif_url = Urls.translators_upload_certif(project, release, lang);
                // create icon with link to the document
                doclink = [$('<a>',{
					'href':Urls.translators_static(project, release, docs[1]) +"?time=" + time,
                    'title':docs[0],
					"target":"_documents",
					'html':$('<i>',{'class':'fa fa-file-' + docs[4] + '-o'})
				}), ' ']

                // if the publication is already validated, insert check mark
                if(status == "validation" || status == "publication")
                    doclink.push(
                        $("<span>", {
                            "class":"text-success",
                            "html":$("<i>", {
                                'class': "fa fa-check"
                            })
                        }))

                // add button for validation
                if(status == "translation")
                    doclink.push(
                        $('<a>', {
                            'title':"Validate translation ",
                            'class':"btn btn-xs "+ (docs[3].length?"btn-success":"btn-default"),
                            'html': $("<i>", {
                                'class': "fa fa-check-square"
                            })
                        }).on('click', function(){
                            // update validation modal with list of signature documents
                            $('#certificates').html('<ul></ul>')
                            $.each(docs[3], function(i, doc) {
                                $('#certificates ul').append(
                                    $('<li>', {
                                        html: $("<a>", {
                                            "href": Urls.translators_static(project, docs[1] + '.cert/' + doc),
                                            'html':doc
                                        })
                                    })
                                )
                            });
                            
                            if (!docs[3].length) {
                                $('#certificates').hide()
                            } else {
                                $('#certificates').show()
                            }
                            
                            $('#upload_delivery_dialog input[name="upload_file"]').val('');
                            $('#upload_delivery_dialog input[name="path"]').val(docs[1])
                            $('#upload_delivery_dialog form').data('project', project)
                            $('#upload_delivery_dialog form').data('release', release)
                            $('#upload_delivery_dialog form').data('lang', lang)
                            $('#upload_delivery_dialog form').data('certificates', docs[3])
                            $('#upload_delivery_dialog form').attr('action', certif_url);
                            $('#upload_delivery_dialog').modal()
                            
                                        
                        })
                    );
                    
            } else {
                // the document does not exists on the browser
                doclink = $("<i>", {
                    'class': "fa fa-question"
                })
            };
            
            row.append($('<td>', {
                html:doclink
            }));
        });
            
            
        $(statecell).append(
            $('<th>',{
                'html':[
                    $('<span>', {
			            "html":lang
                    }),
                    (!can_validate_all)?"":$('<a>', {
                        'title':"Validate all documents in this language ",
                        'class':"btn btn-xs btn-default",
                        'style':"margin-left:6px",
                        'html': $("<i>", {
                            'class': "fa fa-check-square"
                        })
                    }).on('click', function(){
                        var url = Urls.translators_commit_lang(project, release, lang);
                        $.ajax({
                            url : url,
                            type : 'POST',
                            processData: false,
                            contentType: false,
                        }).done(function(data){
                            data = JSON.parse(data)
                            //console.log(data)
                            window.location.reload()
                        })
                    })
                ]
		    })
        )
        
	})
};



var update_releases_langs = function(release) {
//    console.log('update_releases_langs', release)
    var sourcelang,
	    releasename = release.data('release'),
	    project = release.data('project'),
	    statecell = release.find('.kolekti-release-langs'),
        documentscell = release.find('.kolekti-release-documents');
    
    
    statecell.html("<td></td>")
    documentscell.html("")
    $.getJSON(
        Urls.translators_statuses(project, releasename)
	).success(function(data) {
//        console.log(data)
	    $.each(data, function(index,item) {
		    var i = item[0]
		    var v = item[1]
            
		    if (v == 'sourcelang' || v == "translation" || v == "validation" || v == "publication" )
            {
                update_documents(project, releasename, i, documentscell, statecell, v);
            }
        });
	});
};
    
var republish_documents = function(project, release, lang, callbacks){
	var streamcallback = function(data) {
		//		console.log(data);
        callbacks.hasOwnProperty('stream') && callbacks['stream'](data)
	}
    
	$.ajaxPrefilter("html streamed", function(){return "streamed"});
	streamedTransport(streamcallback);
    
	$.ajax({
    	url: Urls.translators_publish(project, release, lang),
		type:'GET',
		dataType:"streamed",
    }).done(function(data) {
        callbacks.hasOwnProperty('success') && callbacks['success'](data)
	}).fail(function(x,e) {
        callbacks.hasOwnProperty('error') && callbacks['error']()
    }).always(function() {
        callbacks.hasOwnProperty('always') && callbacks['always']()
	});
    
}

$(function() {    
    $('.release').each(function(){
	    update_releases_langs($(this))
    });
    
    
    $('.upload-assembly-form').on('submit', function(e) {
        console.log("upload", this)
        e.preventDefault()
        $('#uploadStatusModal .upload-status').html('')
        $('#uploadStatusModal').modal()
        $('#uploadStatusModal .upload-progress').show()
        $('#uploadStatusModal .upload-progress .progresstxt').html("Uploading...")
        var formdata = new FormData($(this)[0])
        //        formdata.append('file', this.files[0]);
        
        $.ajax({
            url : Urls.translators_upload_assembly(),
            data : formdata,
            type : 'POST',
            processData: false,
            contentType: false,
        }).done(function(data){
            data = JSON.parse(data)
            console.log(data)
            
            if (data.status == 'success') {
                $('#uploadStatusModal .upload-status').html(
                    $('<div>', {
                        'class':'alert alert-success',
                        'html':$('<div>', {
                            'class':'alert-content',
                            'html':data.message
                        })
                    })
                )
                
                $('#uploadStatusModal .upload-progress .progresstxt').html("Publishing...")
                
                republish_documents(data.info.project, data.info.release, data.info.lang, {
                    'stream': function(pdata) {
                        console.log(pdata)
                        $('#uploadStatusModal .alert-content-stream').html(pdata)
                    },
                    'success': function(pdata) {
                        $('#uploadStatusModal .upload-progress').hide()
                        $('#uploadStatusModal .upload-status').append(
                            $('<div>', {
                                'class':'alert alert-success',
                                'html':$('<div>', {
                                    'class':'alert-content',
                                    'html':"publication sucessful"
                                })
                            })
                        )
                    }
                })
                
            } else {
                $('#uploadStatusModal .upload-progress').hide()
                $('#uploadStatusModal .upload-status').html(
                    $('<div>', {
                        'class':'alert alert-danger',
                        'html':$('<div>', {
                            'class':'alert-content',
                            'html':data.message
                        })
                    })
                )
            }
        }).error(function() {
            $('#uploadStatusModal .upload-progress').hide()
            $('#uploadStatusModal .upload-status').html(
                $('<div>', {
                    'class':'alert alert-danger',
                    'html':$('<div>', {
                        'class':'alert-content',
                        'html':'an unexpected error occured'
                    })
                })
            )
            
        }).always(function() {
            
        })
        
        return true;
    })
    
    $('#uploadStatusModal').on('hidden.bs.modal', function() {
        window.location.reload()
    })
    
    $('body').on('click','.releaselang', function(e) {
        e.preventDefault()
        e.stopPropagation()
	    var releaseo = $(this).closest('.release')
        var release = $(releaseo).data('release')
	    var project = $(releaseo).data('project')
	    var lang = $(this).data('lang')
	    $(releaseo).data('lang',lang)
	    var statecell = $(this).closest('.kolekti-release-langs')
	    var documentcell = $(releaseo).find('.kolekti-release-documents')
        update_documents(project, release, lang, documentcell)
	    statecell.find('span').removeClass('active')
	    statecell.find('.lg-'+lang).addClass('active')
    })
	
    $('body').on('click','.republish', function() {
        var release_elt = $(this).closest('.release');
        var project = release_elt.data('project')
        var release = release_elt.data('release')
        var lang = release_elt.data('lang')
        var documentcell = release_elt.find('.kolekti-release-documents')
        console.log('republish', project, release, lang, documentcell)
        republish_documents(release_elt, {
            'success': function() {
            	update_documents(project, release, lang, documentcell)
            }
        })
    })
    
    
    $('body').on('click','.commit', function() {
	    var release = $(this).closest('.release').data('release')
	    var project = $(this).closest('.release').data('project')
	    var documentcell = $(this).closest('.release').find('.kolekti-release-documents')
	    var lang = $(this).closest('.release').data('lang')
	    $(this).closest('.release').find('.processing-commit').removeClass('hidden')
	    $(this).closest('.release').find('.commit').addClass('hidden')
	    $.post(
            Urls.translators_commit_lang(project, release, lang)
        ).success(function(data) {
		    update_documents(project, release, lang, documentcell)
	    }).always(function() {
		    $(this).closest('.release').find('.commit').removeClass('hidden')
		    $(this).closest('.release').find('.processing-commit').addClass('hidden')
	    })		
    })

    $('#downloadModal, #uploadModal').on('show.bs.modal', function (event) {
	    var button = $(event.relatedTarget) // Button that triggered the modal
        var release = $(button).closest('.release')
        var source_assembly_url = $(release).data('source-assembly-url')
        var source_zip_url = $(release).data('source-zip-url')
        var upload_url = $(release).data('upload-url')
        var sourcelang = $(release).data('sourcelang')
        var lang = $(release).data('lang')
        var modal = $(this)
        //        console.log($(release).data('translated'))
        if ((lang != $(release).data('sourcelang')) && $(release).data('translated'))
            modal.find('.translations').show()
        else
            modal.find('.translations').hide()
        modal.find('form').data('release',release.data('release'))
        modal.find('form').data('project',release.data('project'))
        modal.find('.langtext').text(lang)
        modal.find('.langinput').attr('value',lang)
        modal.find('.sourcelangtext').text(sourcelang)
        modal.find('.link-source.source.zip').attr('href', source_zip_url + "?lang=" + sourcelang)
        modal.find('.link-source.source.assembly').attr('href', source_assembly_url + "?lang=" + sourcelang)
        modal.find('.link-source.current.zip').attr('href', source_zip_url + "?lang=" + lang)
        modal.find('.link-source.current.assembly').attr('href', source_assembly_url + "?lang=" + lang)
        modal.find('form.form-upload-translation').attr('action', upload_url) 
    })

    // bouton upload
    $('#upload_certificate').on('click', function() {
        $('#input_upload_certificate').click()
    })


    // validation dialog
    
    $('#validate_translation').on('click', function() {
        var project = $('#upload_delivery_dialog form').data('project');
        var release = $('#upload_delivery_dialog form').data('release');
        var lang = $('#upload_delivery_dialog form').data('lang');
        var certif_url = Urls.translators_certif(project, release, lang)
        var formdata = new FormData($('#upload_delivery_dialog form')[0])
        
        $.ajax({
            url : certif_url,
            data : formdata,
            type : 'POST',
            processData: false,
            contentType: false,
        }).done(function(data){
            data = JSON.parse(data)
            console.log(data)            
        })
    })

    
    $('#input_upload_certificate').on('change', function() {
        // envoi d'un nouveau certificat
        var formdata = new FormData($(this).closest('form')[0])
        //        formdata.append('file', this.files[0]);
        var certif_url = $(this).closest('form').attr('action');
        //        console.log(formdata)
        $.ajax({
            url : certif_url,
            data : formdata,
            type : 'POST',
            processData: false,
            contentType: false,
        }).done(function(data){
            data = JSON.parse(data)
            //  console.log(data)
            var certs = $('#upload_delivery_dialog form').data('certificates');
            var project = $('#upload_delivery_dialog form').data('project');
            var release = $('#upload_delivery_dialog form').data('release');
            var lang = $('#upload_delivery_dialog form').data('lang');
            certs.push(data.filename)
            $('#certificates ul').append(
                $('<li>', {
                    html: $("<a>", {
                        "href": Urls.translators_static(project, data.path + '.cert/' + data.filename),
                        'html':data.filename
                    })
                })
                
            )
            $('#certificates').show();
            var release_elt = $('.release[data-project="'+ project +'"][data-release="'+ release +'"]');
            var documentcell=  release_elt.find('.kolekti-release-documents')
            update_documents(project, release, lang, documentcell)
            
        })        
    })

})
