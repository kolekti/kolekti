// retour haut de page
$(window).scroll(function(){
	var posScroll = $(document).scrollTop();
	if(posScroll >=300) {
		$('#topTopLink').fadeIn(600);
		$('#topTopLink').css('display','block');
	} else {
		$('#topTopLink').fadeOut(600);
	}
});
$('#topTopLink').click(function(){
	$('html').animate({scrollTop:0}, 'slow');
	return false;
});

//Sidenav Push Content 
/* Set the width of the side navigation to 250px and the left margin of the page content to 250px */
function openNav() {
	var transitionTime = 400;
	if (sessionStorage && (sessionStorage.getItem("navbar-state") == 'true')) {
		transitionTime = 0;
		$("#mySidenav").addClass("no-transition");
		$("#bootstrapContent").addClass("no-transition");
	}
	$("#mySidenav").css("width", "300px");			    
	$("#bootstrapContent").css("marginLeft", "300px");
	$("#openNavBtn").hide(transitionTime);
	$("#closeNavBtn").show(transitionTime);
	sessionStorage && sessionStorage.setItem("navbar-state", true)
	setTimeout(function () {
		equalizePanelHeadings($('.accueil.sections'));
		$('body').trigger('redraw.elocus.topics');
	}, 500);
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeNav() {
	$("#mySidenav").css("width", "0");			    
	$("#bootstrapContent").css("marginLeft", "0");
	$("#closeNavBtn").hide('400');
	$("#openNavBtn").show('400');
	sessionStorage && sessionStorage.setItem("navbar-state", false)
	$("#mySidenav").removeClass("no-transition");
	$("#bootstrapContent").removeClass("no-transition");
	setTimeout(function () {
		equalizePanelHeadings($('.accueil.sections'));
		$('body').trigger('redraw.elocus.topics');
	}, 500);
}

$("#closeNavBtn").hide('0');
$('#openNavBtn').click(openNav);
$('#closeNavBtn').click(closeNav);

sessionStorage && (sessionStorage.getItem("navbar-state") == 'true') && openNav()

/* $('.sidebar').affix({
    offset: {
        top: 100,
        bottom: function () {
            return (this.bottom = $('.footer').outerHeight(true))
        }
    }
}) */