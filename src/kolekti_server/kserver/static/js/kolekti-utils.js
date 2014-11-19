var kolekti = {
    'lang' : 'fr'
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

$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
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
     } 
});


var kolekti_browser = function(args) {
    var url = "/browse/";
    var params = {};
    var path="";
    var root ='/';

    var mode = "select";
    var parent = ".modal-body";
    var buttonsparent = ".modal-footer";
    var titleparent = ".modal-header h4";
    var title = "Navigateur de fichiers";
    var editable_path = false
    var titlepath = false
    var resfuncs = {};
    var modal = true;

    if (args && args.mode)
	mode = args.mode;
    if (args && args.root) {
	path = args.root;
        root = args.root;
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
    if (args && args.modal && args.modal=='no')
	modal = false;
    if (args && args.editable_path && args.editable_path=='yes')
	editable_path = true;

    params['mode']=mode;

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
	params['path']=path
	$.get(url, params, function(data) {
	    $(parent).html(
		$('<div>', {
		    'class':'panel panel-default',
		    'html':$('<div>', {
			'class':'panel-body',
			'html':[
			    data,
			    $('<div class="row' + ((mode == 'selectonly')?' hidden':'')+'"><label class="col-sm-2 control-label" for="browserval">'+(editable_path?'Chemin':'Nom')+'</label><div class="col-sm-10">  <input type="text" class="form-control browserfile " id="browserval"/></div></div>')]
		    })
		})
	    )
	}).done(function(){	
	    set_browser_value(path + '/');
	    if (modal)
		$('.modal').modal();
	});
    }

    var browser_alert = function(msg) {
	
	$(parent).find('.browser').append(
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

    var select = function(f) {	
	resfuncs['select']=f;
	return {"always":always};
    };

    var always = function(f) {
	resfuncs['always']=f;
    };

    // calls register callback functions

    var closure = function(f) {
	if (mode == "create")
	    $.get("/browse/exists", {'path':get_browser_value()}, function(data) {
		if (!data) {
		    $.map(resfuncs , function(v,i) {
			v(get_browser_value())
		    })
		} else {
		    browser_alert("Le fichier sélectionné existe deja")
		    return
		}
	    })
	else
	    $.map(resfuncs , function(v,i) {
		v(get_browser_value());
	    })
    };

    // click on file

    $(parent).on('click', '.filelink', function() {
	if ($(this).data('mimetype') == "text/directory") {
	    path = path +'/'+ $(this).html();
	    update();
	} else {
	    set_browser_value(path + '/' + $(this).html())
	    if (mode=="selectonly") {
		closure()
	    }
	}
    })

    // navigate into parent folders

    $(parent).on('click', '.pathstep', function() {
	var newpath = $(this).data("path");
	if (newpath.length >= root.length) {
	    path = newpath;
	    update();
	}
    })

    // new folder

    $(parent).on('click', '.create-folder', function() {
	folderpath = path + "/" + $(parent).find(".foldername").val();
	$.post("/browse/mkdir",{path : folderpath}, function(data) {
	    update();
	})
    })

    // Validate modal / browser

    $(parent).on('click', '.browservalidate', function() {
	closure();
    })

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
	bsort($(this).data('sortcol'),asc);
    })

    // sorting

    var bsort = function(col, asc) {		 
	var mylist = $(parent).find('.dirlist tbody');
	var listitems = mylist.children('tr').get();
	listitems.sort(function(a, b) {
	    var cmp = $(a).data('sort-'+col).toUpperCase().localeCompare($(b).data('sort-'+col).toUpperCase());
	    return asc?cmp:0-cmp;
	})
	$.each(listitems, function(idx, itm) { mylist.append(itm); });
    }

    // activate Validate button

    if (mode != "selectonly") {
	if (!$(buttonsparent+'>button.browservalidate').length) {
	    $('<button type="button" class="btn btn-default browservalidate">OK</button>').prependTo($(buttonsparent));
	}

	$(buttonsparent).off('click', '.browservalidate');
	$(buttonsparent).on('click', '.browservalidate', function(event) {
	    closure();
	});
    }

    // set title

    $(titleparent).html(title);
    
    // fetch directory

    update()
    
    // return functions

    return {
	"select":select,
	"always":always
    }
    
}


var radicalbasename = function(path) {
    var pathparts = path.split('/'),
    last = pathparts[pathparts.length - 1];
//    return last;
    return last.split('.')[0];
}

// events

