$(document).ready( function () {
    
	var release = $('#main').data('release')

    var relative_path = function(path) {
        var rpath =
            $.map(
                path.split('/').splice(6),
                function(e,i){
                    if (e.length) return e
                }
            ).join("/")
        console.log(rpath)
        return rpath
    }
    
    $('.btn-lang').click(function() {
	    var lang = $(this).data('lang')
	    window.location.href = Urls.kolekti_release_lang_detail(kolekti.project, release, lang)
    })
    

    
    var enable_save = function() {
	    $('#btn_save').removeClass('disabled');
	    $('#btn_save').removeClass('btn-default');
	    $('#btn_save').removeClass('hidden');
	    $('#btn_save').addClass('btn-warning');
    };

    $(window).on('beforeunload', function(e) {
	    if($('#btn_save').hasClass('btn-warning')) {
            return 'Version non enregistrée';
	    }
    });


    
    // Kolekti Release toolbar
    
    $('.nav-tabs .active .state.lead ').on('click', function() {
	    var tab = $(this).closest('a');
	    has_focus = tab.hasClass('focus');
	    $.ajax({
	        url:"/releases/focus/",
	        method:'POST',
	        data:$.param({
		        'release': $('#main').data('release'),
		        'lang'   : $('#main').data('lang'),
		        'state'  : !has_focus
	        })
	    }).done(function(data) {
	        if (data.status='OK')
	        {
		        if (has_focus)
		            tab.removeClass('focus');
		        else
		            tab.addClass('focus');
	        }
	    });
    })
    
    //chagement d'état
    
    $('.release-state').on('click', function() {
	    var lang = $(this).closest('ul').data('target-lang');
	    var oldstate = $('.btn-lang-menu-'+lang).data('state')
	    var newstate = $(this).data('state')
	    var labelstate = $(this).find('span').html()
	    $('.btn-lang-menu-'+lang).removeClass('btn-lang-menu-'+oldstate)
	    enable_save()
	    $('.btn-lang-menu-'+lang).addClass('btn-lang-menu-'+newstate)
	    $('.btn-lang-menu-'+lang).data('state',newstate);
	    $('.btn-lang-menu-'+lang+' .state').html(labelstate);
        
	    $('#main').data('state', newstate)
	    $('#main').attr('data-state', newstate)

	    $('#release_tabs .active .state-picto').removeClass('state_'+oldstate);
	    $('#release_tabs .active .state-picto').addClass('state_'+newstate);
    });


    // changement d'onglet assemblage / pictures / variables
    

    var update_lang_tabs_assembly = function() {
        $('#release_tabs a').each(function() {
            var lang = $(this).data('lang')
            if (lang != 'share')
                $(this).attr('href', Urls.kolekti_release_lang_detail(kolekti.project, release, lang));
        });
    }
    
    var show_tab_assembly = function() {
	    $('.btn-release-pane').removeClass('active')
	    $('#btn_assembly').addClass('active')
	    $('.release-panel-part').addClass('hidden')
	    $('#content_pane').removeClass('hidden')
        
    	$('#preview').parent().addClass('hidden');
        $('#release_compare').removeClass('hidden')
        $('#release_details').removeClass('hidden')
        update_lang_tabs_assembly()
    }

    $('#btn_assembly').on('click', function() {
        show_tab_assembly()
    })


    var update_lang_tabs_pictures = function(path) {
        console.log(path)
        rpath = relative_path(path)
        $('#release_tabs a').each(function() {
            var lang = $(this).data('lang')
            if (lang != 'share')
                if (rpath && rpath != "/") {
                    $(this).attr('href', Urls.kolekti_release_lang_pictures_browse(kolekti.project, release, lang, rpath));
                } else {
                    $(this).attr('href', Urls.kolekti_release_lang_pictures_browse_root(kolekti.project, release, lang));
                }
        });
    }
    
    var show_tab_pictures = function(dirpath) {
        $('.btn-release-pane').removeClass('active')
	    $('#btn_illust').addClass('active')
	    $('.release-panel-part').addClass('hidden')
	    $('#illust_pane').removeClass('hidden')

        $('#release_compare').addClass('hidden')
        $('#release_details').addClass('hidden')

        var relang = $('#main').data('lang');
        var url, browser_path;
        
        if (dirpath && dirpath != "/") {
            url = Urls.kolekti_release_lang_pictures_browse(kolekti.project, release, relang, dirpath)
            browser_path = '/releases/' + release +'/sources/'+ relang +'/pictures/' + dirpath + '/'
        } else {
            url = Urls.kolekti_release_lang_pictures_browse_root(kolekti.project, release, relang)
            browser_path = '/releases/' + release +'/sources/'+ relang +'/pictures/'
        }

		window.history.pushState(['/'], release + " pictures", url)        

	    kolekti_browser({'root':'/releases/' + release +'/sources/'+ relang +'/pictures/',
                         'path': browser_path,
			             'parent':"#illust_pane",
			             'title':" ",
			             'titleparent':".title",
			             'mode':"selectonly",
			             'modal':"no",
			             'drop_files':true,
			             'os_actions':'yes',
			             'create_actions':'yes',
			             'create_builder':upload_image_builder_builder()
			            })
	        .select(
		        function(path) {
                    console.log(path)
                    rpath = relative_path(path)
		            $.get(Urls.kolekti_release_lang_picture_details(kolekti.project, release, relang, rpath))
			            .done(
			                function(data) {
				                $('#preview').html([
				                    data
				                ]);
                                
				                $('#preview img').attr('src',Urls.kolekti_project_static(kolekti.project, path));
				                $('#preview').closest('.panel').removeClass('hidden');
			                }
			            )
		        })
	        .create(upload_image)
            .setup(
                function(_, path) {
                    update_lang_tabs_pictures(path);
                })
    

	        .browsedir(
                function(_, e, path) {
                    update_lang_tabs_pictures(path)
                })
    };
    
    $('#btn_illust').on('click', function() {
        show_tab_pictures('')
    })


    var update_lang_tabs_variables = function(path) {
        rpath = relative_path(path)
        
        $('#release_tabs a').each(function() {
            var lang = $(this).data('lang')
            if (lang != 'share')
                if (rpath && rpath != "/") {
                    $(this).attr('href', Urls.kolekti_release_lang_variables_browse(kolekti.project, release, lang, rpath));
                } else {
                    $(this).attr('href', Urls.kolekti_release_lang_variables_browse_root(kolekti.project, release, lang));
                }
        });
    }

    var show_tab_variables = function(dirpath) {
	    $('.release-panel-part').addClass('hidden')
	    $('#variables_pane').removeClass('hidden')
	    $('.btn-release-pane').removeClass('active')
	    $('#btn_variables').addClass('active')
        
        $('#preview').parent().addClass('hidden');
	    $('#release_compare').addClass('hidden')
        $('#release_details').addClass('hidden')
        
        var relang = $('#main').data('lang');

        var url, browser_path;
        
        if (dirpath && dirpath != "/") {
            url = Urls.kolekti_release_lang_variables_browse(kolekti.project, release, relang, dirpath)
            browser_path = '/releases/' + release +'/sources/'+ relang +'/variables/' + dirpath +'/'
        } else {
            url = Urls.kolekti_release_lang_variables_browse_root(kolekti.project, release, relang)
            browser_path = '/releases/' + release +'/sources/'+ relang +'/variables/' 
        }
		window.history.pushState([], release + " variables", url)
	    kolekti_browser({'root':'/releases/' + release +'/sources/'+ relang +'/variables',
                         'path': browser_path,
		                 'parent':"#variables_pane",
		                 'title':" ",
		                 'titleparent':".title",
		                 'mode':"selectonly",
		                 'modal':"no",
		                 'os_actions':'yes',
		                 'create_actions':'yes',
		                })
	        .select(
			    function(path) {
                    console.log(path)
                    rpath = relative_path(path)
                    rpath = rpath.replace(".xml","")
                    //                    Urls.kolekti_variable(kolekti.project, path)

		            window.location.href = Urls.kolekti_release_lang_variable(kolekti.project, release, relang, rpath);
                    
	            })
	        .create(create_varfile)
            .setup(
                function(_, path) {
                    console.log(dirpath)
                    console.log(path)
                    update_lang_tabs_variables(path);
                })
        
	        .setup_file(setup_varfile)
        	.browsedir(
                function(_, e, path) {
                    console.log(path)
                    update_lang_tabs_variables(path);
                })
    };

    $('#btn_variables').on('click', function() {
        show_tab_variables('')
    });

    // activate default pane
    var active_tab = $('#main').data('active');
    
    switch(active_tab){
    case 'assembly':
        show_tab_assembly()
        break;
    case 'variables':
        var path = $('#main').data('path')
        
        if (!path) path=""
        show_tab_variables(path)
        break;
    case 'pictures':
        var path = $('#main').data('path')
        if (!path) path=""
        show_tab_pictures(path)
        break;
    }

    var do_save = function() {
	    var state = $('#main').data('state');
	    var lang = $('#main').data('lang');

	    $.ajax({
	        url:Urls.kolekti_release_lang_state(kolekti.project, release, lang),
	        method:'POST',
	        data:$.param({
		        'state' :  $('#main').data('state')
	        })
            
	    }).done(function(data) {
	        $('#btn_save').addClass('disabled');
	        $('#btn_save').addClass('btn-default');
	        $('#btn_save').removeClass('btn-warning');
	        kolekti_recent(displayname($('#main').data('release')),
                           'version',
                           Urls.kolekti_release_lang_detail(kolekti.project, $('#main').data('release'), $('#main').data('lang')))
	    });
    }

    $('#btn_save').on('click', function() {
	    if ($('#main').data('state') == "publication" && $('#main').data('valid-actions') == "yes") {
	        confirm_valid_actions();
	    } else {
	        do_save();
	    }
    })

    var get_publish_languages = function(all_languages) {
	    if (all_languages) {
	        var langs = []
	        $('#release_tabs a').each( function() {
		        if ($(this).data('state') != "unknown")
		            langs.push($(this).data('lang'));
	        });
	        return langs;
	    } else {
	        return [ $('#release_tabs .active a').first().data('lang') ]
	    }
    }

    $('.upload_form').on('submit', function(e) {
	    kolekti_recent(displayname(release), 'version',
                       Urls.kolekti_release_lang_detail(kolekti.project, release, lang)
                      )
    })


    /*
      $('#release_tabs a').click(function (e) {

      e.preventDefault()
      var lang  = $(this).data('lang');
      var state = $(this).data('state');
      if (state != "unknown") {
      $('#main').data('lang', lang)
      load_assembly();
      $('#panel_download').show()
      } else {
      $('#panel_download').hide()
      }
      })
    */

    // content loading function
    
    var load_assembly = function() {
        var lang = $('#main').data('lang');
        var status = $('#main').data('state');
	    $.get(Urls.kolekti_release_lang_assembly(kolekti.project, release, lang))
	        .done(function(data) {
	            $('#content_pane').html(data)
                $('.topic').each(function() {
                    if ($(this).attr('id')) {
                        $(this).find('.edit_topic_release').closest('li').removeClass('disabled')
                    } else {
                        $(this).find('.edit_topic_release').closest('li').addClass('disabled')
                    }
                    if (status == "sourcelang") {
                        $(this).find('.compare_topic_source').closest('li').removeClass('disabled')
                    } else {
                        $(this).find('.compare_topic_source').closest('li').addClass('disabled')
                    }
                })
	                })
        
    }

    load_assembly();

    var load_publications = function() {
        var lang = $('#main').data('lang');
        $.get(Urls.kolekti_release_lang_publications(kolekti.project, release, lang))
	        .done(function(data) {
	            $('#release_publications').html(data)
	        })
    }    
    load_publications();


    // supression langue
    
    $('#suppr_lang').on('click', function() {
	    var lang = get_publish_languages(false)[0]
	    var url= Urls.kolekti_release_lang_delete(kolekti.project, release, lang)
	    if(confirm('Voulez vous réellement supprimer cette langue ?')) {
	        $.ajax({
		        url:url,
		        type:'POST',
	        }).done(function(data) {
		        window.location.href = Urls.kolekti_release_lang_detail(kolekti.project, release, lang)
	        })
        }
    });

    // publication button

    $('.btn_publish').on('click', function() {

	    var alllang = ($(this).attr('id') == "btn_publish_all")
	    var lang = get_publish_languages(alllang)[0];
        //	var lang = get_publish_languages(false)[0]
	    var url = Urls.kolekti_release_lang_publish(kolekti.project, release, lang)

	    $('#main_modal .modal-body').html('<div id="pubresult"></div>');
	    $('#main_modal .modal-title').html('Publication');
	    $('#main_modal .modal-footer').html(
	        $('<button>', {
		        'class':'btn btn-default',
		        'type':'button',
		        'html':'Fermer'
	        }
	         ).on('click',function() {
		         $('.modal').modal('hide')
	         })
	    );
	    $('#main_modal .modal-footer').hide();
	    $('#main_modal .modal').modal({backdrop: "static"});
	    $('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Publication de la version</h4></div><div class="panel-body"><div class="progress" id="pub_progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Publication in progress</span></div></div><div id="pub_results"></div><div id="pub_end" class="alert alert-info" role="alert">Publication terminée</div></div></div>').appendTo($('#pubresult'));
	    //params = get_publish_params(job)

	    $('#pub_end').hide();
	    
	    var params = {}
	    params['release']=release;
	    var alllang = ($(this).attr('id') == "btn_publish_all")
	    params['langs']= get_publish_languages(alllang);
        params['profiles'] = [];
        $('.kolekti-activate-profile').each(function() {
            if ($(this).data('active') == 'yes')
                params['profiles'].push($(this).data('profile'))
        });
        
        params['outputs'] = [];
        $('.kolekti-activate-output').each(function() {
            if ($(this).data('active') == 'yes')
                params['outputs'] .push($(this).data('output'))
        });


        
	    var streamcallback = function(data) {
	        $("#pub_results").html(data);
	    }

	    $.ajaxPrefilter("html streamed", function(){return "streamed"});
	    streamedTransport(streamcallback);
	    $.ajax({
	        url:url,
	        type:'POST',
	        data:params,
	        dataType:"streamed",
	        beforeSend:function(xhr, settings) {
		        ajaxBeforeSend(xhr, settings);
		        settings.xhr.onreadystatechange=function(){
		            console.log(xhr.responseText);
		        }
	        }
	    }).done(function(data) {
	        $("#pub_results").html(data);
	    }).fail(function(jqXHR, textStatus, errorThrown) {
	        $('#pub_results').html([
		        $('<div>',{'class':"alert alert-danger",
			               'html':[$('<h5>',{'html':"Erreur"}),
				                   $('<p>',{'html':"Une erreur inattendue est survenue lors de la publication"})
				                   
				                  ]}),
		        $('<a>',{
		            'class':"btn btn-primary btn-xs",
		            'data-toggle':"collapse",
		            'href':"#collapseStacktrace",
		            'aria-expanded':"false",
		            'aria-controls':"collapseStracktrace",
		            'html':'Détails'}),
		        $('<div>',{'class':"well",
			               'html':[
			                   $('<p>',{'html':textStatus}),
			                   $('<p>',{'html':errorThrown}),
			                   $('<pre>',{'html':jqXHR.responseText})]
			              })
	        ]);
	    }).always(function() {
	        $('#pub_progress').remove();
	        $('#pub_end').show();
	        $('#main_modal .modal-footer').show();
	        load_publications();
	    });
    })


    // validation : dialogue confirmation
    
    var confirm_valid_actions = function() {
	    $('#main_modal .modal-body').html('<div>Des actions sont requises pour la validation de cette langue, voulez vous les effectuer ?</div>');
	    $('#main_modal .modal-title').html('Validation');
	    $('#main_modal .modal-footer').html([
	        $('<button>', {
		        'class':'btn btn-default',
		        'type':'button',
		        'html':'Valider'
	        }
	         ).on('click',function() {
		         do_valid_actions();
	         }),
	        
	        $('<button>', {
		        'class':'btn btn-default',
		        'type':'button',
		        'html':'Annuler'
	        }
	         ).on('click',function() {
		         $('#main_modal .modal').modal('hide')
	         })
	    ]
	                                       );
	    $('#main_modal .modal').on('hidden.bs.modal', function (e) {
	    });
	    $('#main_modal .modal').modal({backdrop: "static"})
	    
    }

    // validation : actions
    
    var do_valid_actions = function() {
	    var alllang = ($(this).attr('id') == "btn_publish_all")
	    var lang= get_publish_languages(alllang);
	    var url= Urls.kolekti_release_lang_validate(kolekti.project, release, lang)

	    $('#main_modal .modal-body').html('<div id="pubresult"></div>');
	    $('#main_modal .modal-title').html('Validation');
	    $('#main_modal .modal-footer').html(
	        $('<button>', {
		        'class':'btn btn-default',
		        'type':'button',
		        'html':'Fermer'
	        }
	         ).on('click',function() {
		         $('#main_modal .modal').modal('hide')
	         })
	    );

	    $('#main_modal .modal-footer button').hide();
	    $('#main_modal .modal').modal({backdrop: "static"});
	    $('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Validation de la version</h4></div><div class="panel-body"><div class="progress" id="pub_progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Actions de validation en cours</span></div></div><div id="pub_results"></div><div id="pub_end" class="alert alert-info" role="alert">Actions de validation effectuées</div></div></div>').appendTo($('#pubresult'));
	    
	    //params = get_publish_params(job)

	    $('#pub_end').hide();
	    
	    var params = {}
	    params['release']=release;
	    var streamcallback = function(data) {
	        $("#pub_results").html(data);
	    }
	    
	    $.ajaxPrefilter("html streamed", function(){return "streamed"});
	    streamedTransport(streamcallback);
	    $.ajax({
	        url:url,
	        type:'POST',
	        data:params,
	        dataType:"streamed",
	        beforeSend:function(xhr, settings) {
		        ajaxBeforeSend(xhr, settings);
		        settings.xhr.onreadystatechange=function(){
		            console.log(xhr.responseText);
		        }
	        }
	    }).done(function(data) {
	        $("#pub_results").html(data);
	        do_save();
	    }).fail(function(jqXHR, textStatus, errorThrown) {
	        $('#pub_results').html([
		        $('<div>',{'class':"alert alert-danger",
			               'html':[$('<h5>',{'html':"Erreur"}),
				                   $('<p>',{'html':"Une erreur inattendue est survenue lors d'une action de validation"})
				                   
				                  ]}),
		        $('<a>',{
		            'class':"btn btn-primary btn-xs",
		            'data-toggle':"collapse",
		            'href':"#collapseStacktrace",
		            'aria-expanded':"false",
		            'aria-controls':"collapseStracktrace",
		            'html':'Détails'}),
		        $('<div>',{'class':"well",
			               'html':[
			                   $('<p>',{'html':textStatus}),
			                   $('<p>',{'html':errorThrown}),
			                   $('<pre>',{'html':jqXHR.responseText})]
			              })
	        ]);
	    }).always(function() {
	        $('#pub_progress').remove();
	        $('#pub_end').show();
	        $('#main_modal .modal-footer button').show();
	        
	    });
    }

    // update release

    $('#btn_update').on('click', function() {
	    
    })

    // variables import

    $('#variables_pane').on('click',".upload-varfile", upload_varfile_form)
    $('.doimport').on('click', function(e) {
	    upload_varfile()
	    $('#uploadmodal').modal('hide');
    });



    // select configuration : user select profiles, scripts
    var toggle_activate =  function() {
        if($(this).data('active')=='yes') {
            $(this).data('active','no')
            $(this).find('.text-success').addClass('hidden')
            $(this).find('.text-danger').removeClass('hidden')
        } else {
            $(this).data('active','yes')
            $(this).find('.text-success').removeClass('hidden')
            $(this).find('.text-danger').addClass('hidden')
        }
    };

    $('.kolekti-activate-output').on("click", toggle_activate);
    $('.kolekti-activate-profile').on("click", toggle_activate);
})
