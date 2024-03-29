
// 

var update_documents = function(project, release, lang, container, staterow ) {
    /* updates the document table for a relase, lang couple
       project : the project to which the release belongs
       release : the release to be updated
       lang :    the language to be updated
       container:the element to contain the documents (tbody) 
       staterow :the <tr> element to contain controls for all the documents in the lang
       status  : the release status for this lang (validation / publication / translation)
    */
    var time = new Date().getTime();

    // perform ajax request to get the documents statuses
	$.getJSON(
        Urls.translators_documents(project, release, lang)
	).success(function(ddata) {
       	console.log(ddata)
        console.log(container)
        console.log(staterow)
        console.log(status)
        var status = ddata['state'];
        var data = ddata['docs'];
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
            //             var row = container.find('tr.t'+index)
            if(row.find('td.lang-'+lang).length) {
                row.find('td.lang-'+lang).html(doclink)
            } else {
                row.append($('<td>', {
                    'class': 'lang-'+lang,
                    'html':doclink
                }));
            }
        });
            
        var statecell = [
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
                }).done(function(vdata){
                    vdata = JSON.parse(vdata)
                    //console.log(data)
                    window.location.reload()
                })
            }),
            (status == "translation" || status == "validation")?$('<button>', {                       
                'title':"Generate pdf ",
                        'data-lang':lang,
                'class':"btn btn-xs btn-default republish",
                'style':"margin-left:6px",
                'html': $("<i>", {
                    'class': "fa fa-refresh"
                })
            })    :""                
        ];
        
        if ($(staterow).find('th.lang-'+lang).length) {
            $(staterow).find('th.lang-'+lang).html(statecell)
        } else {
            $(staterow).append(
                $('<th>', {
                    'class':'lang-'+lang,
                    'html': statecell
                })
            )
        }
        
	})
};



var update_releases_langs = function(release) {
    //    console.log('update_releases_langs', release)
    if ($(release).data('state') == 'loaded') {
        return;
        
    }
    $(release).data('state', 'loaded')
    
    var sourcelang,
	    releasename = release.data('release'),
	    project = release.data('project'),
	    staterow = release.find('.kolekti-release-langs'),
        documentscell = release.find('.kolekti-release-documents');
    
    
    staterow.html("<td></td>")
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
                update_documents(project, releasename, i, documentscell, staterow);
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

    // displays the tables for releases
    
/*
    $('.release').each(function(){
	    update_releases_langs($(this))
    });
*/

    $('.release-collapse').on('shown.bs.collapse', function () {
	    update_releases_langs($(this).closest('.release'))
    })

    $('.sidelink').on('click', function() {
        var rerel = $(this).attr('href')
        update_releases_langs($(rerel))
        $(rerel).find('.release-collapse').collapse('show')
    })
    
    $('.upload-assembly-form').on('submit', function(e) {
        e.preventDefault()
        assembly_upload_submit()
    });
    
    var assembly_upload_submit = function() {        
        console.log("upload", this)
        
        $('#uploadStatusModal .upload-status').html('')
        $('#uploadStatusModal').modal()
        $('#uploadStatusModal .upload-progress').show()
        $('#uploadStatusModal .upload-progress .progresstxt').html("Uploading...")
        var formdata = new FormData($('.upload-assembly-form')[0])
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
            } else if (data.status == 'missing') {
                
                $('#uploadStatusModal .upload-status').html(
                    [
                        $('<div>', {
                            'class':'alert alert-warning',
                            'html':$('<div>', {
                                'class':'alert-content',
                                'html':'could not find assembly information, please fill out :'
                            })
                            
                        }),
                        $('<div>', {
                            'id':"dropdownRelease",
                            'class':"dropdown",
                            'html' :[
                                $('<button>', {
                                    'class':"btn btn-default dropdown-toggle",
                                    'type':"button",
                                    'id':"dropdownRelease",
                                    'data-toggle':"dropdown",
                                    'aria-haspopup':"true",
                                    'aria-expanded':"true",
                                    'html':[
                                        'Choose release ',
                                        $('<span>', {
                                            'class':"caret"
                                        })
                                    ]}),
                                $('<ul>', {
                                    'class':"dropdown-menu",
                                    'aria-labelledby':"dropdownRelease"
                                }),
                            ]}),
                        $('<div>', {
                            'id':"dropdownLang",
                            'class':"dropdown hidden",
                            'html' :[
                                $('<button>', {
                                    'class':"btn btn-default dropdown-toggle",
                                    'type':"button",
                                    'id':"dropdownLang",
                                    'data-toggle':"dropdown",
                                    'aria-haspopup':"true",
                                    'aria-expanded':"true",
                                    'html':[
                                        'Choose language ',
                                        $('<span>', {
                                            'class':"caret"
                                        })
                                    ]}),
                                $('<ul>', {
                                    'class':"dropdown-menu",
                                    'aria-labelledby':"dropdownLang"
                                })
                            ]}),
                        $('<div>', {
                            'id':"btnValid",
                            'class':"hidden",
                            'html' :[
                                $('<button>', {
                                    'class':"btn btn-primary",
                                    'type':"button",
                                    'html': 'Ok'
                                })
                            ]})
                    ])
                
                $('.release').each(function(){
                    $('#dropdownRelease .dropdown-menu').append(
                        $('<li><a href="#" class="dropdownReleaseItem" data-release="' + $(this).data('release') + '" data-project="' + $(this).data('project') + '">'+ $(this).data('project') + " " + $(this).data('release')+'</a></li>')
                    )
                });
                
                $('#uploadStatusModal .dropdownReleaseItem').on('click', function() {
                    var release = $(this).data('release')
                    var project = $(this).data('project')
                    
                    $.get(Urls.translators_statuses(project, release))
                        .done (function(data) {
                            $.each(data, function(i, v) {
                                if (v[1] == "translation") {
                                    console.log(v)
                                    
                                    $('#dropdownLang .dropdown-menu').append(
                                        $('<li><a href="#" class="dropdownLangItem" data-lang="' + v[0] + '">'+ v[0] +'</a></li>')
                                    )
                                }
                            });
                            $('#uploadStatusModal .dropdownLangItem').on('click', function() {
                                var language = $(this).data('lang')
                                $('#btnValid').on('click', function() {
                                    $('#id_project').val(project)
                                    $('#id_release').val(release)
                                    $('#id_lang').val(language)
                                    assembly_upload_submit()
                                })
                                $('#btnValid').removeClass('hidden')
                            })
                            $('#dropdownLang').removeClass('hidden')
                        })
                })
                
                    
                $('#uploadStatusModal .upload-progress').hide()
                
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
    }
    
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
	    var staterow = $(this).closest('.kolekti-release-langs')
	    var documentcell = $(releaseo).find('.kolekti-release-documents')
        update_documents(project, release, lang, documentcell, staterow);
	    staterow.find('span').removeClass('active')
	    staterow.find('.lg-'+lang).addClass('active')
    })
	
    $('body').on('click','.republish', function() {
        var release_elt = $(this).closest('.release');
        var project = release_elt.data('project')
        var release = release_elt.data('release')
        var lang = $(this).data('lang')
	    var staterow = $(this).closest('.kolekti-release-langs')        
        var documentcell = release_elt.find('.kolekti-release-documents')
        console.log('republish', project, release, lang, documentcell)
        $("#publishModal").modal()
        republish_documents(project, release, lang, {
            'success': function(pdata) {
                update_documents(project, release, lang, documentcell, staterow)
                $('#publishModal .publish-status').html(pdata)
                $('#publishModal .publish-status').append(
                    $('<div>', {
                        'class':'alert alert-success',
                        'html':$('<div>', {
                            'class':'alert-content',
                            'html':"publication sucessful"
                        })
                    })
                )
            },
            'always': function(data) {
                $('#publishModal .publish-progress').hide()                
            },
            'stream': function(pdata) {
                console.log(pdata)
                $('#publishModal .publish-status').html(pdata)
            },
        })
    })
    
    
    $('body').on('click','.commit', function() {
	    var release = $(this).closest('.release').data('release')
	    var project = $(this).closest('.release').data('project')
	    var documentcell = $(this).closest('.release').find('.kolekti-release-documents')
	    var staterow = $(this).closest('.kolekti-release-langs')
	    var lang = $(this).closest('.release').data('lang')
	    $(this).closest('.release').find('.processing-commit').removeClass('hidden')
	    $(this).closest('.release').find('.commit').addClass('hidden')
	    $.post(
            Urls.translators_commit_lang(project, release, lang)
        ).success(function(data) {
		    update_documents(project, release, lang, documentcell, staterow)
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
        var release_elt = $('.release[data-project="'+ project +'"][data-release="'+ release +'"]');
        var documentcell = release_elt.find('.kolekti-release-documents')
	    var staterow = release_elt.find('.kolekti-release-langs')
        $.ajax({
            url : certif_url,
            data : formdata,
            type : 'POST',
            processData: false,
            contentType: false,
        }).done(function(data){
            data = JSON.parse(data)
            console.log(data)
            if(data.status == "success") {
                alert('Translation has been validated')
                $('#upload_delivery_dialog').modal('hide')

                update_documents(project, release, lang, documentcell, staterow)
            }
                
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
	        var staterow = release_elt.find('.kolekti-release-langs')
            update_documents(project, release, lang, documentcell, staterow)
            
        })        
    })

})
