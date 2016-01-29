$(document).ready(function() {
    var list_main=[];
    var list_side=[];
    var widgets = [];
    
    var widget = function(wdef, where) {
	var w = $('<div>', {
	    "class":"col-md-8",
	    "html":$('<div>', {
		"class":"panel panel-primary",
		"html":[
		    $('<h4>', {
			"class":"panel-body text-primary ",
			"html":wdef.title
		    }),
		    wdef.content()
		]
	    })
	})
	
	$('#widgets_'+where).append(w);
	return w
    }

    var widget_loader = function(url, wdiv) {
	var wdiv = $('<div>', {
	    "class":"widget",
	});
	$.get(url, function(data) {
	    wdiv.html(data)
	})
	return wdiv;
    }
    
    var publication_widget_builder = function(url) {
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
	'releases':{'title':'Dernières versions',
		    'content':function() {
			return publication_widget_builder('/releases/publications/list.json')
		    }
		   },
	'projecthistory':{'title':'Historique du projet',
			   'content':function() {
			       return widget_loader('/widgets/project-history/')
			   }
			  }
    }
	
    if (localStorage) {
	var sto_main = localStorage.getItem("widgets_main")
	var sto_side = localStorage.getItem("widgets_side")
	console.log(sto_main)
	if (sto_main != null && sto_main.length)
	    list_main = sto_main.split(',')
	else
	    list_main = ["publications",'releases'];
	
	if (sto_side != null && sto_side.length)
	    list_side = sto_side.split(',')
	else
	    list_side = ['projecthistory'];
	
	$.each(list_main, function(i,wn) {
	    widgets.push(widget(widgets_definitions[wn],'main'))
	});
	localStorage.setItem("widgets_main", list_main.join(','))
	
	$.each(list_side, function(i,wn) {
	    widgets.push(widget(widgets_definitions[wn],'side'))
	});
	localStorage.setItem("widgets_side", list_side.join(','))
    }
})



	    
