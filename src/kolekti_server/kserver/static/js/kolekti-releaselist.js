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

	var fmtdate = function(d) {
		var mm = d.getMonth() + 1; // getMonth() is zero-based
		var dd = d.getDate();
		
		return [d.getFullYear(),
			    (mm>9 ? '' : '0') + mm,
			    (dd>9 ? '' : '0') + dd
		       ].join('');
	};
    
    
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
                var release_path = path.replace('/releases/','')
		        document.location.href = Urls.kolekti_release_lang_detail(kolekti.project, release_path, kolekti.lang)
	        })
    
    
	    .setup(function(parent){
            // renaming
            $(parent).find('.kolekti-action-rename').off('click')
            
            $(parent).find('.kolekti-action-rename').click(function(e){

                var releasepath = $(this).closest('tr').data('name')
                var i = releasepath.lastIndexOf('_')
                var min = releasepath.substring(i+1);
                var maj = releasepath.substring(0, i);
                
                $('#modal_release_rename').data('release', releasepath)
                $("#modal_release_rename_index").val(min)
                $('#modal_release_rename').find('.error').html('')
                $("#modal_release_rename").modal()
                $("#modal_release_rename_majorname").val(maj)

                // update major name select menu
                $('#modal_release_rename_menu_majorname').html()
                $('.kolekti-browser-name .dirtoggle').each(function(){
                    var item = $('<li>',{
                        'html':$('<a>',{
                            'href':"#",
                            'html': $(this).html()
                        })
                    })
                    item.on('click', function() {
                        $('#modal_release_rename_majorname').val($(this).find("a").html())
                    })
                    item.appendTo('#modal_release_rename_menu_majorname')
                })
            });

            //modal_release_rename_menu_majornameœ
            
            // update release state
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
            init_view();
	    });

    var toggle_status = sessionStorage.getItem('kolekti_version_browser_state');
    if (toggle_status == null)
	    sessionStorage.setItem('kolekti_version_browser_state',JSON.stringify([]))
    
    var init_view = function(e) {
	    var toggle_status = JSON.parse(sessionStorage.getItem('kolekti_version_browser_state'));
        $.each(toggle_status, function(i, v) {
            var row = $('tr[data-name="' + v + '"]')
            row.find('.kolekti-browser-icon i.fa-folder').addClass('hidden');
            row.find('.kolekti-browser-icon i.fa-folder-open').removeClass('hidden');
	        while (row.length) {
	            row = row.next('.release-index');
		        row.removeClass('hidden')
	        }
        });
    };
    
    $('body').on('click', '.dirtoggle', function(e) {
        var toggle_status = JSON.parse(sessionStorage.getItem('kolekti_version_browser_state'));
	    var row = $(this).closest('tr')
        var name = row.data('name')
	    var toggle = row.find('.kolekti-browser-icon i.hidden');
	    toggle.removeClass('hidden');
	    if (toggle.hasClass('fa-folder-open')) {
	        row.find('.kolekti-browser-icon i.fa-folder').addClass('hidden');
            toggle_status.push(name)
	    } else {
	        row.find('.kolekti-browser-icon i.fa-folder-open').addClass('hidden');
            toggle_status.removevalue(name)
	    }
        sessionStorage.setItem('kolekti_version_browser_state',JSON.stringify(toggle_status))
        
	    while (row.length) {
	        row = row.next('.release-index');
	        if (toggle.hasClass('fa-folder-open')) {
		        row.removeClass('hidden')
	        } else {
		        row.addClass('hidden')
	        }
	    }
    });


    // directory toggle state 
    

    $('body').on('click', '.kolekti-action-update', function(e) {
		var releasepath = $(this).closest('tr').data('name')
        var i = releasepath.lastIndexOf('_')
        var min =releasepath.substring(i+1);
        var maj =releasepath.substring(0, i);
        
        $('#modal_release_update').data('release', releasepath)
        $("#modal_release_new_index").val(fmtdate(new Date()));
        $('#modal_release_update').find('.error').html('')
        $("#modal_release_update").modal()
        $("#modal_release_update .majorname").each(function() {
            $(this).html(maj)
        });
        $("#modal_release_update .minorname").each(function() {
            $(this).html(min)
        });
    })
    
    $('body').on('click', '#modal_release_update_confirm', function(e) {
        var modal = $(this).closest('.modal')
        var release = modal.data('release')
        var index = modal.find('#modal_release_new_index').val()
        var from_sources = modal.find('#modal_release_update_sources').get(0).checked
        var options = {
            'index': index,
            'from_sources':from_sources
        }
        $.post(
	        Urls.kolekti_release_update(kolekti.project, release),
            options
        ).done(function() {
            window.location.reload();
        }).fail(function(xhr) {
            var data = JSON.parse(xhr.responseText)
            var message = data.message
            
            modal.find('.error').html(
                $('<div>', {
                    'class':"alert alert-danger alert-dismissible",
                    'role':"alert",
                    'html':[
                        $('<button>', {
                            'type':"button",
                            'class':"close",
                            'data-dismiss':"alert",
                            'aria-label':"Close",
                            'html':$('<span aria-hidden="true">&times;</span>')
                        }),
                        $('<p>',{
                            'class':"error_message"
                        })
                    ]
                })
            )
            modal.find('.error_message').html(message)
            
        })
               
    })

    
    $('body').on('click', '#modal_release_rename_confirm', function(e) {
        var modal = $(this).closest('.modal')
        var release = modal.data('release')
        var index = modal.find('#modal_release_rename_index').val()
        var majorname = modal.find('#modal_release_rename_majorname').val()
        var options = {
            'source': release,
            'name': majorname,
            'index': index,
        }
        $.post(
	        Urls.kolekti_release_rename(kolekti.project, release),
            options
        ).done(function() {
            window.location.reload();
        }).fail(function(xhr) {
            var data = JSON.parse(xhr.responseText)
            var message = data.message
            
            modal.find('.error').html(
                $('<div>', {
                    'class':"alert alert-danger alert-dismissible",
                    'role':"alert",
                    'html':[
                        $('<button>', {
                            'type':"button",
                            'class':"close",
                            'data-dismiss':"alert",
                            'aria-label':"Close",
                            'html':$('<span aria-hidden="true">&times;</span>')
                        }),
                        $('<p>',{
                            'class':"error_message"
                        })
                    ]
                })
            )
            modal.find('.error_message').html(message)
            
        })
               
    })
})
