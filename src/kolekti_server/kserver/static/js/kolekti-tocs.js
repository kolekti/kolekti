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