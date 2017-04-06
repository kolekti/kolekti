


var update_documents = function(project, release, lang, container) {
    
	$.getJSON('/translator/'+project+'/documents/?release=/releases/'+release + "&lang=" + lang)
	    .success(function(data) {
		console.log(data)
		var refresh = false;
		container.html($('<ul>', {
		    "class" : "list-group",
		    "html":$.map(data, function(v) {
			
			if (v[2]) 
			    return $('<li>', {
				"class":"list-group-item",
				"html":[v[0],
					' [',
					lang,
					'] ',
					$('<a>',{
					    'href':'/translator/' + project +'/'+ v[1],
					    "target":"_documents",
					    'html':$('<i>',{'class':'fa fa-file-pdf-o'})
					}),
				       ]
			    })
			else {
			    refresh = true;
			    return $('<li>', {
				"class":"list-group-item",
				"html":v[0]
			    })
			}
		    })
		}))

                container.find('ul').prepend([
		    $('<li>', {
			'class':'list-group-item sources',
			'html':$('<button>', {
			    'class':'btn btn-small btn-primary sources',
                            "data-toggle":"modal",
                            "data-target":"#downloadModal",
			    'html':[$('<i>',{'class':'fa fa-download'}),' Download sources']})
		    }),
                ])
                    // some documents could not be generated or are missing, display Generate documents command
		refresh && container.find('ul').append([
		    $('<li>', {
			'class':'list-group-item refresh',
			'html':$('<button>', {
			    'class':'btn btn-small btn-primary republish',
			    'html':[$('<i>',{'class':'fa fa-refresh'}),' Generate documents']})
		    }),
		
		    $('<li>', {
			'class':'list-group-item hidden processing',
			'html':$('<div>', {
			    'class':'alert alert-warning',
			    'html':[$('<i>',{'class':'fa fa-refresh fa-spin'}),' Creating documents...']})
		    })
		])

		// if no refresh required, display command to commit this language

		refresh || container.find('ul').append([
		    $('<li>', {
			'class':'list-group-item upload',
			'html':[
                            $('<button>', {
			        'class':'btn btn-small btn-primary upload',
                                "data-toggle":"modal",
                                "data-target":"#uploadModal",
			        'html':[$('<i>',{'class':'fa fa-upload'}),' Upload translation']}),
                            "&nbsp;",
                            $('<button>', {
			        'class':'btn btn-small btn-success commit',
			        'html':[$('<i>',{'class':'fa fa-ok'}),' Validate this language']})
                        ]
                    }),
		    $('<li>', {
			'class':'list-group-item hidden processing-commit',
			'html':$('<div>', {
			    'class':'alert alert-warning',
			    'html':[$('<i>',{'class':'fa fa-refresh fa-spin'}),' Processing...']})
		    })
		])
	    })
};



var update_releases_langs = function(release) {
    var sourcelang,
	releasepath = release.data('release'),
	project = release.data('project'),
	statecell = release.find('.kolekti-release-langs'),
	documentcell = release.find('.kolekti-release-documents');
    statecell.html("")
    documentcell.html("")
    console.log("getting release langs. " + releasepath)
    $.getJSON('/translator/'+project+'/release/states/?release=/releases/'+releasepath)
	.success(function(data) {
	    //		console.log(data)
	    $.each(data, function(index,item) {
		var i = item[0]
		var v = item[1]
		//		    console.log(i,v,this)
		if (v) {
		    statecell.append($('<span>',{
			"class":"langstate lg-"+i+" "+v+ ((v == "sourcelang")?" active":""),
			"html":$('<a>',{
			    "class":"releaselang",
			    "href":"#",
			    "data-lang":i,
			    "data-project":project,
			    "data-release":releasepath,
			    "html":i
			})
		    }))
		    if (v == 'sourcelang') {
			//			    console.log(i)
			sourcelang = i
			release.data('sourcelang', i)
                        release.data('lang', i)
			release.attr('data-lang', i)
			update_documents(project, releasepath, i, documentcell)
		    }
		} else {
                    statecell.append($('<span>',{
			"class":"langstate lg-"+i+" nostate",
			"html":$('<a>',{
			    "class":"releaselang",
			    "href":"#",
			    "data-lang":i,
			    "data-project":project,
			    "data-release":releasepath,
			    "html":i
			})
		    }))
                }
                statecell.find('.sourcelang').addClass('active')
	    });
	})
};


$(function() {
    
    $('.release').each(function(){
	update_releases_langs($(this))
    });

    $('body').on('click','.releaselang', function() {
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
	var release = $(this).closest('.release').data('release')
	var project = $(this).closest('.release').data('project')
	var documentcell = $(this).closest('.release').find('.kolekti-release-documents')
	var lang = $(this).closest('.release').data('lang')
	$(this).closest('.release').find('.processing').removeClass('hidden')
	$(this).closest('.release').find('.refresh').addClass('hidden')
	$.get('/translator/'+project+'/publish/?release=/releases/'+release  + "&lang=" + lang)
	    .success(function(data) {
		update_documents(project, release, lang, documentcell)
	    })
	    .always(function() {
		$(this).closest('.release').find('.refresh').removeClass('hidden')
		$(this).closest('.release').find('.processing').addClass('hidden')
	    })		
    })

    $('body').on('click','.commit', function() {
	var release = $(this).closest('.release').data('release')
	var project = $(this).closest('.release').data('project')
	var documentcell = $(this).closest('.release').find('.kolekti-release-documents')
	var lang = $(this).closest('.release').data('lang')
	$(this).closest('.release').find('.processing-commit').removeClass('hidden')
	$(this).closest('.release').find('.commit').addClass('hidden')
	$.post('/translator/'+project+'/' + release + '/' + lang +'/commit/')
	    .success(function(data) {
		update_documents(project, release, lang, documentcell)
	    })
	    .always(function() {
		$(this).closest('.release').find('.commit').removeClass('hidden')
		$(this).closest('.release').find('.processing-commit').addClass('hidden')
	    })		
    })

    $('#downloadModal,#uploadModal').on('show.bs.modal', function (event) {
	var button = $(event.relatedTarget) // Button that triggered the modal
        var release = $(button).closest('.release')
        var source_assembly_url = $(release).data('source-assembly-url')
        var source_zip_url = $(release).data('source-zip-url')
        var upload_url = $(release).data('upload-url')
        var sourcelang = $(release).data('sourcelang')
        var lang = $(release).data('lang')
        var modal = $(this)
        modal.find('.langtext').text(lang)
        modal.find('.langinput').attr('value',lang)
        modal.find('.sourcelangtext').text(sourcelang)
        modal.find('.link-source.source.zip').attr('href', source_zip_url + "?lang=" + sourcelang)
        modal.find('.link-source.source.assembly').attr('href', source_assembly_url + "?lang=" + sourcelang)
        modal.find('.link-source.current.zip').attr('href', source_zip_url + "?lang=" + lang)
        modal.find('.link-source.current.assembly').attr('href', source_assembly_url + "?lang=" + lang)
        modal.find('form.form-upload-translation').attr('action', upload_url) 
    })
})
