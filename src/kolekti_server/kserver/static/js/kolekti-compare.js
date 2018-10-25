$(function() {
    
    var release = $('#main').data('release')
    var lang = $('#main').data('lang')
    
    $(document).on('click','.compare_topic_source', function(ev) {
        ev.preventDefault();
//        ev.stopPropagation();
        var topicelt = $(this).closest('.topic')
        $.post(Urls.kolekti_compare_topic_source(kolekti.project), {
            'release': release,
            'lang': lang,
            'topic':  topicelt.data('topic-source')
        })
            .done(function(data, status, xhr) {
                
                console.log(data, xhr)
                $(topicelt).find('.topicdiffsource').remove()
                $(topicelt).find('.topiccontent').after($(xhr.responseText))
                $(topicelt).find('.topiccontent').hide()

              })
            .fail(function(data) {
                console.log(data)
                
              })
    })

})
