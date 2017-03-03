$(function() {
    $('#invite_email_btn').on('click', function(e) {
	e.preventDefault();
	var email = $( "#invite_email" ).val();
	$.post('/invitations/send-json-invite/',
	       JSON.stringify([email])
	      )
	    .done(function(data){
		$('#invitation').closest('.alert').removeClass('alert-warning')
		$('#invitation').closest('.alert').addClass('alert-success')
		$('#invitation').html(email + ' invited')
	    })
	
 	    .error(function(data){
		try {
		    $('#invitation').closest('.alert').addClass('alert-danger')
		    $('#invitation').html(email + ": " + data.responseJSON.invalid[0][email])
		}
		catch(e) {
		    $('#invitation').closest('.alert').removeClass('alert-warning')
		    $('#invitation').closest('.alert').addClass('alert-danger')
		    $('#invitation').html("Could not connect to server")
		}
	    })
    })
})
