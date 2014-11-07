var kolekti = {
    'lang' : 'fr'
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

    var mode = "select";
    var parent = ".modal-body";
    var buttonsparent = ".modal-footer";
    var titleparent = ".modal-header h4";
    var title = "Navigateur de fichiers";
    var resfuncs = {};

    if (args && args.mode)
	mode = args.mode;
    if (args && args.root)
	path = args.root;
    if (args && args.parent)
	parent = args.parent;
    if (args && args.buttonsparent)
	buttonsparent = args.buttonsparent;
    if (args && args.titleparent)
	titleparent = args.titleparent;
    if (args && args.title)
	title = args.title;



    var update = function() {
	$.get(url+"?path="+path, function(data) {
	    $(parent).html(data);
	}).done(function(){	
	    $('.modal').modal();
	});
    }

    var select = function(f) {	
	resfuncs['select']=f;
	return {"always":always};
    };

    var always = function(f) {
	resfuncs['always']=f;
    };

    var closure = function(f) {
	$.map(resfuncs , function(v,i) {
	    v($(".browserfile").val())
	})
    };

    $(parent).on('click', '.filelink', function() {
	if ($(this).data('mimetype') == "text/directory") {
	    path = path +'/'+ $(this).html();
	    update();
	} else {
	    $(".browserfile").val(path + '/' + $(this).html());
	}
    })

    $(parent).on('click', '.pathstep', function() {
	path = $(this).data("path");
	update();
    })

    $(parent).on('click', '.browservalidate', function() {
	closure();
    })

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

    var bsort = function(col, asc) {		 
	var mylist = $('.dirlist tbody');
	var listitems = mylist.children('tr').get();
	listitems.sort(function(a, b) {
	    var cmp = $(a).data('sort-'+col).toUpperCase().localeCompare($(b).data('sort-'+col).toUpperCase());
	    console.log(cmp)
	    return asc?cmp:0-cmp;
	})
	$.each(listitems, function(idx, itm) { mylist.append(itm); });
    }

    
    if (!$(buttonsparent+'>button.browservalidate').length) {
	$('<button type="button" class="btn btn-default browservalidate">OK</button>').prependTo($(buttonsparent));
    }
    $(buttonsparent).off('click', '.browservalidate');
    $(buttonsparent).on('click', '.browservalidate', function(event) {
	closure();
    });
    

    $(titleparent).html(title);

    update()
    return {
	"select":select,
	"always":always
    }
    
}

// events

