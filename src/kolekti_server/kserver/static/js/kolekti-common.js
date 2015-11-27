$(function() {
    $('#btn_rev').click(function(e) {
	var url = '/sync/';
	window.location.href = url;
    })
})

var formatTime = function(unixTimestamp) {
    var dt = new Date(unixTimestamp * 1000);

    return dt.toLocaleString();
}
