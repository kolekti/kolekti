$(document).ready(function() {
    var widgets=[];					    
    var widget = function(wdef) {
	var w = $('<div>', {
	    "class":"col-xs-12 col-sm-6 col-md-4",
	    "html":$('<div>', {
		"class":"panel panel-primary",
		"html":[
		    $('<div>', {
			"class":"panel-heading",
			"html":wdef.title
		    }),
		    wdef.content()
		]
	    })
	})
	$('#widgets').append(w);
	return w
    }


    var publication_widget_builder = function(url, wdiv) {
	var wdiv = $('<ul>', {
	    "class":"list-group panel-body ",
	});
	$.getJSON(url, function(data) {
	    $.each(data.publications, function( i, pub ) {
		wdiv.append($('<li>', {
		    "class":"list-group-item",
		    "html":[
			$('<h4>',{'html':pub.path}),
			$('<p>',{html:formatTime(pub.time)}),
			$('<div>',{
			    html:
			    $.map(pub.content, function(ev, iev) {
				if (ev.event == "error")
				    return $('<div>', {
					"class" : "panel panel-alert",
					"html": ev.msg
				    });
				if (ev.event == "lang") 
				    return $('<h4>', {
					"html":$('<em>',{
					    "html":ev.label
					})
				    });
				if (ev.event == "toc" && pub.event == "publication") 
				    return $('<p>', {"html": "Trame : " + ev.file});
				if (ev.event == "job" && pub.event == "publication") 
				    return $('<p>', {"html": "Parametres : " + ev.label});
				if (ev.event == "profile" && pub.event == "publication")
				    return $('<h5>', {"html": "Profil " + ev.label});
				if (ev.event == "result") 
				    return $('<ul>', {
					"html":$.map(ev.docs, function(doc) {
					    return $('<li>', {
						'html': [$('<span>', {"class" : "padright",
								      'html':doc.type + ' :'}),
							 $('<a>', {
							     'href': doc.url,
							     'target':"_blank",
							     'html': doc.label
							 })
							]
					    })
					})
				    })
			    })
			})
		    ]
		}));
	    });
	})
	return wdiv;
    }
    



    var widgets_definitions = {
	'publications':{'title':'Dernières publications',
			'content':function() {
			    return publication_widget_builder('/publications/list.json');
			}
		       },
	'releases':{'title':'Dernières publications (versions)',
		    'content':function() {
			return publication_widget_builder('/releases/publications/list.json')
		    }
		   }
    }
	
    if (localStorage) {
	var widgets_names, widgets_stored = localStorage.getItem("widgets")
	widgets_stored = false;
	if (widgets_stored)
	    widgets_names = widgets_stored.split(',')
	else
	    widgets_names = ["publications",'releases'];
	$.each(widgets_names, function(i,wn) {
	    widgets.push(widget(widgets_definitions[wn]))
	});
	localStorage.setItem("widgets", widgets_names.join(','))
    }
})



	    
