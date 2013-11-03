
$(function() {
    var displaynode = function(path, node) {
	var ulclass,
	i = $.map(node, function(v,k) {
	    if (k == ".svn") return '';
	    return $("<li>",{html:
			     (v==null)?[
				 $('<a>', {
				     "class" : "file",
				     href: "/ui" + path + '/' + k,
				     html: k
				 })
			     ]:[
				 $('<a>', {
				     "class" : "dir",
				     href: "#", //path + '/k',
				     html: k
				 }),
				 displaynode(path + "/" + k, v)
			     ]
			    });
	});
	//	console.log(path);
	
	if (path == "") 
	    ulclass = "nav bs-sidenav"
	else
	    ulclass = "nav"
	return $('<ul>',
		 {
		     "class":ulclass,
		     html:i
		 }
		);
    }

    $.getJSON('/xhr/tree/sources/'+kolekti.lang, function(data) {
	console.log(data);
	$('.index_base').append(displaynode('/sources/'+kolekti.lang,data[0]));
	$('.index_base [href=#]').click(function (e) {
	    $(this).parent().toggleClass("active");
	    e.preventDefault()
	})
/*
	$('.index_trames').append(displaynode(data[0]['trames']));
	$('.index_modules').append(displaynode(data[0]['modules']));
	$('.index_images').append(displaynode(data[0]['images']));
	$('.index_lancements').append(displaynode(data[0]['configuration']['orders']));
*/
    });
    if (kolekti.resource.length && kolekti.resource.length > 1)
    $.get(kolekti.resource, function(data) {
	$("#mainpanel").html(data);
	$("#mainpanel").attr('data-mercury',"full");
	$("#mainpanel>title").remove();
	$("#mainpanel>meta").remove();

	$(window).on('mercury.ready', function() {
	    Mercury.trigger('reinitialize');
	})
	try {
	    Mercury.trigger('reinitialize');
	} catch(e) {}
    })
});
