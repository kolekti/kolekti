$(function() {

    // sets revision number
    
    $('#btn_rev').click(function(e) {
	var url = '/sync/';
	window.location.href = url;
    })

    var updatestatus = function(e) {
	$('#btn_rev>span span.circle').hide()
	$('#btn_rev>span span.spinner').show()
	$('#btn_rev>span').removeClass('strong')
	$('#btn_rev').removeClass('btn-success btn-warning btn-danger btn-info')
	$('#btn_rev').addClass('btn-default')
	$.get('/sync/status').done(function(data){
	    var color="default";
	    // console.log(data.revision.status);
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
	})
	$.get('/sync/remotestatus').done(function(data){
	    $('#revnum').html(data.revision.number);
	})
    }
    
    $(window).focus(updatestatus);
    $(window).on('kolektibrowserchange',updatestatus);
    updatestatus();


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
	$(this).closest('ul').find('li.filterable')
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
	$(this).find('li.filterable')
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
