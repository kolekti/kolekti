$(document).ready( function () {
    // highlight and enable save button
    // should be called after sucessfully performing any mofication on toc
    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').removeClass('hidden');
	$('#btn_save').addClass('btn-warning');
    }

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
	    buf+="<div class='section'>";
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
	    topic.find('h4');
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
					    'class':"btn_section_exclude",
					    'html':"Exclure du sommaire"
					})
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
		var v = data[topicref].removevalue(tocref)
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
	if($('#toc_root').find('div').length == 0) {
	    $('#toc_root').append(
		$('<button>',{
		    'type':"button",
		    'class':"btn btn-default kolekti-ui",
		    'html':"Insérer"
		}).on('click', function(e) {newcomp($(this),false)}))
	}
    }

    // left panel button events

    // save

    $('#btn_save').on('click', function() {
	$.ajax({
	    url:'/tocs/edit/',
	    type:'POST',
	    data:process_toc($('#toc_root')),
	    contentType:'text/plain'
	}).success(function(data) {
	    $('#btn_save').addClass('disabled');
	    $('#btn_save').addClass('btn-default');
	    $('#btn_save').addClass('hidden');
	    $('#btn_save').removeClass('btn-warning');
	});
    })

    $('#btn_save_as').on('click', function() {
	kolekti_browser({
	    'root':'/sources/'+kolekti.lang+'/tocs',
	    'title':"Enregistrer sous...",
	    'mode':"create",
	    'editable_path':false
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
		document.location.href = '/tocs/edit/?toc='+path
	    });
	}).always(function(data) {
	    $('.modal').modal('hide');
	})
    })

    // publish

    var get_publish_params = function(params) {
	params['profiles']=[]
	$(".kolekti-job").find('.publish_job_profile').each(function(i, e) {
	    if (e.checked)
		params['profiles'].push($(e).data('kolekti-profile'))
	});
	params['scripts']=[]
	$(".kolekti-job").find('.publish_job_script').each(function(i, e) {
	    if (e.checked)
		params['scripts'].push($(e).data('kolekti-script'))
	});
	return params;
    }

    $('.publish_job').on('click', function(e) {
	$('#collapse_'+$(this).attr('id')).collapse('toggle');
	
    })


    $('.btn_publish').on('click', function() {
	var url='/publish/'
	var params = {}
	if ($(this).attr('id') == 'btn_release') {
	    url += 'release/'
	} else {
	    url += 'draft/'
	}
	$('.modal-body').html('<div id="pubresult"></div>');
	$('.modal-title').html('Publication');
	$('.modal-footer button').html('fermer');
	$('.modal').modal();
	var toc = $('#toc_root').data('kolekti-path');

	//    $('.publish_job').each(function(i,e){
//	$('.kolekti-job').each(function(i,e){
//	    if (!$(e).hasClass('hidden')) {
//		nojob = false;

	var job = $('#toc_root').data('kolekti-job');
	var jobpath =  $('#toc_root').data('kolekti-job-path');
//	var idjob = $(e).attr('id');
	$('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Lancement '+job+'</h4></div><div class="panel-body"><div id="pub_results"><div class="progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Publication in progress</span></div></div></div></div></div>').appendTo($('#pubresult'));
	params = get_publish_params(params)
		
	if (!(params['profiles'].length &&  params['scripts'].length)) {
	    $('#pub_results').html('<div class="alert alert-danger" role="alert"><p>Sélectionnez au moins un profile et un script</p></div>');
	} else {
	    params['toc']=toc;
	    params['job']=jobpath;
	    
	    $.ajax({
		url:url,
		type:'POST',
		data:params,
	    }).done(function(data) {
		$('#pub_results').html(data);
	    });
	};
    })

    // display

    $('#btn_collapse_all').on('click', function() {
	$('.topic .collapse').collapse('hide');
    });

    $('#btn_expand_all').on('click', function() {
	$('.topic .collapse').collapse('show');
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

    $('body').on('click','.entry_tocjob', function(e) {
	var name = $.trim($(this).text())
	var path = $(this).data('kolekti-job-path');
	console.log(name)
	$('#toc_root').data('kolekti-job',name)
	$('#toc_root').attr('data-kolekti-job',name)
	$('#toc_root').data('kolekti-job-path',path)
	$('#toc_root').attr('data-kolekti-job-path',path)
	$('#editjoblink').attr('href','/settings/job?path='+path)
	$('.label_job').each(function(i,e) {
	    $(e).html(name)}
			    );
	$('.kolekti-job').addClass('hidden')
	$('.kolekti-job-'+name).removeClass('hidden')
	enable_save()
    });

    // contextual menus

    // modify topic / section

    $('body').on('click', '.btn_topic_edit', function(e) {
	var topic = $(this).closest('.topic');
	var url = topic.data('kolekti-topic-href');
	window.open('/topics/edit/?topic='+url);
	e.preventDefault();
    }) 

    $('body').on('click', '.btn_section_rename', function(e) {
	// get section title
	var title_elt = $(this).closest('.section')
	    .children('.panel-heading')
	    .children('')
	    .children('a');

	title_elt.after(
	    $('<input>',{
		"type":'text',
		"value":title_elt.children('span').html()
	    }).on('focusout',function(e){
		if ($(this).closest('tr').data('name')!= $(this).val()) {
		    var new_title=$(this).val();
		    title_elt.children('span').html(new_title);
		    enable_save();
		    $(this).remove();
		}
	    })
	);
	title_elt.children('span').html('');
	e.preventDefault();
    });	
    

    // move topic

    $('body').on('click', '.btn_topic_up', function(e) {
	var topic = $(this).closest('.topic');
	if (topic) {
	    if (topic.prev('.topic').length) {
		topic.insertBefore(topic.prev('.topic'));
		enable_save();
	    } else {
		var section = topic.closest('.section');
		if (section.length) {
		    var prev_section = section.prev('.section');
		    if (prev_section.length) {
			topic.appendTo(prev_section),
			enable_save();
		    } else {
			topic.insertBefore(section);
			enable_save();
		    }
		}
	    }
	} else {
	}
	e.preventDefault();
    });


    $('body').on('click','.btn_topic_down', function(e) {
	var topic = $(this).closest('.topic');
	if (topic) {
	    if (topic.next('.topic').length) {
		topic.insertAfter(topic.next('.topic'));
		enable_save();
	    } else {
		var next_section = topic.next('.section');
		if (next_section.length) {
		    var first_topic = next_section.find('.topic');
		    if (first_topic.length) {
			topic.insertBefore(first_topic[0]);
			enable_save();
		    } else {
			topic.appendTo(next_section),
			enable_save();
		    }
		} else {
		    var section = topic.closest('.section');
		    if (section.length) {
			var next_section = section.next('.section');
			if (next_section.length) {
			    var first_topic = next_section.find('.topic');
			    if (first_topic.length) {
				topic.insertBefore(first_topic[0]);
				enable_save();
			    } else {
				topic.appendTo(next_section),
				enable_save();
			    }
			}
		    }
		}
	    }
	}
	e.preventDefault();
    });

    $('body').on('click', '.btn_topic_insert_before', function(e) {
	var topic = $(this).closest('.topic');
	newcomp(topic, false);
	e.preventDefault();
    });

    $('body').on('click', '.btn_topic_insert_after', function(e) {
	var topic = $(this).closest('.topic');
	newcomp(topic,true);
	e.preventDefault();
    });
    
    // remove topic

    $('body').on('click', '.btn_topic_delete', function(e) {
	var topic = $(this).closest('.topic');
	if (topic)
	    topic.remove();
	else 
	    $(this).closest('.section').remove();
	enable_save();
	check_empty();
	e.preventDefault();
    });

    
    var create_topic_obj = function(path, id, topic) {

	var topicfile = displayname(path);

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
					'html':topicfile
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


    // handles dialog for insertion of topics & sections

    var newcomp = function(comp, isafter) {
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

	var select_topic_browser = function(e) {
	    e.preventDefault();
	    $('.insert-buttons a').removeClass('active');
	    $('.modal .btn-insert-module').addClass('active');
	    $('.modal-footer').off('click', '.browservalidate');

	    kolekti_browser(
		{'root':'/sources/'+kolekti.lang+'/topics',
		 'parent':".insert-main",
		 'titleparent':".new-module-title",
		 'create_actions':'yes',
		 'create_builder':create_builder
		}).select(function(path) {
		    $.get(path).success(
			function(data){
			    var topic = $.parseXML( data ),
			    id = Math.round(new Date().getTime() + (Math.random() * 100)),
			    topic_obj = create_topic_obj(path, id, topic);
			    if (isafter) 
				comp.after(topic_obj);
			    else 
				comp.before(topic_obj)
			    $("#toc_root>button").remove();
			    usecases(topic_obj);
			    enable_save();
			    $('.modal').modal('hide');
			})
		})
		.create(create_topic)

	    $('.insert-main').on('click', '.tpl-item',function(e){
		e.preventDefault();
		$('.label-tpl').html($(this).data('tpl'))
		$('.label-tpl').data('tpl',$(this).data('tpl'));
	    })

	};

	// handle add  topic : select topic

	// $('.modal').on('click','.btn-insert-module', select_topic_browser);


	// handles add section : get section title & update structure

	$('.modal').on('click','.btn-insert-section', function(e) {
	    e.preventDefault();
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
		    'class':"btn btn-default",
		    'html':"Insérer"
		}).one('click', function(e) {})

	    ]);
	    
/*
	    $('.modal-footer').on('click', '.browservalidate', function(event) {
		console.log("add section")
	    });	
*/
	})

	// handles add toc (if not already exists)
	
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
		    comp.after(topic_obj)
		else 
		    comp.before(topic_obj)
		$("#toc_root>button").remove();
		enable_save();
		$('.modal').modal('hide');
	    });	
	}

	// handles add index (if not already exists)

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
		    comp.after(topic_obj)
		else 
		    comp.before(topic_obj)
		$("#toc_root>button").remove();
		enable_save();
		$('.modal').modal('hide');
	    });	
	}
	/*
	if (!$('.modal-footer>button.browservalidate').length)
	    $('<button type="button" class="btn btn-default browservalidate">Valider</button>').prependTo($('.modal-footer'));
	*/
	select_topic_browser({'preventDefault':function(){}});

	// display dialog
	$('.modal').modal();
    }

    // end insert dialog


    // finalize UI by adding menus to topics

    $('.topic').each(function(i,t){
	($(t).data('kolekti-topic-rel')=='kolekti:toc' || $(t).data('kolekti-topic-rel')=='kolekti:index')
	    && topicmenu($(t));
    });

    $('a').each(function(i,comp) {
	if($(comp).attr('rel')=="kolekti:topic") {
	    var path = $(this).data('kolekti-topic-url');
	    $.get(path)
		.done(
		    function(data){
			if (data instanceof Document)
			    var topic = data;
			else
			    var topic = $.parseXML( data );
			var id = Math.round(new Date().getTime() + (Math.random() * 100));
			var topic_obj = create_topic_obj(path, id, topic);
			$(comp).after(topic_obj)
			usecases(topic_obj);
			$(comp).detach()

		    }
		);
	}
    });

    $('.section').each(function(i,t){
	topicmenu($(t));
    });
    check_empty();
})