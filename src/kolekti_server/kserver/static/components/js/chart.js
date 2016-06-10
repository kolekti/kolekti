

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
	    $(e.target).find('.ecorse-chart').each(function() {
		drawchart(this, true)
	    });
	}
    });
    


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
	    var topic = $(this).closest('.topic')
	    var chart = topic.find('.ecorse-chart')
	    var release = $('.report').data('release')
	    
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
		    btn.closest('ul').find('i').remove();
		    btn.append($('<i>', { 'class':'fa fa-check'}));
		    chart.attr('data-chartkind',chartkind)
		    chart.html('')
		    drawchart(chart.get(0), true);
		}
	    }).fail(function(data) {
	    });
	    
	}
    })

})
})
