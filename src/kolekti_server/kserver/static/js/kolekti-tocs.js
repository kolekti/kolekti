
// highlight and enable save button
// should be called after sucessfully performing any mofication on toc
var enable_save = function() {
    $('#btn_save').removeClass('disabled');
    $('#btn_save').removeClass('btn-default');
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
	    'html' :$('<span>', {
		'class':"btn-group",
		'html':[
		    (topic.data('kolekti-topic-rel')=='kolekti:topic' || topic.hasClass('section'))?$('<button>', {
			'type':"button",
			'class':"btn btn-primary btn-xs btn_topic_edit",
			'html':[
			    $('<span>',{
				'class':"glyphicon glyphicon-pencil",
				'html':" "}),
			    " Modifier "
			]}):"",
		    $('<button>', {
			'type':"button",
			'class':"btn btn-primary btn-xs dropdown-toggle",
			'data-toggle':"dropdown",
			'html':[
			    $('<span>',{
				'class':"glyphicon glyphicon-cog",
				'html':" "}),
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
	})
    );
}

var usecases = function(path) {
    var listpath = []
    if( path== undefined) {
	$('div[data-kolekti-topic-rel="kolekti:topic"]').each(function(i,e) {
	    listpath.push($(e).data('kolekti-topic-href'))
	});
    } else {
	listpath.push(path)
    };
    var tocref=$('#toc_root').data('kolekti-path');
    $.get('/tocs/usecases/',{"pathes":listpath}).
	success(function(data){ 
	    $('.topic').each(function(i,topic) {
		var topicref = $(topic).data('kolekti-topic-href');
		if (data[topicref]) {
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
		}
	    });
	})
}

usecases();

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
	$('#btn_save').removeClass('btn-warning');
    });
})

// publish

$('.btn_publish').on('click', function() {
    var url='/publish/'
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
    $('.publish_job').each(function(i,e){
	if (e.checked) {
	    var job = $(e).data('kolekti-job');
	    var idjob = $(e).attr('id');
	    var label = $(e).data('kolekti-jobname');
	    $('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a data-toggle="collapse" href="#collapse'+idjob+'">Job '+label+'</a></h4></div><div id="collapse'+idjob+'" class="panel-collapse collapse in"><div class="panel-body"><div id="pub_'+idjob+'"><div class="progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Publication in progress</span></div></div></div></div></div>').appendTo($('#pubresult'));

	    $.ajax({
		url:url,
		type:'POST',
		data:{'toc':toc, 'job':job}
	    }).done(function(data) {
		$('#pub_'+idjob).html(data);
	    });
	}
    });
})

// display

$('#btn_collapse_all').on('click', function() {
    $('.topic .collapse').collapse('hide');
});

$('#btn_expand_all').on('click', function() {
    $('.topic .collapse').collapse('show');
});

// diagnostic

$('#btn_audit').on('click', function() {
    kolekti_browser({'root':'/sources'})
	.select(function(path) {console.log(path)})
	.always(function() {console.log("after")})
    ;
});



// contextual menus

// modify topic / section

$('body').on('click', '.btn_topic_edit', function() {
    var topic = $(this).closest('.topic');
    if (topic.length) {
	var url = topic.data('kolekti-topic-href');
	window.open('/topics/edit/?topic='+url);
    } else {
	// get section title
	var title_elt = $(this).closest('.section')
	    .children('.panel-heading')
	    .children('')
	    .children('a');
	// change section title
	$('.modal-title').html('Renommer');
	$('.modal-footer')
	$('.modal-body').html($('<input>', {
	    'type':'text',
	    'id':'input_section_title',
	    'placeholder':title_elt.text()
	}))
	if (!$('.modal-footer>button.browservalidate').length)
	    $('<button type="button" class="btn btn-default browservalidate">Valider</button>').prependTo($('.modal-footer'));
	$('.modal-footer').off('click', '.browservalidate');
	$('.modal-footer').on('click', '.browservalidate', function(){
	    title_elt.html($('#input_section_title').val());
	    enable_save();
	    $('.modal').modal('hide')	    
	});	
	$('.modal').modal()
    }
})
	    

// move topic

$('body').on('click', '.btn_topic_up', function() {
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
});


$('body').on('click','.btn_topic_down', function() {
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
});

$('body').on('click', '.btn_topic_insert_before', function() {
    var topic = $(this).closest('.topic');
    newcomp(topic, false);
});

$('body').on('click', '.btn_topic_insert_after', function() {
    var topic = $(this).closest('.topic');
    newcomp(topic,true);
});

// remove topic

$('body').on('click', '.btn_topic_delete', function() {
    var topic = $(this).closest('.topic');
    if (topic)
	topic.remove();
    else 
	$(this).closest('.section').remove();
    enable_save();
});



// handles dialog for insertion of topics & sections

var newcomp = function(comp, isafter) {
    $('.modal-title').html('Insert Element');
    
    // builds dialog
    $('.modal-body').html(
	$('<div>', {
	"class":"row",
	"html":[
	    $("<div>", {
		"class":"col-sm-12 col-md-4",
		    "html":[
			$('<a>',{
				"class":"btn btn-block btn-default btn-insert-new-module",
				"href":"#",
				"html":"Creer module"
			    }),
			$('<a>',{
				"class":"btn btn-block btn-default btn-insert-module",
				"href":"#",
				"html":"Choisir module"
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
		"class":"col-sm-12 col-md-8 insert-main"
	    })
	]
	})
    );

    // handles new topic part : select model / select topic

    $('.modal').on('click','.btn-insert-new-module', function() {
	$('.modal-footer').off('click', '.browservalidate');
	$('.insert-main').html($('<div>',{
	    "html":[
		$('<div>',{
		    "class":"alert alert-info",
		    "html":$("<p>",{
			"class":"new-module-title",
			"html":"test&nbsp;"
		    })
		}),
		$('<div>',{
		    "class":"new-module-browser",
		})
	    ]}));

	kolekti_browser({'root':'/sources/'+kolekti.lang+'/topics',
			 'parent':".new-module-browser",
			 'title':"Sélectionnez un modèle",
			 'titleparent':".new-module-title"
			})
	    .select(function(path) {console.log(path)})
//	    .always(function() {console.log("after")})
    })

    // handle add existing topic : select topic

    $('.modal').on('click','.btn-insert-module', function(e) {
	$('.modal-footer').off('click', '.browservalidate');
	$('.insert-main').html($('<div>',{
	    'html':[
		$('<div>',{
		    "class":"alert alert-info",
		    "html":$("<p>",{
			"class":"new-module-title",
			"html":"&nbsp;"
		    })
		}),
		$('<div>',{
		    "class":"new-module-browser",
		})
	    ]}));

	kolekti_browser(
	    {'root':'/sources/'+kolekti.lang+'/topics',
	     'parent':".new-module-browser",
	     'title':"Sélectionnez le module à insérer",
	     'titleparent':".new-module-title"
	    }).select(function(path) {
		$.get('/static'+path).success(
		    function(data){
			var topic = $.parseXML( data ),
			id = Math.round(new Date().getTime() + (Math.random() * 100)),
			topic_obj = $('<div>', {
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
						'href':"#collapse_"+id,
						'html':$('<span>',{
						    'data-toggle':"tooltip", 
						    'data-placement':"top",
						    'title':path,
						    'html':$(topic).find('title').html()
						})
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
			if (isafter) 
			    comp.after(topic_obj)
			else 
			    comp.before(topic_obj)
			enable_save();
			$('.modal').modal('hide');
		    })
	    })
    });

    // handles add section : get section title & update structure

    $('.modal').on('click','.btn-insert-section', function() {
	$('.modal-footer').off('click', '.browservalidate');
	$('.insert-main').html([
	    $('<div>',{
		"class":"alert alert-info",
		"html":$("<p>",{
		    "html":"Nouvelle section"
		})
	    }),
	    $('<input>', {
		'type':'text',
		'id':'input_section_title',		
		'placeholder':'Titre de la section'
	    })
	]);
	
	$('.modal-footer').on('click', '.browservalidate', function(event) {
	    console.log("add section")
	});	

    })

    // handles add toc (if not already exists)
    
    if ($('#toc_root div[data-kolekti-topic-rel="kolekti:toc"]').length) {
	$('.modal .btn-insert-toc').addClass('disabled');
    } else {
	$('.modal').on('click','.btn-insert-toc', function() {
	    $('.modal-footer').off('click', '.browservalidate');
	    $('.insert-main').html($('<div>',{"class":"alert alert-info","html":$("<p>",{"html":"Validez pour insérer une table des matières"})}));
	    $('.modal-footer').on('click', '.browservalidate', function(event) {
		console.log("add toc")
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
		enable_save();
		$('.modal').modal('hide');
	    });	
	})
    }

    // handles add index (if not already exists)

    if ($('#toc_root div[data-kolekti-topic-rel="kolekti:index"]').length) {
	$('.modal .btn-insert-idx').addClass('disabled');
    } else {
	$('.modal').on('click','.btn-insert-idx', function() {
	    $('.modal-footer').off('click', '.browservalidate');
	    $('.insert-main').html($('<div>',{"class":"alert alert-info","html":$("<p>",{"html":"Validez pour insérer un index alphabétique"})}));
	    $('.modal-footer').on('click', '.browservalidate', function(event) {
		console.log("add index")
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
		enable_save();
		$('.modal').modal('hide');
	    });	
	})
    }
    if (!$('.modal-footer>button.browservalidate').length)
	$('<button type="button" class="btn btn-default browservalidate">Valider</button>').prependTo($('.modal-footer'));

    // display dialog
    $('.modal').modal();
}

// finalize UI by adding menus to topics

$('.topic').each(function(i,t){
    topicmenu($(t));
});

$('.section').each(function(i,t){
    topicmenu($(t));
});


