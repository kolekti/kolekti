$(function() {
        
    $('#content_pane').on("click", ".edit_topic_release", function(e) {
        e.preventDefault()
        var topic_id = $(this).closest('.topic').attr('id')
        var lang = $('#main').data('lang');
	    var release = $('#main').data('release')
        window.open(Urls.kolekti_release_lang_edit_topic(kolekti.project, release, lang, topic_id))
        
    })
})
