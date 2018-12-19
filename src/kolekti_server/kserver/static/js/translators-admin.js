$(function() {
    
    $('#invite_email_btn').on('click', function(e) {
	    e.preventDefault();
	    var email = $( "#invite_email" ).val();
	    $.post(
            '/invitations/send-json-invite/',
	        JSON.stringify([email])
	    ).done(function(data){
		    $('#invitation').closest('.alert').removeClass('alert-warning')
		    $('#invitation').closest('.alert').addClass('alert-success')
		    $('#invitation').html(email + ' invited')
	    }).error(function(data){
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
    

    var label_state = {
        "sourcelang":"source language",
        "edition":"new release",
        "translation":"Translation in progress",
        "validation":"Validation in progress",
        "publication":"Validated"
    }
    
    
    $(".kolekti-release-langs").each(function() {
        var releaseelt = $(this).closest('.release'),
            release = releaseelt.data('release'),
	        project = releaseelt.data('project'),
            statecell = $(this)

        $.getJSON(
            Urls.admin_translators_statuses(project, release)
        ).success(function(data) {
            console.log(data)

	        $.each(data, function(index,item) {
                var codelg = item[0]
		        var state  = item[1]
                
		        if (state) {
		            statecell.append($('<span>',{
			            "class":"langstate lg-" + codelg + " " + state + ((state == "sourcelang")?" active":""),
			            "html":[$('<a>',{
			                "class":"releaselang",
			                "href": Urls.kolekti_release_lang_detail(project, release, codelg),
                            "title":label_state[state],
			                "data-lang":codelg,
			                "data-project":project,
			                "data-release":release,
			                "html":codelg
			            }),
                                $('<span>', {
                                    "class":"releaselangback",
                                    "html":" "})
                               ]
		            }))
                }
	        });
	    })        
    });
})
