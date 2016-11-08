$(document).ready(function() {
  if (sessionStorage && (sessionStorage.getItem("anim-page-de-garde") == null)) {
    console.log("debut anim page de garde. sessionStorage :" + sessionStorage.getItem("anim-page-de-garde"));

    // creation de l'html

    // ajout d'une div main-content autour de l'existant
      $( "body" ).wrapInner( "<div class='main-content'></div>");
      var oldbodypadding = $( "body" ).css("padding-top");
      $( "body" ).css("padding-top","0");
    // html de la page de garde
    $('<div>', {
        'class': 'page-de-garde container-fluid',
        html: [
            $('<div>', {
                'class': "signature",
                html: [
                    $('<div>', {
                        'class': "svg-container",
                        html: [
                            $('<img>', {
                                'class': "img-responsive logo-ecorse",
                                'src': "/static/pganim/logoEcoRSEG.svg",
                                'alt': "logo ecorse"
                            }),
                        ]
                    }),
                    $('<div>', {
                        'class': "mentions-elocus",
                        html: [
                            $('<p>', {
                                'class': "slogan",
                                html: [
                                    $('<span>', {
                                        'class': "slogan-start",
                                        html: "Simulez et pilotez"
                                    }),
                                    $('<br/>'),
                                    $('<span>', {
                                        'class': "slogan-end",
                                        html: "Les projets de développement de votre territoire"
                                    }),
                                ]
                            }),
                            $('<p>', {
                                'class': "powered-by-elocus",
                                html: "Powered by Elocus"
                            })
                        ]
                    }),
                    $('<div>', {
                        'class': "frise",
                        html: ""
                    })
                ]
            }),
            $('<div>', {
                'class': "frise",
                html: ""
            })
        ]
    }).prependTo($('body'));

    //settings de départ
    $('div.page-de-garde').css({display: 'block'});
    $('div.main-content').css({opacity : 0.0});

    //démarrage animation frise
    animateFrise();

    // disparition progressive de la page de garde
    var pageDeGardeDisparait = true;
    if (pageDeGardeDisparait) {
      $('div.page-de-garde').delay(6000).animate({opacity : 0.0}, {
        duration: 3000,
        start:function() {
          // Animation commencée
          $('div.main-content')
            .delay(100)
            .css({display: 'block'})
            .animate({opacity : 1.0}, {duration: 3000});
          //disparition progressive de la frise
            $('div.page-de-garde div.frise').animate({opacity : 0.0}, 3000);
        },
        complete:function() {
            // Animation finie
	    $( "body" ).animate({'padding-top': oldbodypadding}, 500);


          $('div.page-de-garde')
            .css({display: 'none'});
            sessionStorage && sessionStorage.setItem("anim-page-de-garde", "false");
	    
          console.log("fin anim page de garde. sessionStorage :" + sessionStorage.getItem("anim-page-de-garde"));
        }
      });
    }
  } else {
    console.log("pas d'anim page de garde. sessionStorage :" + sessionStorage.getItem("anim-page-de-garde"));
  }
});

// mouvement de la frise
var friseLeftPosition = 0;
var animFriseT = 100;
var delaiMvtfrise = 1000;
function animateFrise() {
  if(delaiMvtfrise <= 0) {
    var friseBgPositionPx = friseLeftPosition + "px";
    $('div.page-de-garde div.frise').animate({'background-position-x' : friseBgPositionPx}, animFriseT);
    friseLeftPosition -= 3;
  }
  delaiMvtfrise -= animFriseT;
  if (sessionStorage.getItem("anim-page-de-garde") == null && delaiMvtfrise > -10000) {
    window.setTimeout(function() { animateFrise() }, animFriseT);
  }
  //console.log("friseBgPosition :" + friseBgPosition);
}

//bouton pour rejouer anim
$('#playAnimation').click(function(){
	sessionStorage.removeItem("anim-page-de-garde");
	alert("rafraichissez maintenant la fenêtre");
});

