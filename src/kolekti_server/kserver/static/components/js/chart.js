

$(document).ready(function() {
    $.getScript('/static/components/js/chart_functions.js', function(){

	// display chart on report main page for starred topics
	$('.alaune .ecorse-chart').each(function() {
		drawchart(this, true)
	});
	$("body").trigger( "displayed.elocus.alaune", [ "chart" ] );


	// remove chart drawing on section collapse hide
	$('.section-content.collapse').on('hidden.bs.collapse', function(e) {
	    if ($(e.target).hasClass('section-content')) {
		$(e.target).find('.ecorse-chart').each(function() {
		    $(this).html('');
		});
	    }
	});
					  
	// display chart drawing on section collapse show
	$('.section-content.collapse').on('shown.bs.collapse', function(e) {
	    console.log('collapse show');
	    if ($(e.target).hasClass('section-content')) {
		$('.report').attr('style','padding-bottom:1200px;')
		$(e.target).find('.panel .ecorse-chart').each(function() {
		    $(this).attr('style','');
		    drawchart(this, true)
		});
		$('.report').attr('style','padding-bottom:40px;')
		$(e.target).trigger( "displayed.elocus.topics", [ "chart" ] );
	    }
	});

	
	// display chart drawing on edit modal show	
	$('.modal-topic-details').on('show.bs.modal', function(e) {
	    var modal = $(e.target).closest('.modal');
	    var topic = $(modal).closest('.topic');
	    var tchart = $(topic).find('.panel .ecorse-chart')
	    var chartkind = tchart.attr('data-chartkind');
	    $(e.target).find('.ecorse-chart').each(function() {
		$(this).html('')
		$(this).attr('data-chartkind',chartkind);
		
	    });
	    $(modal).find('.ecorse-action-chart[data-chartkind='+chartkind +']').append($('<i>', { 'class':'fa fa-check'}));
	    
	});

	$('.modal-topic-details').on('shown.bs.modal', function(e) {
	    $(e.target).find('.ecorse-chart').each(function() {
		drawchart(this, true)
	    });
	});

	// prepare request parameter on edit modal confirm
	$('.modal-topic-details').on('confirm.bs.modal', function(e) {
	    console.log('chart modal confirm');
	    var modal = $(e.target).closest('.modal'),
		dchart = $(modal).find('.ecorse-chart'),
		topic = $(modal).closest('.topic'),
		chartkind = dchart.attr('data-chartkind'),
		elocus_params = modal.data('elocus_params')
	    elocus_params['release'] = $('.report').data('release');
	    elocus_params['topic'] =  topic.attr('id');
	    elocus_params['chartkind'] = chartkind;
	    modal.data('elocus_params', elocus_params);
	});

	$('.modal-topic-details').on('confirmed.bs.modal', function(e) {
	    console.log('chart modal confirmed');
	    var modal = $(e.target).closest('.modal'),
		topic = $(modal).closest('.topic'),
		dchart = $(modal).find('.ecorse-chart'),
		chartkind = dchart.attr('data-chartkind');

	    $(topic).find('.panel .ecorse-chart').each(function() {
		$(this).attr('data-chartkind',chartkind);
		$(this).html('')
		drawchart(this, true);
	    });
	})

	// remove chart in modal when closed
	$('.modal-topic-details').on('hide.bs.modal', function(e) {
	    console.log('chart modal hide');
	    var modal = $(e.target).closest('.modal');
	    var dchart = $(modal).find('.ecorse-chart');
	    var topic = $(modal).closest('.topic');
	    var chartkind = $(topic).find('.panel .ecorse-chart').attr('data-chartkind');
	    $(modal).find('.ecorse-action-chart i').remove();
	    
	})

	// redraw chart on window resize
	$(window).on('resize', function() {
	    $('.collapse.in').find('.ecorse-chart').each(function() {
		$(this).html('')
		drawchart(this, false)
	    });
	    $(e.target).trigger( "displayed.elocus.topics", [ "chart" ] );
	    $('.alaune').find('.ecorse-chart').each(function() {
		$(this).html('')
		drawchart(this, false)
	    });
	    $(e.target).trigger( "displayed.elocus.alaune", [ "chart" ] );
	})
	
	
	// menu selection graphique
	$('.ecorse-action-chart').on('click', function(e) {
	    e.preventDefault()
	    if(!$(this).find('i').length) {
		var btn = $(this)
		var chartkind = $(this).attr('data-chartkind')
		var dialog = $(this).closest('.modal')
		var chart = dialog.find('.ecorse-chart')
		//var release = $('.report').data('release')

		btn.closest('ul').find('i').remove();
		btn.append($('<i>', { 'class':'fa fa-check'}));
		chart.attr('data-chartkind',chartkind)
		chart.html('')
		drawchart(chart.get(0), true);
		
		/* should be done a modal validation */
	    }
	})
	
    })
})
