$(document).ready(function() {
    var label_state = {
        "sourcelang":"Langue source",
        "edition":"Nouvelle version",
        "translation":"Traduction en cours",
        "validation":"Validation en cours",
        "publication":"Traduction validée"
    }
    
    var url_releases = Urls.kolekti_browser_releases(kolekti.project)
    var path = $('.browser').data('browserpath')
    
    kolekti_browser({'root':'/releases',
                     'url':url_releases,
		             'parent':".browser",
		             'title':" ",
		             'titleparent':".title",
		             'mode':"selectonly",
		             'modal':"no",
		             'os_action_delete':'yes',
                     'os_action_rename':'yes'
		            })
	    .select(
	        function(path) {
                console.log(path);
                var release_path = path.replace('/releases/','')
		        document.location.href = Urls.kolekti_release_lang_detail(kolekti.project, release_path, kolekti.lang)
		        
                /*
		          $.get('/releases/detail/',{'path':path})
		          .success(function(data) {
		          $('#detail_release').html($(data));
		          })
		          //	document.location.href = '/release/detail/?release='+path
		          */
	        })
    
    
	    .setup(function(){
	        $('.kolekti-browser-release-state').each(function() {
		        var releasepath = $(this).closest('tr').data('name')
		        var statecell = $(this)
                var url_states = Urls.kolekti_release_states(kolekti.project, releasepath)
		        $.getJSON(url_states)
		            .success(function(data) {
			            $.each(data, function(index,item) {
			                var i = item[0]
			                var v = item[1]
			                if (v)
				                statecell.append($('<span>',{
				                    "class":"langstate "+v,
				                    "html":[
                                        $('<a>',{
                                            "title":label_state[v],
					                        "href":Urls.kolekti_release_lang_detail(kolekti.project, releasepath, i),
//					                        "href":"/releases/detail/?release=/releases/"+releasepath+"&lang="+i,
					                        "html":i
				                        })
                                        ,$('<span>',{
                                            "class":"releaselangback"}
                                          )]
				                }))
			            });	      
					        
		            })
	        });
	    });

    
    $('body').on('click', '.dirtoggle', function(e) {
	    e.preventDefault()
	    var toggle = $(this).closest('tr').find('.kolekti-browser-icon i.hidden');
	    toggle.removeClass('hidden');
	    if (toggle.hasClass('fa-folder-open')) {
	        $(this).closest('tr').find('.kolekti-browser-icon i.fa-folder').addClass('hidden');
	    } else {
	        $(this).closest('tr').find('.kolekti-browser-icon i.fa-folder-open').addClass('hidden');
	    }
	    var row = $(this).closest('tr')
	    while (row.length) {
	        row = row.next('.release-index');
	        if (toggle.hasClass('fa-folder-open')) {
		        row.removeClass('hidden')
	        } else {
		        row.addClass('hidden')
	        }
	    }
    });
    
})
