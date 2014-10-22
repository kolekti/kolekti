var enable_save = function() {
    $('#btn_save').removeClass('disabled');
    $('#btn_save').removeClass('btn-default');
    $('#btn_save').addClass('btn-warning');
}
 
$('#btn_collapse_all').on('click', function() {
    $('.main .collapse').collapse('hide');
});

$('#btn_expand_all').on('click', function() {
    $('.main .collapse').collapse('show');
});

$('.btn_topic_delete').on('click', function() {
    var topic = $(this).closest('.topic');
    topic.remove();
    enable_save();
});

$('#btn_topics_delete').on('click', function() {
    $('.select_topic').each(function(i,e) {
	if (e.checked) {
	    var topic = $(e).closest('.topic');
	    topic.remove();
	    enable_save();
	}
    });
});

var first_selected = function() {
    ft = $('.select_topic:checked').first();
    if (ft.length == 0)
	ft = $('.select_topic').first();
    return ft;
}

$('#btn_idx_add').on('click', function() {
    first_selected().each(function(i,e) {
	var topic = $(e).closest('.topic');
	$('<div class="topic" data-kolekti-topic-rel="kolekti:index"><div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><input type="checkbox" class="select_topic"> <a data-toggle="collapse" href="#collapse_idm290171584"><span data-toggle="tooltip" data-placement="top" title="Index alphabétique"><span class="glyphicon glyphicon-cog"></span>Index alphabétique</span></a> <span class="dropdown"><a data-toggle="dropdown" href="#" id="dropdownMenu_idmidx"><span class="caret"></span></a><ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu_idmidx"><li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_delete">Supprimer</a></li><li role="presentation" class="divider"></li><li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_up">Monter</a></li><li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_down">Descendre</a></li></ul></span></h4></div></div></div>').insertBefore(topic);
	    enable_save();
	    return;
    });
});

$('#btn_toc_add').on('click', function() {
    first_selected().each(function(i,e) {
	var topic = $(e).closest('.topic');
	$('<div class="topic" data-kolekti-topic-rel="kolekti:index"><div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><input type="checkbox" class="select_topic"> <a data-toggle="collapse" href="#collapse_idm290171584"><span data-toggle="tooltip" data-placement="top" title="Index alphabétique"><span class="glyphicon glyphicon-cog"></span>Index alphabétique</span></a> <span class="dropdown"><a data-toggle="dropdown" href="#" id="dropdownMenu_idmtoc"><span class="caret"></span></a><ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu_idmtoc"><li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_delete">Supprimer</a></li><li role="presentation" class="divider"></li><li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_up">Monter</a></li><li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_down">Descendre</a></li></ul></span></h4></div></div></div>').insertBefore(topic);
	    enable_save();
	    return;
    });
});

$('#btn_topic_add').on('click', function() {
    kolekti_browser({"type":"topics"})
	.select(function(path) {console.log(path)})
	.always(function() {console.log("after")})
    ;
/*
    $.get('/browser/sources/fr/topics', function(data) {   
        $('#').append(data);
    });
*/
});


$('.btn_topic_up').on('click', function() {
    var topic = $(this).closest('.topic');
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
});


$('.btn_topic_down').on('click', function() {
    var topic = $(this).closest('.topic');
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
});

var process_toc = function(elt) {
    var buf = '';
    var domelt = elt.get(0);
    if (elt.hasClass('topic')) {
	buf+="<a ";
	if(elt.data('kolekti-topic-href'))
	    buf += "href='" + elt.data('kolekti-topic-href') + "' ";
	buf += "rel='" + elt.data('kolekti-topic-rel') + "'/>";
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

$('#btn_save').on('click', function() {
    console.log(process_toc($('#toc_root')));
    $.ajax({
	url:'/tocs/edit/',
	type:'POST',
	data:process_toc($('#toc_root')),
	contentType:'text/plain'
    }).done(function(data) {
	console.log(data);
    });
})

$('#btn_publish').on('click', function() {
    var url='/publish/'
    if ($('#publish_release').get(0).checked) {
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

$('body').on('click', '.btn_topic_edit', function() {
    var topic = $(this).closest('.topic');
    var url = topic.data('kolekti-topic-href');
    
    window.open('/topics/edit/?topic='+url);
})