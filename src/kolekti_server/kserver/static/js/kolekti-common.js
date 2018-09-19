$(function() {
    
    // sets revision number
    
    $('#btn_rev').click(function(e) {
	    var url = Urls.kolekti_sync(kolekti.project);
	    window.location.href = url;
    })
    
    var setstatus = function(data) {
	    var color="default";
        
	    if (!data.hasOwnProperty('revision')) {
	        $('#btn_rev').removeClass('btn-default')
	        $('#btn_rev').addClass('btn-danger')
	        $('#btn_rev>span').addClass('strong')
	        $('#btn_rev').attr('title', 'impossible de contacter le serveur')
	        return
	    };
        
        $('#revnum').html(data.revision.revnum)
        
	    switch(data.revision.status) {
	    case '*':
		    color="warning"
		    $('#btn_rev').attr('title', gettext('vos modifications locales n\'ont pas été synchronisées'))
		    break;
	    case 'N':
		    color="default"
		    $('#btn_rev').attr('title', gettext('le projet est synchronisé'))
		    break;
	    case 'E':
		    color="danger"
		    $('#btn_rev').attr('title', gettext('une erreur est survenue'))
		    break;
	    case 'C':
		    color="danger"
		    $('#btn_rev').attr('title', gettext('le projet est en conflit'))
		    break;
	    case 'M':
		    color="warning"
		    $('#btn_rev').attr('title', gettext('des modifications locales n\'ont pas été synchronisées, des mises à jour sont disponibles'))
		    break;
	    case 'U':
		    color="warning"
		    $('#btn_rev').attr('title', gettext('mise a jour disponible'))
		    break;
	    }
	    $('#btn_rev>span span.spinner').hide()
	    if (color != 'default') {
		    $('#btn_rev').removeClass('btn-default')
		    $('#btn_rev').addClass('btn-'+color)
		    $('#btn_rev>span').addClass('strong')
		    $('#btn_rev>span span.circle').show()
	    }
    }

    var pendingstatusrequest = false;
    
    var updatestatus = function(e) {
	    if (pendingstatusrequest)
	        return
	
	    var cached_status = sessionStorage.getItem('kolektistatus');
	    var now = new Date()
	    if(cached_status != null) {
	        cached_status = JSON.parse(cached_status);
	        if (cached_status['project'] == kolekti.project) {
		        if(cached_status['time'] > (now.getTime() - 10000)){
		            setstatus(cached_status['status'])
                    console.log('cached')
		            return;
		        }
	        }
	    }
        pendingstatusrequest = true;
        
	    $('#btn_rev>span span.circle').hide()
	    $('#btn_rev>span span.spinner').show()
	    $('#btn_rev>span').removeClass('strong')
	    $('#btn_rev').removeClass('btn-success btn-warning btn-danger btn-info')
	    $('#btn_rev').addClass('btn-default')
	    
        var url = Urls.kolekti_sync_status(kolekti.project)
	    $.get(url).done(function(data){
	        var now = new Date()
	        cached_status = {
		        'project':kolekti.project,
		        'time':now.getTime()
	        }
	        cached_status['status'] = data;
	        cached_status['revnum'] = data.revision.revnum;
	        setstatus(data)
	        sessionStorage.setItem('kolektistatus',JSON.stringify(cached_status))
	    }).always(function() {
	        pendingstatusrequest = false;
	    })
    }
    
    var pendingrevnumrequest = false;
    
    var updaterevnum = function(e) {
	if(pendingrevnumrequest)
	    return
        var url = Urls.kolekti_sync_remote_status(kolekti.project)
	    $.get(url).done(function(data){
	        if (data.revision)
	            $('#revnum').html(data.revision.number);
	    })
    }
    
    $(window).focus(function(){
	    updatestatus();
	    updaterevnum();
    });
    $(window).on('kolektibrowserchange',function(){
	    updatestatus();
	    updaterevnum();
    });
    updatestatus();
    updaterevnum();

    $(window).kolekti_status = function(data) {
        $('footer p').attr('class', 'bg-danger');
        $('footer p').html(' ')
    }
    
    // history

    $('.btn-back').on('click', function() {
	window.history.back();
    })
	
    // menu selection filter

    $('body').on('click',".input-filter-menu", function(e) {
	e.stopPropagation()
    });

    // filterable menus
    
    $('body').on('keyup',".input-filter-menu", function(e) {
	var filter = this.value.toLowerCase();
	var filterable = $($(this).data('filter-list'))
	if (filterable.length == 0)
	    filterable = $(this).closest('ul')
	
	filterable.find('.filterable')
	    .each(function() {
		$(this).show();
		var itemval = $(this).attr('data-filter-value').toLowerCase();
		if (! itemval.startsWith(filter))
		    $(this).hide();
	    });
    });

    $(document).on('shown.bs.dropdown','.filterable-menu', function () {
	$(this).find('.input-filter-menu').val('');
	$(this).find('.input-filter-menu').focus();
	$(this).find('.filterable')
	    .each(function() {
		$(this).show()
	    });
    });	 

    window.KOLEKTI_STATE_DONE = 0
    window.KOLEKTI_STATE_WAIT = 1
    window.KOLEKTI_STATE_OK = 2
    window.KOLEKTI_STATE_INFO = 3
    window.KOLEKTI_STATE_WARN = 4
    window.KOLEKTI_STATE_ERROR = 5
    
    window.kolekti_status = function(state, message, callback) {
        switch (state) {
        case window.KOLEKTI_STATE_OK:
            $('#toaster button').attr('class','btn btn-xs btn-success')
            break;
        case window.KOLEKTI_STATE_INFO:
            $('#toaster button').attr('class','btn btn-xs btn-info')
            break;
        case window.KOLEKTI_STATE_WARN:
            $('#toaster button').attr('class','btn btn-xs btn-warning')
            break;
        case window.KOLEKTI_STATE_ERROR:
            $('#toaster button').attr('class','btn btn-xs btn-danger')
            break;
        default:
            $('#toaster button').attr('class','btn btn-xs btn-default')
        }
        
        if (state == window.KOLEKTI_STATE_WAIT) {
            $('#toaster .spinner').show()
        } else {
            $('#toaster .spinner').hide()
        }
        
        if (message) {
            $('#toaster .msg').html(message);
            $('#toaster .msg').show();
        } else {
            $('#toaster .msg').hide();
        }
        $('#toaster').off('click')
        $('#toaster').on('click', function() {
            if (callback)
                callback()
            else
                $('#toaster').removeClass('in')
        })
                         
        
        if (state == window.KOLEKTI_STATE_DONE) {
            $('#toaster').removeClass('in')
        } else {
            $('#toaster').addClass('in')
        }

        if (state == window.KOLEKTI_STATE_OK || state == window.KOLEKTI_STATE_INFO) {
            window.setTimeout(function() {
                $('#toaster').removeClass('in')
            }, 2000)
        }
    }
    
})

var formatTime = function(unixTimestamp) {
    var dt = new Date(unixTimestamp * 1000);

    return dt.toLocaleString();
}


var kolekti_recent = function(name, info, url) {
    if (localStorage) {
	    var storage = "kolekti-recent-"+ window.kolekti.project;
	    var stored = JSON.parse(localStorage.getItem(storage))
	    if (stored == null) stored = [];
	    stored.unshift({'name':name, 'info':info, 'url':url, 'time':Date.now()/1000})
	    localStorage.setItem(storage, JSON.stringify(stored))
    }
}
