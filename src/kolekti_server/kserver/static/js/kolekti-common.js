$(function() {

    // sets revision number
    
    $('#btn_rev').click(function(e) {
	var url = '/sync/';
	window.location.href = url;
    })
    $.get('/sync/status').done(function(data){
	var color="default";
	// console.log(data.revision.status);
	switch(data.revision.status) {
	case '*':
	    color="info"
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
	    color="warning"
	    $('#btn_rev').attr('title', 'le projet est en conflit')
	    break;
	case 'M':
	    color="warning"
	    $('#btn_rev').attr('title', 'des modifications locales n\'ont pas été synchronisées, des mises à jour sont disponibles')
	    break;
	case 'U':
	    color="info"
	    $('#btn_rev').attr('title', 'mise a jour disponible')
	    break;
	}
	$('#btn_rev>span span').hide()
	$('#btn_rev>span').removeClass('strong text-success text-default text-warning text-danger text-info')
	$('#btn_rev>span').addClass('text-'+color)
	if (color != 'default') {
	    $('#btn_rev>span span').show()
	}
    })

    // history

    $('.btn-back').on('click', function() {
	window.history.back();
    })
	
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
