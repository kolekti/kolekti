$(document).ready(function() {
    var conditions = kolekti_variable_data['conditions'];
    var path = $('#main').data('path');

    // add condition 

    var exists_condition = function(callback_true) {
	var exists = false;
	$.each(conditions, function(i,v){
	    console.log(i,v);
	    callback_true();
	});
	return exists;
    }

    
    $('#modal_cond .cond_item').on('click', function() {
	// condition menu
	console.log($(this).data('valuelabel'))
	console.log($(this).closest('.btn-group'));
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	exists_condition(function() {$('.msg-exist').show()})
    })
    
    $('#modal_add_crit .crit_cond_item').on('click', function() {
	// condition menu
	console.log($(this).data('valuelabel'))
	console.log($(this).closest('.btn-group'));
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	
    })
    
    $('#modal_add_crit .crit_val_item').on('click', function() {
	
    })
				       
    $('#modal_cond form').on('submit', function() {
	// check
    })
    
    $('#modal_add_crit form').on('submit', function() {
	// check
    })
    
    $('.kolekti-action-remove-variable').on('click', function() {
	var varindex = $(this).data('varindex')
	var varname = $(this).data('varname')
	if (confirm('Voulez vous réélement supprimer la variable '+varname)) {
	    $.ajax({
		url:'/variables/detail/',
		type:'POST',
		data:{"action":"dellvar",
		      "path":path,
		      "index":varindex}
	    }).success(function(data) {
		window.location.href='/variables/detail/?path='+path
	    });
	}
	
    })
    
    

});
