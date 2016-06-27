

$(document).ready(function() {
    $.getScript('/static/components/js/chart_functions.js', function(){
	console.log('init charts');
	
	$('.section-content.collapse').on('hidden.bs.collapse', function(e) {
	    if ($(e.target).hasClass('section-content')) {
		$(e.target).find('.ecorse-chart').each(function() {
		    $(this).html('');
		});
	    }
	});
    
	$('.section-content.collapse').on('shown.bs.collapse', function(e) {
	    if ($(e.target).hasClass('section-content')) {
		$('.report').attr('style','padding-bottom:1200px;')
		$(e.target).find('.panel .ecorse-chart').each(function() {
		    $(this).attr('style','');
		    drawchart(this, true)
		});
		$('.report').attr('style','padding-bottom:40px;')
	    }
	});
	
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

	$('.modal-topic-details').on('confirm.bs.modal', function(e) {
	    console.log('chart modal confirm');
	    var modal = $(e.target).closest('.modal');
	    var dchart = $(modal).find('.ecorse-chart');
	    var topic = $(modal).closest('.topic');
	    var release = $('.report').data('release');
	    var chartkind = dchart.attr('data-chartkind');
	    
	    $.ajax({
		url:"/elocus/report/chart",
		method:'POST',
		data:$.param({
		    'release': release,
		    'topic': topic.attr('id'),
		    'chartkind': chartkind
		})
	    }).done(function(data) {
		
		if (data.status == 'ok') {
		    $(topic).find('.panel .ecorse-chart').each(function() {
			$(this).attr('data-chartkind',chartkind);
			$(this).html('')
			drawchart(this, true);
		    });

		}
	    }).fail(function(data) {
	    });
	});
	
	$('.modal-topic-details').on('hide.bs.modal', function(e) {
	    console.log('chart modal hide');
	    var modal = $(e.target).closest('.modal');
	    var dchart = $(modal).find('.ecorse-chart');
	    var topic = $(modal).closest('.topic');
	    var chartkind = $(topic).find('.panel .ecorse-chart').attr('data-chartkind');
	    $(modal).find('.ecorse-action-chart i').remove();
	    
	})

	$(window).on('resize', function() {
	    $('.collapse.in').find('.ecorse-chart').each(function() {
		$(this).html('')
		drawchart(this, false)
	    });
	    
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
