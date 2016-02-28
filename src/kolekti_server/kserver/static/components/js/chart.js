$(document).ready(function() {
    console.log('init chart componenent');
    $('.section-content.collapse').on('shown.bs.collapse', function(e) {
	if ($(e.target).hasClass('section-content')) {
	    $(e.target).each(function() {
		var selchart = d3.select(this).select('.ecorse-chart')
		selcharts.datum(function() { return this.dataset})
		    
	    });
	}
    })
    
})
