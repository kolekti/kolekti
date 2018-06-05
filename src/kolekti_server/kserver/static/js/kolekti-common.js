$(function() {

    // sets revision number
    
    $('#btn_rev').click(function(e) {
	var url = '/sync/';
	window.location.href = url;
    })

    var setstatus = function(data) {
	    var color="default";
	// console.log(data.revision.status);
	if (!data.hasOwnProperty('revision')) {
	    $('#btn_rev').removeClass('btn-default')
	    $('#btn_rev').addClass('btn-danger')
	    $('#btn_rev>span').addClass('strong')
	    $('#btn_rev').attr('title', 'impossible de contacter le serveur')
	    return
	}
	switch(data.revision.status) {
	    case '*':
		color="warning"
		$('#btn_rev').attr('title', 'vos modifications locales n\'ont pas été synchronisées')
		break;
	    case 'N':
		color="default"
		$('#btn_rev').attr('title', 'le projet est synchronisé')
		break;
	    case 'E':
		color="danger"
		$('#btn_rev').attr('title', 'une erreur est survenue')
		break;
	    case 'C':
		color="danger"
		$('#btn_rev').attr('title', 'le projet est en conflit')
		break;
	    case 'M':
		color="warning"
		$('#btn_rev').attr('title', 'des modifications locales n\'ont pas été synchronisées, des mises à jour sont disponibles')
		break;
	    case 'U':
		color="warning"
		$('#btn_rev').attr('title', 'mise a jour disponible')
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
        return
	    if (pendingstatusrequest)
	        return
	
	    var cached_status = sessionStorage.getItem('kolektistatus');
	    var now = new Date()
	    if(cached_status != null) {
	        cached_status = JSON.parse(cached_status);
	        if (cached_status['project'] == kolekti.project) {
		        if(cached_status['time'] > (now.getTime() - 60000)){
		            $('#revnum').html(cached_status['revnum'])
		            setstatus(cached_status['status'])
		            return;
		        }
	        }
	    }
	    $('#btn_rev>span span.circle').hide()
	    $('#btn_rev>span span.spinner').show()
	    $('#btn_rev>span').removeClass('strong')
	    $('#btn_rev').removeClass('btn-success btn-warning btn-danger btn-info')
	    $('#btn_rev').addClass('btn-default')
	    
	    pendingstatusrequest = true;
	    $.get('/sync/status').done(function(data){
	        var now = new Date()
	        cached_status = {
		        'project':kolekti.project,
		        'time':now.getTime()
	        }
	        cached_status['status'] = data;
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
	    $.get('/sync/remotestatus').done(function(data){
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

    // history

    $('.btn-back').on('click', function() {
	window.history.back();
    })
	
    // menu selection filter

    $('body').on('click',".input-filter-menu", function(e) {
	e.stopPropagation()
    });
    
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
