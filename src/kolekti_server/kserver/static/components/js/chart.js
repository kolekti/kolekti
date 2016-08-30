$(document).ready(function() {
    $.getScript('/static/components/js/chart_functions.js', function(){

	// affichage des charts dans les topics à la une sur la page principale du rapport
	
	if ($('.alaune .ecorse-chart').length) {
	    // display chart on report main page for starred topics
	    $('.alaune .ecorse-chart').each(function() {
		drawchart(this, {"anim":true})
	    });
	    $(".alaune").trigger( "displayed.elocus.topics", [ "chart" ] );
	}

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
	    if ($(e.target).hasClass('section-content')) {
//		$('.report').attr('style','padding-bottom:1200px;')
		$(e.target).find('.panel .ecorse-chart').each(function() {
		    $(this).attr('style','');
		    drawchart(this, {"anim":true})
		});
//		$('.report').attr('style','padding-bottom:40px;')
		$(e.target).trigger( "displayed.elocus.topics", [ "chart" ] );
	    }
	});

	
	// display chart drawing on edit modal show
	
	$('.modal-topic-details').on('show.bs.modal', function(e) {
	    var modal = $(e.target).closest('.modal');
	    var topic = $(modal).closest('.topic');
	    var tchart = $(topic).find('.panel .ecorse-chart')
	    var chartkind = tchart.attr('data-chartkind');
	    var chartopts = tchart.attr('data-chartopts');
	    $(e.target).find('.ecorse-chart').each(function() {
		$(this).html('')
		$(this).attr('data-chartkind',chartkind);
		$(this).attr('data-chartopts',chartopts);
		
	    });
	    $(modal).find('.ecorse-action-chart[data-chartkind='+chartkind +']').append($('<i>', { 'class':'fa fa-check'}));
	    
	});

	// display chart on details... modal show
	
	$('.modal-topic-details').on('shown.bs.modal', function(e) {
	    $(e.target).find('.ecorse-chart').each(function() {
		drawchart(this, {"anim":true})
	    });
	});

	// prepare request parameter on edit modal confirm
	
	$('.modal-topic-details').on('confirm.bs.modal', function(e) {
	    var modal = $(e.target).closest('.modal'),
		dchart = $(modal).find('.ecorse-chart'),
		topic = $(modal).closest('.topic'),
		chartkind = dchart.attr('data-chartkind'),
		chartopts = dchart.attr('data-chartopts'),
		elocus_params = modal.data('elocus_params')
	    elocus_params['release'] = $('.report').data('release');
	    elocus_params['topic'] =  topic.attr('id');
	    elocus_params['chartkind'] = chartkind;
	    elocus_params['chartopts'] = chartopts;
	    modal.data('elocus_params', elocus_params);
	});

	// redraw topic chart after closing modal
	
	$('.modal-topic-details').on('confirmed.bs.modal', function(e) {
	    var modal = $(e.target).closest('.modal'),
		topic = $(modal).closest('.topic'),
		dchart = $(modal).find('.ecorse-chart'),
		chartkind = dchart.attr('data-chartkind'),
		chartopts = dchart.attr('data-chartopts');

	    $(topic).find('.panel .ecorse-chart').each(function() {
		$(this).attr('data-chartkind',chartkind);
		$(this).attr('data-chartopts',chartopts);
		$(this).html('')
		drawchart(this, {"anim":true});
	    });
	})

	// remove chart in modal when closed
	
	$('.modal-topic-details').on('hide.bs.modal', function(e) {
	    var modal = $(e.target).closest('.modal');
	    var dchart = $(modal).find('.ecorse-chart');
	    var topic = $(modal).closest('.topic');
	    $(modal).find('.ecorse-action-chart i').remove();
	    
	})

	// redraw function for handling resize & menu hide/show events

	var redraw = function(e) {
	    console.log("redraw")
	    console.log(e)
	    if ($('.collapse.in .ecorse-chart').length) {
		$('.collapse.in').find('.ecorse-chart').each(function() {
		    $(this).html('')
		    drawchart(this, {"anim":false})
		});
		$('.collapse.in').trigger( "displayed.elocus.topics", [ "chart" ] );
	    }
	    
	    if ($('.alaune .ecorse-chart').length) {
		$('.alaune').find('.ecorse-chart').each(function() {
		    $(this).html('')
		    drawchart(this, {"anim":false})
		});
		$('.alaune').trigger( "displayed.elocus.topics", [ "chart" ] );
	    }
	}

	// redraw chart on window resize
	$(window).on('resize', redraw);

	// redraw chart on menu hide/show
	$('body').on('redraw.elocus.topics', redraw);
	
	
	// menu selection graphique
	$('.ecorse-action-chart-kind').on('click', function(e) {
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
		drawchart(chart.get(0), {"chartkind":chartkind, "anim":true});
		
		/* should be done a modal validation */
	    }
	})
	// menu selection graphique
	$('.ecorse-action-chart-icon').on('click', function(e) {
	    var dialog = $(this).closest('.modal')
	    var chart = dialog.find('.ecorse-chart')
	    //var release = $('.report').data('release')
	    var opts = chart.data('chartopts');
	    opts = opts?opts:{};
	    opts['show_icon'] = $(this).is(':checked'); 
	    chart.data('chartopts', opts);
	    console.log(opts);
	    chart.html('');
	    drawchart(chart.get(0), opts);
		
	    /* should be done a modal validation */
	})
	
    })
})
