$(function() {

    $('body').popover({
        selector: '.btn-popover',
        html:true
    });
    
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
                $(topicelt).find('.topicstatus').addClass('alert-info')
                $(topicelt).find('.topicstatus').removeClass('alert-danger')
                var nbdiff = $(topicelt).find('.topicdiffsource').data('diff-count')
                $(topicelt).find('.topicstatus .content').html("Comparaison avec le module source (" + nbdiff + " différences)")
                $(topicelt).find('.topicstatus').removeClass('hidden')
                
              })
            .fail(function(data) {
                var statuss = JSON.parse(data.responseText)
                console.log(data)
                console.log(statuss)
                console.log(statuss.message)
                
                $(topicelt).find('.topicstatus').addClass('alert-danger')
                $(topicelt).find('.topicstatus').removeClass('alert-info')
                $(topicelt).find('.topicstatus .content').html(statuss.message)
                $(topicelt).find('.topicstatus').removeClass('hidden')
            })
            .always(function() {
                $(topicelt).find('.topicstatus').on('close.bs.alert', function (e) {
                    e.preventDefault()
                    $(topicelt).find('.topicstatus').addClass('alert-info')
                    $(topicelt).find('.topicstatus').removeClass('alert-danger')
                    $(topicelt).find('.topicstatus').addClass('hidden')
                    $(topicelt).find('.topiccontent').show()
                    $(topicelt).find('.topicdiffsource').remove()
                })
            })
    })

    $(document).on('click','.compare_topic_version', function(ev) {
        ev.preventDefault();
        var topicelt = $(this).closest('.topic')
        $.post(Urls.kolekti_compare_topic_version_usage(kolekti.project), {
            'release': release,
            'lang': lang,
            'topic':  topicelt.data('topic-source')
        })
    })

})
