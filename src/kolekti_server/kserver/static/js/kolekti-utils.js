/*
  var kolekti = {
  'lang' : 'fr'
  }
*/

var kolekti_bootstrap_status = {
    "ok":"muted",
    "update":"info",
    "commit":"info",
    "merge":"warning",
    "conflict":"warning",
    "error":"warning"
}

function displayname(path) {
    var f = basename(path)
    return f.replace(/\.[^\.]+$/,'')
}

function basename(path) {
    return path.replace(/\\/g,'/').replace( /.*\//, '' );
}

function dirname(path) {
    return path.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');;
}

Array.prototype.removevalue = function() {
    var what, a = arguments, L = a.length, ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};

var xhrSuccessStatus = {
	// file protocol always yields status code 0, assume 200
	0: 200,
	// Support: IE9
	// #1450: sometimes IE returns 1223 when it should be 204
	1223: 204
}

var ajaxBeforeSend = function(xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
    settings.converters["* streamed"]=true;
} ;

$.ajaxSetup({ 
    beforeSend: ajaxBeforeSend
});


// define transport ajax function for streaming data

var streamedTransport = function(streamCallback) {
    return $.ajaxTransport("streamed", function( options, originalOptions, jqXHR ) {
	    return {
	        send: function( headers, completeCallback ) {
		        var i,
		            xhr = options.xhr();
		        
		        xhr.open(
		            options.type,
		            options.url,
		            options.async,
		            options.username,
		            options.password
		        );

		        // Apply custom fields if provided
		        if ( options.xhrFields ) {
		            for ( i in options.xhrFields ) {
			            xhr[ i ] = options.xhrFields[ i ];
		            }
		        }

		        // Override mime type if needed
		        if ( options.mimeType && xhr.overrideMimeType ) {
		            xhr.overrideMimeType( options.mimeType );
		        }

		        // X-Requested-With header
		        // For cross-domain requests, seeing as conditions for a preflight are
		        // akin to a jigsaw puzzle, we simply never set it to be sure.
		        // (it can always be set on a per-request basis or even using ajaxSetup)
		        // For same-domain requests, won't change header if already provided.
		        if ( !options.crossDomain && !headers["X-Requested-With"] ) {
		            headers["X-Requested-With"] = "XMLHttpRequest";
		        }
		        
		        // Set headers
		        for ( i in headers ) {
		            xhr.setRequestHeader( i, headers[ i ] );
		        }

		        // Callback
		        callback = function( type ) {
		            return function() {
			            if ( type === "state" ) {
			                streamCallback(xhr.responseText)
			            }
			            
			            else if ( callback ) {
			                callback = xhr.onload = xhr.onerror = null;
			                //console.log(xhr.responseText)
			                if ( type === "abort" ) {
				                xhr.abort();
			                }
			                else if ( type === "error" ) {
				                completeCallback(
				                    // file: protocol always yields status 0; see #8605, #14207
				                    xhr.status,
				                    xhr.statusText
				                );
			                } else {
				                completeCallback(
				                    xhrSuccessStatus[ xhr.status ] || xhr.status,
				                    xhr.statusText,
				                    // Support: IE9
				                    // Accessing binary-data responseText throws an exception
				                    // (#11426)
				                    typeof xhr.responseText === "string" ? {
					                    text: xhr.responseText
				                    } : undefined,
				                    xhr.getAllResponseHeaders()
				                );
			                }
			            }
		            }
		        };

		        // Listen to events
		        xhr.onload = callback();
		        xhr.onreadystatechange = callback("state");
		        xhr.onerror = callback("error");
		        
		        // Create the abort callback
		        callback = callback("abort");
		        
		        try {
		            // Do send the request (this may raise an exception)
		            xhr.send( options.hasContent && options.data || null );
		        } catch ( e ) {
		            // #14683: Only rethrow if this hasn't been notified as an error yet
		            if ( callback ) {
			            throw e;
		            }
		        }
	        },
	        
	        abort: function() {
		        if ( callback ) {
		            callback();
		        }
	        }
	    }
    });
}






/* kolekti objects browser
   inserts a browsable view of the server files in the kolekti interface
   parmaters passed to the browser:
   - mode : select / selectonly / create: 
   - parent : class of the parent element in which the browser is to be inserter
   - buttonsparent : class of the element to contain the action buttons
   - titleparent  : class of the element to conatin the title of the browser
   - title : title of the browser
   - editable_path (boolean) : shall the browser contain a path component 
   - editable_path_title : 
*/


var kolekti_browser = function(args) {
    var url = Urls.kolekti_browser(kolekti.project);
    var urlname = 'kolekti_browser';
    var params = {};
    var path="";
    var root ='/';

    var mode = "select"; // select : Shows select only - create
    var parent = ".modal-body";
    var buttonsparent = ".modal-footer";
    var titleparent = ".modal-header h4";
    var title = "Navigateur de fichiers";
    var editable_path = false
    var update_url = true;
    var titlepath = false
    var drop_files = false
    var os_actions = false
    var os_action_copy = false
    var os_action_delete = false
    var os_action_move = false
    var os_action_rename = false
    var create_actions = false
    var create_builder = function(e, path){
	    e.prepend(
	        [gettext('Nouveau fichier : '),
	         $('<input>',{ 'type':"text",
			               "id":"new_name",
			               'class':"form-control filename"
			             })]
	    )
    };
    var resfuncs = {};
    var modal = true;

    if (args && args.mode)
	    mode = args.mode;
    if (args && args.root) {
	    path = args.root;
        root = args.root;
	    params['root']=root
    }
    if (args && args.path) {
	    path = args.path;
    }
    if (args && args.urlname) {
	    urlname = args.urlname;
    }
    if (args && args.url) {
	    url = args.url;
    }
    if (args && args.parent)
	    parent = args.parent;
    if (args && args.buttonsparent)
	    buttonsparent = args.buttonsparent;
    if (args && args.titleparent)
	    titleparent = args.titleparent;
    if (args && args.title)
	    title = args.title;
    if (args && args.titlepath)
	    titlepath = args.titlepath;
    if (args && args.drop_files)
	    drop_files = args.drop_files;
    if (args && args.modal && args.modal=='no')
	    modal = false;
    if (args && args.editable_path && args.editable_path=='yes')
	    editable_path = true;
    if (args && args.update_url && args.update_url=='no')
	    update_url = false;
	
    if (args && args.os_actions && args.os_actions=='yes') {
	    os_action_delete = true;
	    os_action_copy = true;
	    os_action_rename = true;
	    os_action_move = true;
    }
    if (args && args.os_action_copy && args.os_action_copy=='yes')
	    os_action_copy= true;
    if (args && args.os_action_delete && args.os_action_delete=='yes') 
	    os_action_delete = true;
    if (args && args.os_action_move && args.os_action_move=='yes') 
	    os_action_move = true;
    if (args && args.os_action_rename && args.os_action_rename=='yes') 
	    os_action_rename = true;
    os_actions = (os_action_copy || os_action_delete || os_action_move || os_action_rename)
    
    if (args && args.create_actions && args.create_actions=='yes')
	    create_actions= true;
    else if (args && args.create_actions)
        create_actions= args.create_actions;
    
    if (args && args.create_builder)
	    create_builder = args.create_builder;
    
    params['mode']=mode;


    var get_folder_path = function() {
	    return $(parent).data('folder_path')
    }
    
    var set_folder_path = function(path) {
	    $(parent).data('folder_path', path)
    }

    set_folder_path(path)
    
    var get_browser_value = function() {
	    var path;
	    if (editable_path)
	        path = $(parent).find(".browserfile").val();
	    else
	        path = $(parent).find(".browserfile").data('path')+'/'+$(parent).find(".browserfile").val();
	    return path;
    }

    var set_browser_value = function(path) {
	    if (editable_path)
	        $(parent).find(".browserfile").val(path);
	    else {
	        $(parent).find(".browserfile").data('path', dirname(path))
	        $(parent).find(".browserfile").val(basename(path));
	    }

    }

    var update = function() {

//        console.log( 'browser update ',get_folder_path())
        
        params['path'] = get_folder_path()
        //	    $(parent).data('path',path)

	    $.get(url, params, function(data) {
	        $(parent).html([
		        data,
		        $('<div class="row hidden"><div class="col-sm-12"><input type="text" class="form-control browserfile" id="browserval"/></div></div>')]
			              )
	    }).done(function(){
            if (! $(parent).find('.browser'))
                return
	        if (!create_actions) {
		        $(parent).find('.kolekti-browser-create-actions').hide()
	        } else {
                if (create_actions == "files") {
                    $(parent).find('.kolekti-browser-create-actions .newfolder').hide()
                }
                else if (create_actions == "folders") {
                    $(parent).find('.kolekti-browser-create-actions .newfile').hide()
                }
                else
		            create_builder($(parent).find('.newfile_collapse form'), get_folder_path())
	        }

	        if (!os_actions) 
		        $(parent).find('.kolekti-browser-item-action').hide()
	        else {  
		        if(os_action_delete)
		            $(parent).find('.kolekti-action-remove').click(function(e){
			            var item = $(this).closest('tr').data('name');
			            if (window.confirm(interpolate(gettext("Voulez vous vraiment supprimer %s ?"), [item]))) {
			                $.post(Urls.kolekti_browser_delete(kolekti.project),
                                   {'path': get_folder_path() + "/" + item})
				                .done(function(data) {
				                    closure_remove(item);
				                    update();
				                })
			            }
		            })
		        else
		            $(parent).find('.kolekti-action-remove').hide()

		        if(os_action_copy)
		            $(parent).find('.kolekti-action-copy').click(function(e){
			            var picto = $(this).closest('tr').find('td').first().clone(),
			                name = interpolate(gettext('Copie de %s'),[$(this).closest('tr').data('name')]),
			                srcname = $(this).closest('tr').data('name');
			            $(this).closest('tr').after(
			                $('<tr>', {
				                'html':[$('<td>',{'html':picto}),
					                    $('<td>',{
					                        'html': $('<input>',{
						                        'type':'text',
						                        'class':"copynameinput",
						                        "value":name
					                        }).on('focusout',function(e){
						                        $.post(Urls.kolekti_browser_copy(kolekti.project), 
						                               {
                                                           'from': get_folder_path() + srcname,
						                                   'to': get_folder_path() + $(this).val()
						                               })
						                            .done(function(data) {
							                            // console.log(data)
							                            update();
						                            })
					                        })
					                    }),
					                    $('<td>'),
					                    $('<td>'),
					                    $('<td>')]
			                }))
			            $('.copynameinput').focus();
			            
		            });
		        else
		            $(parent).find('.kolekti-action-copy').hide()

		        if(os_action_rename)
		            $(parent).find('.kolekti-action-rename').click(function(e){
			            $(this).closest('tr').find('.filelink').parent().html(
			                $('<input>',{
				                "type":'text',
				                "value":$(this).closest('tr').data('name')
			                }).on('focusout',function(e){
                                //				console.log('field focusout')
				                var value = $(this).val();
				                var name = $(this).closest('tr').data('name')
				                $(this).remove()
				                if (name != $(this).val())
				                    browser_move_dialog(name, get_folder_path(), value)
                                /*
				                  $.post('/browse/move',
					              {'from':path + "/" + $(this).closest('tr').data('name'),
					              'to': path + "/" + $(this).val()
					              })
				                  .done(function(data) {
					              update();
				                  })
                                */
				                else
				                    update()
			                })
			            );
			            $(this).closest('tr').find('input').focus();
		            });
		        else
		            $(parent).find('.kolekti-action-rename').hide()
		        
		        if(os_action_move)		
		            $(parent).find('.kolekti-action-move').click(function(e){
			            $.post(Urls.kolekti_browser_move(kolekti.project),
			                   {
                                   'from': get_folder_path() + $(this).closest('tr').data('name'),
				                   'to': get_folder_path() + $(this).data('dir')
			                   })
			                .done(function(data) {
				                // console.log(data)
				                update();
			                })

		            });
		        else
		            $(parent).find('.kolekti-action-move').hide()
	            
		        $(parent).find('.dirlist tr.file').each(function(i,e){
		            promise_setup_file(e)
		        });
	        } // end os actions 
	        
//	        set_browser_value(path + '/');
            
//            console.log('res status', get_folder_path())
	        $.get(Urls.kolekti_sync_res_status(kolekti.project),
                  {'path':get_folder_path()})
		        .done(function(data) {
                    $(parent).data('statuses', data)
		            var rows =  $(parent).find('tr[data-name]')
                    $.each(rows, function(ri,row) {
                        console.log($(row).data('name'))
                        var entry = data[$(row).data('name')].__self
                        status = entry.kolekti_status
			            if (entry.kind != 'dir') {
				            var cell = $(row).find('.kolekti-browser-sync');
				            switch(status) {
				            case 'unversioned':
					            icon = $('<i>',{
					                'class':"fa fa-question-circle text-"+kolekti_bootstrap_status[status]
					            })
				                
					            break;
				            case 'update':
				            case 'commit':
					            icon = $('<i>',{
					                'class':"fa fa-info-circle text-"+kolekti_bootstrap_status[status]
					            })
					            break;
				            case 'merge':
				            case 'conflict':
				            case 'error':
					            icon = $('<i>',{
					                'class':"fa fa-exclamation-circle text-"+kolekti_bootstrap_status[status]
					            })
					            break;
				            default:
					            icon = $('<i>',{
					                'class':"fa fa-check text-"+kolekti_bootstrap_status[status]
					            })
				            }
			                
				            cell.html($('<span>',{
                                //					'href':"#",
					            'class':status,
					            'data-status':status,
					            'data-rstatus':entry.rstatus,
					            'data-wstatus':entry.wstatus,
					            'html':icon,
					            'role':"button",
					            "data-trigger":"focus",
					            'tabindex':ri
				            }))
				        }
			        });
		            
		            var sync_popover = $('.kolekti-browser-sync span').popover({
			            'content':function(){
			                var msg = "",
				                linksync = false,
				                linkadd  = false;
			                switch($(this).data('status')) {
			                case 'unversioned':
				                linkadd = true;
				                break;
			                case 'ok':
				                msg =  gettext("À jour avec le référentiel");
				                break;
			                case 'commit':
				                if ($(this).data('wstatus') == 'added') {
				                    msg += "<div><a href='#' class='kolekti-browser-sync-remove'>";
                                    msg += gettext("Enlever de la synchro");
                                    msg += "</a></div>";
                                }
				                linksync = true;
				                break;
			                case 'merge':
				                msg = gettext("Modifications locales et distantes, la fusion est possible");
				                linksync = true;
				                break;
			                case 'update':
				                msg = gettext("Mise à jour disponible");
				                linksync = true;
				                break;
			                case 'conflict':
			                case 'error':
				                msg = gettext("Modifications locales et distantes concurrentes");
				                linksync = true;
				                break;
			                }
			                if(msg.length)
				                msg = "<div>"+msg+"</div>";
			                if(linksync) {
				                msg += "<div><a href='/sync/'>";
                                msg += gettext("Synchroniser le projet");
                                msg += "</a></div>";
                            }
			                if(linkadd) {
				                msg += "<div><a href='#' class='kolekti-browser-sync-add'>";
                                msg += gettext("Ajouter à la synchro");
                                msg += "</a></div>";
                            }
			                return msg
			            },
			            'title':function(){
			                var msg = "";
			                switch($(this).data('status')) {
			                case 'unversioned':
				                msg =  gettext("Non synchronisé");
				                break;
			                case 'ok':
				                msg = gettext("Synchronisé")
				                break;
			                case 'commit':
				                switch($(this).data('wstatus')) {
				                case 'added':
				                    msg = gettext("Ajouté")
				                    break;
				                default:
				                    msg = gettext("Modifié")
				                }
				                break;
			                case 'merge':
				                msg = gettext("Modifié")
				                break;
			                case 'update':
				                msg = gettext("Obsolète")
				                break;
			                case 'conflict':
				                msg = gettext('Conflit')
				                break;
			                case 'error':
				                msg = gettext('Conflit')
				                break;
			                }
			                return "<span class='text-"+kolekti_bootstrap_status[$(this).data('status')]+"'><strong>"+msg+"</strong></span>";
			            },
			            'trigger':'click',
			            'placement':"left",
			            'html':true
		            }); // end popover definition
		        })



	        // DND

	        $(parent+' tr.file').draggable({
		        revert: "invalid", // when not dropped, the item will revert back to its initial position
		        containment: "document",
		        helper: "clone",
		        cursor: "move"
	        });
	        
	        $(parent+' tr.dir').droppable({
		        accept:"tr.file",
		        hoverClass: "ui-state-hover",
		        drop: function( event, ui ) {
		            browser_move_dialog($(ui.draggable).data('name'), get_folder_path() +  $(this).data('name') + '/', null)
		        }	    
	        })

	        $(parent).find('.pathstep').each(function(i,e) {
		        var newpath = $(this).data("path");
		        if (newpath.split('/').length >= root.split('/').length - 1) {
		            $(this).droppable({
			            accept:"tr.file",
			            hoverClass: "ui-state-hover",
			            drop: function( event, ui ) {
			                browser_move_dialog($(ui.draggable).data('name'), $( this ).data('path'), null)
			            }	    
		            })
		        }
	        });
		    
	        // order entries : read from session storage
	        
	        if (sessionStorage && sessionStorage.browser_sort) {
		        sort = sessionStorage.browser_sort
		        order = sessionStorage.browser_sort_order
	        } else {
		        sort = "name";
		        order = "asc";
	        }
	        $(parent).find('.sortcol-'+sort).each(function(i,e) {
		        $(e).attr('data-sort',order)
		        if(order=="asc") {
		            $(e).children("span").removeClass('glyphicon-arrow-up hidden');
		            $(e).children("span").addClass('glyphicon-arrow-down');
		        } else {
		            $(e).children("span").removeClass('glyphicon-arrow-down hidden');
		            $(e).children("span").addClass('glyphicon-arrow-up');
		        }
	        });
	        bsort(sort, order == "asc")
	        
	        promise_setup();
	        
	        if (modal)
		        $('.modal').modal();
	    });

	    $(window).trigger('kolektibrowserchange');
    } // end update function

    var browser_move_dialog = function(filename, newpath, newfilename) {
	    if (newfilename == null) {
	        newfilename = filename;
	    }
        //	console.log('browser move alert')
	    $('.browser-alert').remove();
	    $(parent).find('.browser').prepend(
	        $('  <div>', {
		        'class':"alert alert-danger browser-alert",
		        'role':"alert",
		        'html':[
		            $("<button>", {
			            'type':"button",
			            'class':"close",
			            'data-dismiss':"alert",
			            'html':$("<span>", {
			                'aria-hidden':"true",
			                'html':[
				                '&times;',
				                $('<span>',{'class':"sr-only",'html':gettext('Fermer')})
			                ]
			            })
		            }),
		            $("<span>", {
			            'class':"alert-body",
			            'html':[gettext("Déplacer / renommer"),
				                $('<p><strong>' +
                                  gettext("Attention") +
                                  '</strong> ' +
                                  gettext("Si vous déplacez ou renommez cette ressource, les liens et références seront cassés !") +
                                  "</p>"),
				                $('<button>', {
				                    'class':"btn btn-xs btn-default",
				                    'html':gettext('Annuler')
				                    //				}).on('click', function(){$(this).closest('.alert').remove()}),
				                }).on('click', function(){update()}),
				                " ",
				                $('<button>', {
				                    'class':"btn btn-xs btn-primary",
				                    'html':'Confirmer'
				                }).on('click', function(){
				                    $(this).closest('.alert-body').html()
				                    $.post(Urls.kolekti_browser_move(kolekti.project), 
                                           {
                                               'from':get_folder_path() + filename,
					                           'to':newpath + newfilename
                                           })
					                    .done(update)
					                    .fail(
					                        $(this).closest('.alert-body').html([
						                        $("<p>",{
                                                    html:gettext("Erreur au déplacement de la ressource")
                                                }),
						                        $('<button>', {
						                            'class':"btn btn-xs btn-default",
						                            'html':gettext('Fermer')
						                        }).on('click', function(){$(this).closest('.alert').remove()}),
					                        ]))
				                }),
				                
			                   ]
				        
		            })
		        ]
	        })
	    )
    }
    
    var browser_alert = function(msg) {
        //	    console.log('browser-alert')
	    $('.browser-alert').remove();
	    $(parent).find('.browser').prepend(
	        $('  <div>', {
		        'class':"alert alert-danger alert-dismissible browser-alert",
		        'role':"alert",
		        'html':[
		            $("<button>", {
			            'type':"button",
			            'class':"close",
			            'data-dismiss':"alert",
			            'html':$("<span>", {
			                'aria-hidden':"true",
			                'html':[
				                '&times;',
				                $('<span>',{'class':"sr-only",'html':'Fermer'})
			                ]
			            })
		            }),
		            $("<span>", {
			            'class':"alert-body",
			            'html':msg
		            })
		        ]
	        })
	    )
    }
    var return_functions = {
	    'select':function(f) {	
	        resfuncs['select']=f;
	        return return_functions;
	    },
	    'create':function(f) {	
	        resfuncs['create']=f;
	        return return_functions;
	    },
	    'remove':function(f) {
	        resfuncs['remove']=f;
	        return return_functions;
	    },
	    'setup_file':function(f) {	
	        resfuncs['setup_file']=f;
	        return return_functions;
	    },
	    'setup':function(f) {
            //	        console.log("register setup")
	        resfuncs['setup']=f;
	        return return_functions;
	    },
    };

    var error_callback = function(msg) {
        $(parent + ' .newfile_collapse.in').collapse('hide');
        $(parent + ' .newfolder_collapse.in').collapse('hide');
        $(parent + ' .error_collapse').collapse('show')
        $(parent + ' .error_collapse .panel-body').html(msg)
    }
    
    // calls register callback functions

    var closure_select = function(e) {
        //	    console.log(get_browser_value())
	    resfuncs['select'].length && e.preventDefault() 
	    resfuncs['select'] && resfuncs['select'](get_browser_value(), error_callback);
    };	
    var closure_create = function() {
//	    console.log('closure create', get_folder_path())
	    resfuncs['create'] && resfuncs['create']($(parent), get_folder_path(), update, error_callback);
    };
    var closure_remove = function(e) {
	    resfuncs['remove'] && resfuncs['remove'](e, get_folder_path(), error_callback);
    };
    var promise_setup_file = function(e) {
	    var f = $(e).data('name'); 
	    resfuncs['setup_file'] && resfuncs['setup_file']($(parent), e, get_folder_path(), f);
    };
    var promise_setup = function() {
	    // console.log(resfuncs.setup)
	    // console.log(resfuncs['setup'])
	    resfuncs['setup'] && resfuncs['setup']($(parent), get_folder_path());
    };


    // click on file/directory name

    $(parent).on('click', '.filelink', function(e) {
	    if ($(this).data('mimetype') == "text/directory") {
	        e.preventDefault();
	        var path = get_folder_path() + $(this).html()+ '/';
	        if (update_url) {
                var url = Urls.kolekti_project_static(kolekti.project,  path.substr(1))
		        window.history.pushState([path], document.title, url)
            }
            set_folder_path(path);
	        update();
            
	    } else {
	        if ($(this).attr('href') != "#") {
		        set_browser_value($(this).attr('href'))
	        } else {
		        set_browser_value(get_folder_path() + '/' + $(this).html())
	        }
	        closure_select(e)
	    }


    })

    // navigate into parent folders

    $(parent).on('click', '.pathstep', function(e) {
	    e.preventDefault();
	    var newpath = $(this).data("path") + "/";
		if (newpath.split('/').length >= root.split('/').length) {
	        if (update_url) {
                var url = Urls['kolekti_project_static'](kolekti.project, newpath.substr(1))
		        window.history.pushState([newpath],document.title, url)
            }
	        set_folder_path(newpath);
	        update();
	    }
    })

    // new folder/file accordion behavior

    $(parent).on('click', '.newfolder', function(e){
	    $(parent + ' .newfile_collapse.in').collapse('hide');
        $(parent + ' .error_collapse.in').collapse('hide');
    });

    $(parent).on('click', '.newfile', function(e){
	    $(parent + ' .newfolder_collapse.in').collapse('hide');
        $(parent + ' .error_collapse.in').collapse('hide');
    });

    $(parent).on('shown.bs.collapse', '.newfile_collapse', function () {
	    $(parent + ' .newfile_collapse input').focus();
    })
    
    $(parent).on('shown.bs.collapse', '.newfolder_collapse', function () {
	    $(parent + ' .newfolder_collapse input').focus();
    })
    
    // new folder

    $(parent).on('click', '.create-folder', function(e) {
		e.preventDefault();
		e.stopImmediatePropagation();
	    folderpath = get_folder_path() + $(parent).find(".foldername").val();
	    $.post(Urls.kolekti_browser_mkdir(kolekti.project),{'path':folderpath})
            .done(function(data) {
                var path = folderpath + '/';
	            if (update_url) {
                    var url = Urls.kolekti_project_static(kolekti.project, path.substring(1))
		            window.history.pushState(path, document.title, url + '/')
                }
                set_folder_path(path);               
	            update();
	        })
    })
    
    $(parent).on('click', '.create-file', function(e) {
	    e.preventDefault();
	    e.stopImmediatePropagation();
	    closure_create();
    })
    
    $(parent).on('keyup', '.panel-heading input[type=text]', function (e) {
        if(e.keyCode == 13) {
            $(this).closest('form').find('button.create_action').trigger( "click" );
        }
    })
    

    // Validate modal / browser

    /*
      $(parent).on('click', '.browservalidate', function() {
	  closure();
      })
    */


    // sorting

    
    var bsort = function(col, asc) {
        var bsort_function = function(a, b)  {
            var stra = (''+$(a).data('sort-'+col)).toUpperCase();
            var strb = (''+$(b).data('sort-'+col)).toUpperCase();
	        var cmp = stra.localeCompare(strb);
	        return asc?cmp:0-cmp;
	    }

	    var mylist = $(parent).find('.dirlist tbody');
	    var listitems = mylist.children('tr').get();
        var lastlistitem, parentitems = {};
        $.each(listitems, function(idx, itm) {
            if ($(itm).hasClass('sortableitem')) {
                lastlistitem = itm
            }
            else {
                if(parentitems[$(lastlistitem).data('name')]) {
                    parentitems[$(lastlistitem).data('name')].push(itm)
                } else {
                    parentitems[$(lastlistitem).data('name')]=[itm]
                }
            }
        });
	    var listitems = mylist.children('tr.sortableitem').get();
	    listitems.sort(bsort_function)
	    $.each(listitems, function(idx, itm) {
            mylist.append(itm);
            if (parentitems[$(itm).data('name')]) {
                parentitems[$(itm).data('name')].sort(bsort_function)
                $.each(parentitems[$(itm).data('name')], function(iidx, iitm) {
                    mylist.append(iitm);
                });
            }
        });
    }

    
    // handler : click for sort

    $(parent).on('click', '.sortcol', function(event) {
	    event.preventDefault();
	    var asc = true;
	    $(parent+" .sortcol span").addClass("hidden");
	    if ($(this).data('sort')=="asc") {
	        asc = false
	        $(this).data('sort',"des");
	        $(this).children("span").data('sort',"des");
	        $(this).children("span").removeClass('glyphicon-arrow-down hidden');
	        $(this).children("span").addClass('glyphicon-arrow-up');
	    } else {
	        asc = true
	        $(this).data('sort',"asc");
	        $(this).children("span").removeClass('glyphicon-arrow-up hidden');
	        $(this).children("span").addClass('glyphicon-arrow-down');
	    }
	    if (sessionStorage) {
	        sessionStorage.browser_sort = $(this).data("sortcol")
	        sessionStorage.browser_sort_order = $(this).data('sort')
	    }
	    bsort($(this).data('sortcol'),asc);
    })

    

    // drag and drop files

    if (drop_files) {
	    $(parent).on('dragenter', '.panel', function() {
            $(this).addClass('panel-danger');
	        $(this).addClass('drop');
            return false;
	    });
	    
	    $(parent).on('dragover', '.panel', function(e){
            e.preventDefault();
            e.stopPropagation();
            $(this).addClass('panel-danger');
	        $(this).addClass('drop');
	        return false;
	    });
	    
	    $(parent).on('dragleave', '.panel', function(e) {
            e.preventDefault();
            e.stopPropagation();
	        $(this).removeClass('panel-danger');
	        $(this).removeClass('drop');
            return false;
	    });
	    
	    $(parent).on('drop', '.panel', function(e) {
            if(e.originalEvent.dataTransfer){
		        if(e.originalEvent.dataTransfer.files.length) {
                    // Stop the propagation of the event
                    e.preventDefault();
                    e.stopPropagation();
		            $(this).removeClass('panel-danger');		
		            $(this).removeClass('drop');
                    // Main function to upload
                    upload(e.originalEvent.dataTransfer.files);
		        }  
            }
            else {
		        $(this).removeClass('drop');
		        $(this).removeClass('panel-danger');		
            }
            return false;
	    });
	    
	    function upload(files) {
	        var promises = []
	        var progress_uploads = 0;
	        var imagePromise = function(f) {
		        // Only process image files.
		        /*
		          if (!f.type.match('image/jpeg')) {
		          alert('The file must be a jpeg image') ;
		          return false ;
		          }
	            */
		        var loader = new FileReader();
		        var def = $.Deferred(), promise = def.promise();
		        loader.onprogress = loader.onloadstart = function (e) { def.notify(e); };
		        loader.onerror = loader.onabort = function (e) { def.reject(e); };
		        promise.abort = function () { return loader.abort.apply(loader, arguments); };
		        
		        // When the image is loaded,
		        // run handleReaderLoad function
		        loader.onload = function(evt) {
		            var pic = {};
		            var picinfo = evt.target.result.split(',');
		            
		            pic.mime = picinfo[0];
		            pic.file = picinfo[1];
		            pic.name = f.name;
		            pic.path = get_folder_path(path);
		            $.ajax({
			            type: 'POST',
			            url: Urls.kolekti_browser_upload(kolekti.project),
			            data: $.param(pic),
		            }).done(function(data) {
			            def.resolve(data) ;
		            })
		        }
		        loader.readAsDataURL(f);
		        
		        return promise;
	        }
            $.each(files, function(i,f) {
		        promises.push(imagePromise(f));
	        });
	        $.when.apply($, promises).done(function () {
		        update();
	        })
	    }
    }
    
    // sync callbacks
    $(parent).on('click', '.kolekti-browser-sync-add', function(event) {
	    $.ajax({
	        type: 'POST',
	        url: Urls.kolekti_sync_add(kolekti.project),
	        data: {"path": get_foder_path() + $(this).closest('tr').data('name')}
	    }).done(update)
	    
    })

    $(parent).on('click', '.kolekti-browser-sync-remove', function(event) {
	    $.ajax({
	        type: 'POST',
	        url: Urls.kolekti_sync_remove(kolekti.project),
	        data: {"path": get_folder_path()+ $(this).closest('tr').data('name')}
	    }).done(update)
	    
    })
    
    // pop curent directory from history
    if (update_url) {
	    var currentState = window.history.state;
	    if(currentState && currentState.path) {
	        set_folder_path(currentState.path)
	    }
        
	    window.onpopstate = function(event) {
	        if(event.state && event.state.path) {
		        set_folder_path(event.state.path)
		        update()
	        } else {
                set_folder_path(root + '/')
		        update()
	        }
	        
	    };
    }
    
    // fetch directory
    
    update()
    
    // return functions

    return return_functions;
}


var radicalbasename = function(path) {
    var pathparts = path.split('/'),
        last = pathparts[pathparts.length - 1];
    //    return last;
    return last.split('.')[0];
}




$(document).ready(function () {
    // affix width

    $('#sideaffix').width($('#sideaffix').parent().width());
    $(window).resize(function () {
        $('#sideaffix').width($('#sideaffix').parent().width());
    });

    // events on text contols
    var handle_return = function(e) {
	    if (e.keyCode == 13) {
	        $('.btn_back').focus();
	        $(this).trigger("focusout");
	    }
    }
    $('body').on('keyup','.copynameinput', handle_return)
    $('body').on('keyup','.kolekti-browser-name input[type=text]', handle_return)


    $("body").on("change","form.upload_form input[type=file]",  function(e) {
        var btn = $(this).closest('form').find('button[type=submit]');
        
        if ($(this).val().length > 0) {
            btn.addClass('btn-primary')
            btn.removeClass('btn-default')
        } else {
            btn.addClass('btn-default')
            btn.removeClass('btn-primary')
        }
    })
    
    $("body").on("submit", "form.upload_form", function(e) {
        if($(this).find("input[type=file]").val().length == 0)
            e.preventDefault()
    })
});
