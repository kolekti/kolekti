$(document).ready( function () {
    // highlight and enable save button
    // should be called after sucessfully performing any mofication on toc
    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').removeClass('hidden');
	$('#btn_save').addClass('btn-warning');
    }

    var disable_save = function() {
	$('#btn_save').addClass('disabled');
	$('#btn_save').addClass('btn-default');
	$('#btn_save').removeClass('btn-warning');
    }
    
    $(window).on('beforeunload', function(e) {
	if($('#btn_save').hasClass('btn-warning')) {
            return 'Trame non enregistrée';
	}
    });

    // serialize the toc in a fomat suitable to push it to the server (save) 

    var process_toc = function(elt) {
	var buf = '';
	var domelt = elt.get(0);
	if (elt.hasClass('kolekti-ui')) {
	    return '';
	}
	else if (elt.hasClass('topic')) {
	    buf+="<a ";
	    if(elt.data('kolekti-topic-href'))
		buf += "href='" + elt.data('kolekti-topic-href') + "' ";
	    buf += "rel='" + elt.data('kolekti-topic-rel') + "'/>";
	}
	else if (elt.hasClass('section')) {
	    buf+="<div class='section'";
	    if (elt.attr('data-hidden') == 'true')
		buf+=" data-hidden='true'";
	    buf+=">";
	    elt.children('.panel-heading').children().each(function(i,e) {
		buf += process_toc($(e));
	    });
	    elt.children('.panel-collapse').children().children().each(function(i,e) {
		buf += process_toc($(e));
	    });
	    buf += "</div>";
	}
	else {
	    if (domelt.nodeType==1) {
		buf += "<" + domelt.localName;
		var attrs = domelt.attributes
		for (var j=0; j<attrs.length; j++) {
		    buf += " " + attrs[j].name;
		    buf += "='"  + attrs[j].value;
		    buf += "'";
		}
		buf += ">";
		for (var j = 0; j < domelt.childNodes.length; j++) {
		    var child = domelt.childNodes[j]
		    buf += process_toc($(child));
		};
		buf += "</" + domelt.localName +">";
	    } else {
		buf += domelt.nodeValue;
	    }
	}
	return buf;		    
    }

    // builds the contaxtual menu for any topic entry in the toc

    var topicmenu = function(topic) {
	var parent=topic.hasClass('section')?
	    topic.children('.panel-heading').find("a").parent():
	    topic.find('h4.panel-title');
	parent.append(
	    $('<span>', {
		'class':'pull-right kolekti-ui kolekti-ui-topic-actions',
		'html' :[
		    (topic.data('kolekti-topic-rel')=='kolekti:topic')?$('<button>', {
			'type':"button",
			'class':"btn btn-primary btn-xs btn_topic_edit",
			'html':[
			    $('<span>',{
				'class':"glyphicon glyphicon-pencil",
				'html':" "}),
			    " Modifier "
			]}):"",
		    " ",
		    $('<span>', {
			'class':"btn-group",
			'html': [
			    $('<button>', {
				'type':"button",
				'class':"btn btn-default btn-xs dropdown-toggle",
				'data-toggle':"dropdown",
				'html':[
				    " Actions ",
				    $('<span>',{
					'class':"caret",
					'html':" "})
				]
			    }),
			    $('<ul>',{
				'class':"dropdown-menu",
				'role':"menu",
				'html':[
				    $('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_topic_insert_before",
					    'html':"Insérer avant..."
					})
				    }),
				    topic.hasClass('section')?$('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_topic_insert_inside",
					    'html':"Insérer dedans..."
					})
				    }):null,
				    $('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_topic_insert_after",
					    'html':"Insérer après..."
					})
				    }),
				    
				    topic.hasClass('section')?$('<li>', {
					'role':"presentation",
					'class':"divider"
				    }):null,
				    
				    topic.hasClass('section')?$('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_section_rename",
					    'html':"Renommer"
					})
				    }):null,
				    
				    topic.hasClass('section')?$('<li>', {
					'role':"presentation",
					'class':"divider"
				    }):null,
				    
				    topic.hasClass('section')?$('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_section_toc_exclude",
					    'html':["Exclure du sommaire",
						topic.attr('data-hidden')=='true'?' ':'',
						topic.attr('data-hidden')=='true'?$('<span>',{'class':"glyphicon glyphicon-ok"}):null,
					       ]
					}),
				    }):null,
				    
				    $('<li>', {
					'role':"presentation",
					'class':"divider"
				    }),

				    $('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_topic_up",
					    'html':"Monter"
					})
				    }),
				    $('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_topic_down",
					    'html':"Descendre"
					})
				    }),
				    $('<li>', {
					'role':"presentation",
					'class':"divider"
				    }),
				    $('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':"#",
					    'class':"btn_topic_delete",
					    'html':"Supprimer"
					})
				    })
				]
			    })
			]
		    })
		]
	    })
	);
    }

    // create / insert "shared" menu for every topic

    var usecases = function(topic) {
/*
	if( path== undefined) {
	    $('div[data-kolekti-topic-rel="kolekti:topic"]').each(function(i,e) {
		listpath.push($(e).data('kolekti-topic-href'))
	    });
	} else {
	    listpath.push(path)
	};
*/
	var topicref = $(topic).data('kolekti-topic-href');
	var tocref=$('#toc_root').data('kolekti-path');
	$.get('/tocs/usecases/',{"pathes":[topicref]}).
	    success(function(data){ 
		$(topic).find('.kolekti-shared-topic').remove();
		var v;
		if (topicref in data)
		    v = data[topicref].removevalue(tocref)
		else
		    v = []
		if(v.length)
		    $('<span>', {
			'class':"btn-group kolekti-shared-topic",
			'html':[
			    $('<button>', {
				'type':"button",
				'class':"btn btn-default btn-xs dropdown-toggle",
				'data-toggle':"dropdown",
				'html':[
				    " Partagé ",
				    $('<span>',{
					'class':"caret",
					'html':" "})
				]
			    }),
			    $('<ul>',{
				'class':"dropdown-menu",
				'role':"menu",
				'html':
				$.map(v, function(tocref) {
				    return $('<li>', {
					'role':"presentation",
					'html':$('<a>', {
					    'role':"menuitem",
					    'tabindex':"-1",
					    'href':'/tocs/edit/?toc='+tocref,
					    'html':tocref
					})
				    })
				}),
			    })]
		    }).insertBefore($(topic).find('.kolekti-ui-topic-actions'));
	    });
    }

    var check_empty = function() {
	if($('#toc_root').find('div, a[rel=kolekti\\:topic]').length == 0) {
	    $('#toc_root').append(
		$('<button>',{
		    'type':"button",
		    'class':"btn btn-default kolekti-ui",
		    'html':"Insérer"
		}).on('click', function(e) {newcomp($(this),false, false)}))
	}
    }

    // left panel button events

    // save

    $('#btn_save').on('click', function() {
	var path = $('#toc_root').data('kolekti-path');
	$.ajax({
	    url:'/tocs/edit/',
	    type:'POST',
	    data:process_toc($('#toc_root')),
	    contentType:'text/plain'
	}).success(function(data) {
	    disable_save();
	    kolekti_recent(displayname(path),'trame','/tocs/edit/?toc='+path)
	    
	});
    })

    $('#btn_save_as').on('click', function() {
	kolekti_browser({
	    'root':'/sources/'+kolekti.lang+'/tocs',
	    'title':"Enregistrer sous...",
	    'mode':"create",
	    'editable_path':false,
	    'update_url':false
	}).select(function(path) {
	    console.log(path);
	    $('#toc_root').attr('data-kolekti-path', path);
	    $.ajax({
		url:'/tocs/edit/',
		type:'POST',
		data:process_toc($('#toc_root')),
		contentType:'text/plain'
	    }).success(function() {
		$('#btn_save').addClass('disabled');
		$('#btn_save').addClass('btn-default');
		$('#btn_save').removeClass('btn-warning');
		kolekti_recent(displayname(path),'trame','/tocs/edit/?toc='+path)
		document.location.href = '/tocs/edit/?toc='+path
	    });
	}).always(function(data) {
	    $('.modal').modal('hide');
	})
    })

    // publish

    var get_publish_params = function(cssclass) {
	var params={};
	params['profiles']=[]
	$(".kolekti-job-"+cssclass).find('.publish_job_profile').each(function(i, e) {
	    if ($(e).is(":checked"))
		params['profiles'].push($(e).data('kolekti-profile'))
	});
	params['scripts']=[]
	$(".kolekti-job-"+cssclass).find('.publish_job_script').each(function(i, e) {
	    if ($(e).is(":checked"))
		params['scripts'].push($(e).data('kolekti-script'))
	});
	params['pubdir']=$("#input_toc_pubdir").val();
	params['pubtitle']=$("#input_toc_title").val();
	return params;
    }

    $('.publish_job').on('click', function(e) {
	$('#collapse_'+$(this).attr('id')).collapse('toggle');
    })

    
    $('.btn_publish').on('click', function() {
	var url='/publish/'

	var toc = $('#toc_root').data('kolekti-path');
	var job = $('#toc_root').data('kolekti-meta-kolekti_job');
	var cssclass = $('#toc_root').data('kolekti-meta-kolekti_jobclass');
	var jobpath =  $('#toc_root').data('kolekti-meta-kolekti_jobpath');
	params = get_publish_params(cssclass)
	params['toc']=toc;
	params['job']=jobpath;

	$('.modal-body').html('<div id="releasename"></div><div id="pubresult"></div>');
	$('.modal-title').html('Publication');

	if (!(params['profiles'].length &&  params['scripts'].length)) {
	    $('#pub_progress').remove();
	    $('#pubresult').html('<div class="alert alert-danger" role="alert"><p>Sélectionnez au moins un profile et un script</p></div>');
	    $('.modal').modal();
	    return;
	} 
	
	
	var check_release = function(action) {
	    var fmtdate = function(d) {
		var mm = d.getMonth() + 1; // getMonth() is zero-based
		var dd = d.getDate();
		
		return [d.getFullYear(),
			(mm>9 ? '' : '0') + mm,
			(dd>9 ? '' : '0') + dd
		       ].join('');
	    };

	    var toc = $('#toc_root').data('kolekti-path');
	    $('.modal-footer button').html('fermer');
	    $('.modal-title').html('Création de version');
	    $('#releasename').html('<div class="panel panel-default"><div class="panel-body"><div class="form"><div class="form-group"><label for="release_name">Nom de la version</label><input type="text" class="form-control" id="release_name"/></div><div class="form-group"><label for="release_indice">Indice de la version</label><input type="text" class="form-control" id="release_index"/></div><div class="form-group"><button class="btn btn-default" id="confirm_version">Créer la version</button></div></div></div></div>');
	    $('.modal').modal('show');
	    $('.modal').on('shown.bs.modal', function() {
		$("#release_name").val($('#toc_root').data('kolekti-tocname'));
		$("#release_index").val(fmtdate(new Date()));
		$("#release_name").focus();
	    })

	    $('#modalform').submit( function(e) {
		e.preventDefault();
		e.stopImmediatePropagation();
		
		params['release_name'] = $('#release_name').val().replace('/','_')
		params['release_index'] = $('#release_index').val().replace('/','_')
		params['pubdir'] = params['release_name'] + '_' +params['release_index'];
		var assembly = "/releases/"+ params['pubdir'] +"/sources/" + kolekti.lang + "/assembly/" + params['pubdir'] + '_asm.html'
		$.get(assembly)
		    .success(function() {
			if(confirm('Cette version existe deja, voulez vous forcer la création ?'))
			    do_publish()
		    })
		    .error(function() {
			do_publish()
		    })
	    })
	}

	var do_publish = function() {
	    $('.modal-footer button').html('fermer');
	    $('.modal').modal();
	    $('#pubresult').html('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Lancement '+job+'</h4></div><div class="panel-body"><div class="progress" id="pub_progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Publication in progress</span></div></div><div id="pub_results"></div><div id="pub_end" class="alert alert-info" role="alert">Publication terminée</div></div></div>');
	    
	    $('#pub_end').hide();

	    var streamcallback = function(data) {
		//		console.log(data);
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
	    });
	};
	
	if ($(this).attr('id') == 'btn_release') {
	    url += 'release/'
	    $('.modal-title').html('Création de version');
	    check_release(params, do_publish)

	} else {
	    url += 'draft/'
	    $('.modal-title').html('Publication');
	    do_publish()
	}

    });

    // display

    
    $('#btn_collapse_all').on('click', function() {
	$('.topic .collapse').collapse('hide');
	$('.topic a[data-toggle=collapse]').addClass('collapsed');
    });

    $('#btn_expand_all').on('click', function() {
	$('.topic .collapse').collapse('show');
	$('.topic a[data-toggle=collapse]').removeClass('collapsed');
    });

    $('#btn_toggle_all').on('click', function(e) {
	if ($(this).hasClass('collapsed')) {
	    $(this).removeClass('collapsed');
	    $('.topic .collapse').collapse('show');
	    $('.topic a[data-toggle=collapse]').removeClass('collapsed');
	} else {
	    $(this).addClass('collapsed');
	    $('.topic .collapse').collapse('hide');
	    $('.topic a[data-toggle=collapse]').addClass('collapsed');
	}
    });
    
    $('#toc_meta').hide();

    $('#btn_meta').on('click', function(e) {
	if ($(this).hasClass('collapsed')) {
	    $(this).removeClass('collapsed');
	    $('#toc_meta').show();
	} else {
	    $(this).addClass('collapsed');
	    $('#toc_meta').hide();
	}
    });

    // diagnostic

    $('#btn_audit').on('click', function() {
	kolekti_browser({'root':'/sources'})
	    .select(function(path) {console.log(path)})
	    .always(function() {console.log("after")})
	;
    });



    // components from meta
    $('body').on('change','#input_toc_title', function(e) {
	var title = $.trim($(this).val());
	$('#toc_root').data('kolekti-title',title)
	$('#toc_root').attr('data-kolekti-title',title)
	enable_save()
    })

    $('body').on('change','#input_toc_author', function(e) {
	var author = $.trim($(this).val());
	$('#toc_root').data('kolekti-author', author)
	$('#toc_root').attr('data-kolekti-author', author)
	enable_save()
    })


    $('body').on('change','#input_toc_pubdir', function(e) {
	var title = $.trim($(this).val());
	$('#toc_root').data('kolekti-meta-kolekti_pubdir',title)
	$('#toc_root').attr('data-kolekti-meta-kolekti_pubdir',title)
	enable_save()
    })

    // job selection menu items
    
    $('body').on('click','.entry_tocjob', function(e) {
	var name = $.trim($(this).text())
	var path = $(this).data('kolekti-jobpath');
	var cssclass = $(this).data('kolekti-jobclass');

	$('#editjoblink').show();
	$('#editjoblink').removeClass('hidden')
	$('#quickselect').removeClass('hidden')

	$('#toc_root').data('kolekti-meta-kolekti_job',name)
	$('#toc_root').attr('data-kolekti-meta-kolekti_job',name)
	$('#toc_root').data('kolekti-meta-kolekti_jobclass',cssclass)
	$('#toc_root').attr('data-kolekti-meta-kolekti_jobclass',cssclass)
	$('#toc_root').data('kolekti-meta-kolekti_jobpath',path)
	$('#toc_root').attr('data-kolekti-meta-kolekti_jobpath',path)
	$('#editjoblink').attr('href','/settings/job?path='+path)
	$('.label_job').each(function(i,e) {
	    $(e).html(name)}
			    );
	$('.kolekti-job').addClass('hidden')
	$('.kolekti-job-'+cssclass).removeClass('hidden')
	enable_save()
    });

    
    // contextual menus

    // modify topic / section

    $('body').on('click', '.btn_topic_edit', function(e) {
	var topic = $(this).closest('.topic');
	var url = topic.data('kolekti-topic-href');
	window.open('/topics/edit/?topic='+url);

    }) 

    $('body').on('click', '.btn_section_rename', function(e) {
	// get section title
	e.preventDefault();
	disable_save()
	
	var title_elt = $(this).closest('.section')
	    .children('.panel-heading')
	    .children('')
	    .children('a');
	
	var i = $('<input>',{
	    "type":'text',
	    "value":title_elt.children('span').html()
	});
	
	i.on('focusout',function(e){
	    if ($(this).closest('tr').data('name')!= $(this).val()) {
		var new_title=$(this).val();
		title_elt.children('span').html(new_title);
		    enable_save();
		    $(this).remove();
		}
	    })
	title_elt.after(i);
	i.focus();
   
	title_elt.children('span').html('');
    });	
    

    $('body').on('click', '.btn_section_toc_exclude', function(e) {
	var section = $(this).closest('.section')
	if ($(this).data("state") == 'on')
	{
	    $(this).data("state",'off');
	    $(this).parent().find('span').remove();
	    section.removeAttr('data-hidden')
	} else {
	    $(this).data("state",'on');
	    $(this).append([' ',$('<span>',{'class':"glyphicon glyphicon-ok"})]);
	    section.attr('data-hidden', 'true')
	}
	enable_save();
    })

    
    // move topic

    $('body').on('click', '.btn_topic_up', function(e) {
	e.preventDefault();
	var comp = $(this).closest('.topic, .section');
	if (comp.length) {
	    if (comp.prev('.topic').length) {
		// precedent est un topic
		comp.insertBefore(comp.prev('.topic'));
		enable_save();
	    } else if (comp.prev('.section').length) {
		// precedent est une section
		var section = comp.prev('.section');
		comp.appendTo(section.find('.panel-body')[0]);
		show_section(section);
		enable_save();
	    } else {
		// pas de précédent, on regarde si on est dans un section
		var sections = comp.parents('.section');
		if (sections.length) {
		    // section.insertBefore(comp);
		    comp.insertBefore(sections.first());
		    enable_save();
		}
	    }
	}

    });


    $('body').on('click','.btn_topic_down', function(e) {
	e.preventDefault();
	var comp = $(this).closest('.topic, .section');
	if (comp.length) {
	    if (comp.next('.topic').length) {
		// suivant  est un topic
		comp.insertAfter(comp.next('.topic'));
		enable_save();
	    } else if (comp.next('.section').length) {
		// suivant  est une section
		var section = comp.next('.section');
		comp.prependTo(section.find('.panel-body'));
		show_section(section);
		enable_save();
	    } else {
		// pas de suivant, on regarde si on est dans un section
		var sections = comp.parents('.section');
		if (sections.length) {
		    comp.insertAfter(sections.first());
		    enable_save();
		}
	    }
	}
    });

    $('body').on('click', '.btn_topic_insert_before', function(e) {
	e.preventDefault();
	var topic = $(this).closest('.topic');
	if (topic.length == 0)
	    topic = $(this).closest('.section');
	newcomp(topic, false, false);
    });

    $('body').on('click', '.btn_topic_insert_after', function(e) {
	e.preventDefault();
	var topic = $(this).closest('.topic');
	if (topic.length == 0)
	    topic = $(this).closest('.section');
	newcomp(topic,true, false);
    });
    
    $('body').on('click', '.btn_topic_insert_inside', function(e) {
	e.preventDefault();
	topic = $(this).closest('.section');
	newcomp(topic,false, true);
    });
    
    // remove topic

    $('body').on('click', '.btn_topic_delete', function(e) {
	e.preventDefault();
	var topic = $(this).closest('.topic');
	if (topic.length) {
	    topic.remove();
	    enable_save();
	} else if ($(this).closest('.section').length) {
	    if (window.confirm('Supprimer la section ?')) {
		$(this).closest('.section').remove();
		enable_save();
	    }
	}
	check_empty();
    });

    
    var create_topic_obj = function(path, id, topic) {

	var topicfile = basename(path);

	var topic_obj = $('<div>', {
	    'class':"topic",
	    'data-kolekti-topic-rel':"kolekti:topic",
	    'data-kolekti-topic-href':path,
	    'html':$('<div>', {
		'class':"panel panel-default",
		'html':[
		    $('<div>', {
			'class':"panel-heading",
			'html':$('<h4>', {
			    'class':"panel-title",
			    'html':$('<a>',{
				'data-toggle':"collapse",
				'class':"collapsed",
				'href':"#collapse_"+id,
				'html':[
				    $('<small>',{
					'html':[
					    $('<span>',{
						'class':"glyphicon glyphicon-chevron-right",
						'aria-hidden':"true",
						html:' '
					    }),
					    $('<span>',{
						'class':"glyphicon glyphicon-chevron-down",
						'aria-hidden':"false",
						html:' '
					    })
					]}),
				    $('<span>',{
					'data-toggle':"tooltip", 
					'data-placement':"top",
					'title':path,
					'html':$('<small>',{'html':topicfile})
				    })
				]
			    })
			})
		    }),
		    $('<div>', {
			'class':"panel-collapse collapse",
			'id':"collapse_"+id,
			'html':$('<div>',{ 
			    'class':"topiccontent",
			    'html':$(topic).find('body').children()
			}),
		    })
		]
	    })
	});
	
	topicmenu(topic_obj);
	return topic_obj;
    } 

    var create_topic_error_obj = function(path, id, reason) {
	reason = reason || "Module has errors"
	var topicfile = displayname(path);

	var topic_obj = $('<div>', {
	    'class':"topic",
	    'data-kolekti-topic-rel':"kolekti:topic:error",
	    'data-kolekti-topic-href':path,
	    'html':$('<div>', {
		'class':"panel panel-danger",
		'html':[
		    $('<div>', {
			'class':"panel-heading",
			'html':$('<h4>', {
			    'class':"panel-title",
			    'html':[
				$('<span>',{
				    'class':"glyphicon glyphicon-warning-sign",
				    'title':reason,
				    'html':" "}),
				" ",
				$('<span>',{
				    'data-toggle':"tooltip", 
				    'data-placement':"top",
				    'title':path,
				    'html':$("<small>",{"html":topicfile})
			    })]
			})
		    })
		]
	    })
	});
	
	topicmenu(topic_obj);
	return topic_obj;
    }

    var create_section_obj = function(id, title) {
	var section_obj = $('<div>', {
	    'class':"section panel panel-info",
	    'html':[$('<div>', {
		'class':"panel-heading",
		'html':$('<h1>', {
		    'html':$('<a>',{
			'data-toggle':"collapse",
			'class':"collapsed",
			'href':"#collapse_"+id,
			'html':[
			    $('<small>',{
				'data-ui':'yes',
				'html':[
				    $('<span>',{
					'class':"glyphicon glyphicon-chevron-right",
					'aria-hidden':"true",
					html:' '
				    }),
				    $('<span>',{
					'class':"glyphicon glyphicon-chevron-down",
					'aria-hidden':"false",
					html:' '
				    })
				]}),
			    $('<span>',{
				'data-ui':"wrap", 
				'html':title
			    })
			]
		    })
		})
	    }),
		    $('<div>', {
			'class':"panel-collapse collapse",
			'id':"collapse_"+id,
			'html':$('<div>',{ 
			    'class':"panel-body",
			}),
		    })
		   ]
	});
	
	topicmenu(section_obj);
	return section_obj;
    }
 
    var show_section = function(section_obj) {
	section_obj.find('a[data-toggle=collapse]').first().removeClass('collapsed');
	if (! section_obj.find('.panel-collapse.collapse').first().hasClass('in'))
	    section_obj.find('.panel-collapse').first().collapse('toggle');
    }

    // handles dialog for insertion of topics & sections

    var newcomp = function(refcomp, isafter, isinside) {
//	$('.modal').data('refcomp', refcomp);
	$('.modal-title').html('Insertion');
	
	// builds dialog
	$('.modal-body').html(
	    $('<div>', {
		"class":"row",
		"html":[
		    $("<div>", {
			"class":"col-sm-12 col-md-3 insert-buttons",
			"html":[
			    $('<a>',{
				"class":"btn btn-block btn-default btn-insert-module",
				"href":"#",
				"html":"Module"
			    }),
			    $('<a>',{
				"class":"btn btn-block btn-default btn-insert-section",
				"href":"#",
				"html":"Section"
			    }),
			    $('<a>',{
				"class":"btn btn-block btn-default btn-insert-toc",
				"href":"#",
				"html":"Table des matières"
			    }),		
			    $('<a>',{
				"class":"btn btn-block btn-default btn-insert-idx",
				"href":"#",
				"html":"Index"
			    })]
		    }),
		    $("<div>", {
			"class":"col-sm-12 col-md-9 insert-main"
		    })
		]
	    })
	);

	var select_topic_browser = function() {
	    //e.preventDefault();
	    //e.stopImmediatePropagation();
	    
	    $('.insert-buttons a').removeClass('active');
	    $('.modal .btn-insert-module').addClass('active');
	    $('.modal-footer').off('click', '.browservalidate');

	    var insert_topic = function(path) {
		    $.get(path).success(
			function(data){
			    var topic = $.parseXML( data ),
			    id = Math.round(new Date().getTime() + (Math.random() * 100)),
			    topic_obj = create_topic_obj(path, id, topic);
			    if (isafter) { 
				refcomp.after(topic_obj);
			    } else {
				if (isinside) {
				    refcomp.find('.panel-body').prepend(topic_obj);
				    show_section(refcomp);
			        } else {
				    refcomp.before(topic_obj);
				}
			    }
			    $("#toc_root>button").remove();
			    usecases(topic_obj);
			    enable_save();
			    $('.modal').modal('hide');
			})
	    };
	    
	    kolekti_browser(
		{'root':'/sources/'+kolekti.lang+'/topics',
		 'parent':".insert-main",
		 'titleparent':".new-module-title",
		 'create_actions':'yes',
		 'create_builder':create_builder,
		 'update_url':'no'
		})
		.select(insert_topic)
		.create(function(browser, folder, update_function) {
		    var filename = $(browser).find('#new_name').val();
		    $.post('/topics/create/',
			   {
			       'model': $('.label-tpl').data('tpl'),
			       'topicpath': folder + "/" + filename
			   }).done(function(data) {
			       insert_topic(data);
			   }).fail(function() {
			       console.log("error")
			   }).always(function() {
			   });
		})

	    $('.insert-main').on('click', '.tpl-item',function(e){
		$('.label-tpl').html($(this).data('tpl'))
		$('.label-tpl').data('tpl',$(this).data('tpl'));
	    })

	};

	// handle add  topic : select topic

	$('.modal').on('click','.btn-insert-module', function(e) {
	    select_topic_browser();
	});

	$('.modal').off('click','.btn-add-section');
	$('.modal').on('click', '.btn-add-section',function(e) {
	    var id = Math.round(new Date().getTime() + (Math.random() * 100)),
		title = $('.modal #input_section_title').val()
	    section_obj = create_section_obj(id, title);
	    if (isafter) 
		refcomp.after(section_obj);
	    else 
		if (isinside) {
		    refcomp.find('.panel-body').first().prepend(section_obj);
		    show_section(refcomp);
		} else {
		    refcomp.before(section_obj)
		}
	    $("#toc_root>button").remove();
	    enable_save();
	    $('.modal').modal('hide');
	});

	// handles add section : get section title & update structure

	$('.modal').off('click','.btn-insert-section')
	$('.modal').on('click','.btn-insert-section', function(e) {
	    $('.insert-buttons a').removeClass('active');
	    $(this).addClass('active');
	    $('.modal-footer').off('click', '.browservalidate');
	    $('.insert-main').html([
		"Libellé de la section",
		$('<input>', {
		    'type':'text',
		    'class':"form-control",
		    'id':'input_section_title',		
		    'placeholder':''
		}),
		$('<button>',{
		    'type':"button",
		    'class':"btn btn-default btn-add-section",
		    'html':"Insérer"
		})
	    ]);
	    
/*
	    $('.modal-footer').on('click', '.browservalidate', function(event) {
		console.log("add section")
	    });	
*/
	})

	// handles add toc (if not already exists)
	$('.modal').off('click','.btn-insert-toc')
	if ($('#toc_root div[data-kolekti-topic-rel="kolekti:toc"]').length) {
	    $('.modal .btn-insert-toc').addClass('disabled');
	} else {
	    $('.modal').one('click','.btn-insert-toc', function(e) {
		e.preventDefault();
		$('.insert-buttons a').removeClass('active');
		$(this).addClass('active');
		var topic_obj = $('<div>', {
		    'class':"topic",
		    'data-kolekti-topic-rel':"kolekti:toc",
		    'html':$('<div>', {
			'class':"panel panel-warning",
			'html':[
			    $('<div>', {
				'class':"panel-heading",
				'html':$('<h4>', {
				    'class':"panel-title",
				    'html':$('<span>',{
					'data-toggle':"tooltip", 
					'data-placement':"top",
					'title':"Table des matières",
					'html':$('<em>',{'html':"Table des matières"})
				    })
				})
			    })]
		    })
		});
		topicmenu(topic_obj);
		if (isafter) 
		    refcomp.after(topic_obj)
		else 
		    if (isinside) {
			refcomp.find('.panel-body').prepend(topic_obj);
			show_section(refcomp);
		    } else {
			refcomp.before(topic_obj)
		    }
		$("#toc_root>button").remove();
		enable_save();
		$('.modal').modal('hide');
	    });	
	}

	// handles add index (if not already exists)
	$('.modal').off('click','.btn-insert-idx')
	if ($('#toc_root div[data-kolekti-topic-rel="kolekti:index"]').length) {
	    $('.modal .btn-insert-idx').addClass('disabled');
	} else {
	    $('.modal').one('click','.btn-insert-idx', function(e) {
		e.preventDefault();
		$('.insert-buttons a').removeClass('active');
		$(this).addClass('active');
		$('.modal-footer').off('click', '.browservalidate');
		var topic_obj = $('<div>', {
		    'class':"topic",
		    'data-kolekti-topic-rel':"kolekti:index",
		    'html':$('<div>', {
			'class':"panel panel-warning",
			'html':[
			    $('<div>', {
				'class':"panel-heading",
				'html':$('<h4>', {
				    'class':"panel-title",
				    'html':$('<span>',{
					'data-toggle':"tooltip", 
					'data-placement':"top",
					'title':"Index alphabétique",
					'html':$('<em>',{'html':"Index alphabétique"})
				    })
				})
			    })]
		    })
		});

		topicmenu(topic_obj);
		if (isafter) 
		    refcomp.after(topic_obj)
		else 
		    if (isinside) {
			refcomp.find('.panel-body').prepend(topic_obj);
			show_section(refcomp);
		    } else {
			refcomp.before(topic_obj)
		    }
		$("#toc_root>button").remove();
		enable_save();
		$('.modal').modal('hide');
	    });	
	}
	/*
	if (!$('.modal-footer>button.browservalidate').length)
	    $('<button type="button" class="btn btn-default browservalidate">Valider</button>').prependTo($('.modal-footer'));
	*/
	select_topic_browser()

	// display dialog
	$('.modal').modal();
    }  // newcomp

    // end insert dialog


    // finalize UI by adding menus to topics

    $('.topic').each(function(i,t){
	($(t).data('kolekti-topic-rel')=='kolekti:toc' || $(t).data('kolekti-topic-rel')=='kolekti:index')
	    && topicmenu($(t));
    });
    

    $('a').each(function(i,refcomp) {
	if($(refcomp).attr('rel')=="kolekti:topic") {
	    var path = $(this).data('kolekti-topic-url');
	    var idtopic = $(this).data('kolekti-topic-id');
	    var topic;
	    $.get(path)
		.done(
		    function(data){
			try {
			    if (data instanceof Document)
				topic = data;
			    else
				topic = $.parseXML( data );
			    var topic_obj = create_topic_obj(path, idtopic, topic);
			    $(refcomp).after(topic_obj)
			    usecases(topic_obj);
			    $(refcomp).detach();
			} catch (err) {
			    // was not XML
			    var id = Math.round(new Date().getTime() + (Math.random() * 100));
			    var topic_obj = create_topic_error_obj(path, idtopic, "Le module n'est pas valide");
			    $(refcomp).after(topic_obj)
			    $(refcomp).detach();
			}
		    })
		.fail(
		    function(data){
			var id = Math.round(new Date().getTime() + (Math.random() * 100));
			var topic_obj = create_topic_error_obj(path, idtopic, "Module non trouvé");
			$(refcomp).after(topic_obj)
			$(refcomp).detach();
		    });
	}
    });

    $('.section').each(function(i,t){
	topicmenu($(t));
    });

    check_empty();
})
