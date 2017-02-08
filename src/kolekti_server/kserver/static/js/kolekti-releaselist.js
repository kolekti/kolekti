$(document).ready(function() {

    kolekti_browser({'root':'/releases',
		     'url':"/browse/releases/",
		     'parent':".browser",
		     'title':" ",
		     'titleparent':".title",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_action_delete':'yes'
		    })
	.select(
	    function(path) {
		document.location.href = '/releases/detail/?release='+path+'&lang='+kolekti.lang
		
/*
		$.get('/releases/detail/',{'path':path})
		.success(function(data) {
		$('#detail_release').html($(data));
		})
		//	document.location.href = '/release/detail/?release='+path
		*/
	    })
    
	.setup(function(){
	    console.log('browser loaded');	    
	    $('.kolekti-browser-release-state').each(function() {
		console.log($(this).closest('tr'));
		var releasepath = $(this).closest('tr').data('name')
		var statecell = $(this)
		console.log(releasepath)
		$.getJSON('/releases/states/?release=/release/'+releasepath)
		    .success(function(data) {
			$.each(data, function(index,item) {
			    var i = item[0]
			    var v = item[1]
			    console.log(i,v,this)
			    if (v)
				statecell.append($('<span>',{
				    "class":"langstate "+v,
				    "html":$('<a>',{
					"href":"/releases/detail/?release=/releases/"+releasepath+"&lang="+i,
					"html":i
				    })
				}))
			})	      
					       
			console.log(data)
		    })
	    });
	});


    $('body').on('click', '.dirtoggle', function(e) {
	e.preventDefault()
	var toggle = $(this).closest('tr').find('.kolekti-browser-icon i.hidden');
	toggle.removeClass('hidden');
	if (toggle.hasClass('fa-folder-open')) {
	    $(this).closest('tr').find('.kolekti-browser-icon i.fa-folder').addClass('hidden');
	} else {
	    $(this).closest('tr').find('.kolekti-browser-icon i.fa-folder-open').addClass('hidden');
	}
	var row = $(this).closest('tr')
	while (row.length) {
	    row = row.next('.release-index');
	    if (toggle.hasClass('fa-folder-open')) {
		row.removeClass('hidden')
	    } else {
		row.addClass('hidden')
	    }
	}
    });

})
