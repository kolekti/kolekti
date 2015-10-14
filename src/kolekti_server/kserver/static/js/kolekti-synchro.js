
$(document).ready(function() {
    
    $('#selectall').change(function() {
	$('.selectentry').prop('checked',$(this).prop('checked'))
	check_action()
    });
    var check_action = function(e) {
	if ($('.selectentry').length) {
	    var map = $('.selectentry').filter(function() { return $(this).prop('checked')})
	    if(map.length == 0) 
		$('.btn-action-synchro').addClass('disabled')
	    else
		$('.btn-action-synchro').removeClass('disabled')
	}
    };
		  
    $('body').on('change','.selectentry',check_action);
    check_action()

		  
    $('body').on('change','select',function(e) {
	var val = $(this).val();
	if (val == "local" || val == "merge") {
	    $("#commitmsg").show();
	} else {
	    $("#commitmsg").hide();
	}
    });
		 
    $('body').on('click','.btn-select-merge',function(e) {
	action = $('.select-merge').val();
	console.log(action);
	$('.entry-merge:selected').each(function(i,e) {
	    $.post('/sync/merge/'+action, {
		'path':$(this).data('path')
	    })
		.done(function(data) {
		    $('.modal-body').append($(data))
		});
	    $('.modal-title').html('Synchronisation')		
	    $('.modal-footer').html(
		$('<button>',{
		    "class":"btn btn-default", 
		    "html":"fermer"})
		    .on('click',function() { window.location.reload()})
		)
	    $('.modal').modal();
	});
    });

    $('body').on('click','.btn-select-conflit',function(e) {
	action = $('.select-confilt').val();
	console.log(action);
	$('.entry-conflit:selected').each(function(i,e) {
	    $.post('/sync/conflit/'+action, {
		'path':$(this).data('path')
	    })
		.done(function(data) {
		    $('.modal-body').append($(data))
		});
	    $('.modal-title').html('Synchronisation')		
	    $('.modal-footer').html(
		$('<button>',{
		    "class":"btn btn-default", 
		    "html":"fermer"})
		    .on('click',function() { window.location.reload()})
		)
	    $('.modal').modal();
	});
    });

    $('body').on('click','.dosynchro',function(e) {
	console.log('synchro');
	
	$.post('/sync/'+$(this).data('action'), {
	    'syncromsg':$('#syncromsg').val()
	})
	    .done(function(data) {
		$('.modal-title').html('Synchronisation')		
		$('.modal-body').html(data)
		$('.modal-footer').html(
		    $('<button>',{
			"class":"btn btn-default", 
			"html":"fermer"})
			.on('click',function() { window.location.reload()})
		)
    		$('.modal').modal();
	    })
    })

    $('#syncromsg').focus()    
})
