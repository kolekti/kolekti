$(function() {
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
	    break;
	case 'N':
	    color="default"
	    break;
	case 'E':
	    color="danger"
	    break;
	case 'C':
	    color="warning"
	    break;
	case 'M':
	    color="warning"
	    break;
	case 'U':
	    color="info"
	    break;
	}
	$('#btn_rev').removeClass('btn-success btn-default btn-warning btn-danger btn-info')
	$('#btn_rev').addClass('btn-'+color)
    })
	
})

var formatTime = function(unixTimestamp) {
    var dt = new Date(unixTimestamp * 1000);

    return dt.toLocaleString();
}
