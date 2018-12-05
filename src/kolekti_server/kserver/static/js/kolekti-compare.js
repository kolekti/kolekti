$(function() {

    $('body').popover({
        selector: '.btn-popover',
        html:true
    });
    
    var release = $('#main').data('release')
    var lang = $('#main').data('lang')
    var status = $('#main').data('state')

    var compare_topic = function (topicelt, cmp_release) {
//        console.log(cmp_release)
        $.post(Urls.kolekti_compare_topic_source(kolekti.project), {
            'release': release,
            'cmprelease': cmp_release,
            'lang': lang,
            'topic':  topicelt.data('topic-source')
        })
            .done(function(data, status, xhr) {                
//                console.log(data, xhr)
                $(topicelt).find('.topicdiffsource').remove()
                $(topicelt).find('.topiccontent').after($(xhr.responseText))
                $(topicelt).find('.topiccontent').hide()
                $(topicelt).find('.topicstatus').addClass('alert-info')
                $(topicelt).find('.topicstatus').removeClass('alert-danger')
                var nbdiff = $(topicelt).find('.topicdiffsource').data('diff-count')
                if (!cmp_release)
                    $(topicelt).find('.topicstatus .content').html("Comparaison avec le module source (" + nbdiff + " différences)")
                else
                    $(topicelt).find('.topicstatus .content').html("Comparaison avec la version " + cmp_release +" (" + nbdiff + " différences)")
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
    }



    $(document).on('click','.btn_compare_release_source', function(ev) {
        if ($(this).closest('li').hasClass('disabled'))
            return
        ev.preventDefault();
        $('.topic').each(function(){
            compare_topic($(this))
        })
    })
                   
    $(document).on('click','.btn_compare_releases', function(ev) {
        if ($(this).closest('li').hasClass('disabled'))
            return
        ev.preventDefault();
        var release = $(this).data('release')
        $('.topic').each(function(){
            compare_topic($(this), release)
        })

    })
                   
    $(document).on('click','.compare_topic_source', function(ev) {
        if ($(this).closest('li').hasClass('disabled'))
            return
        ev.preventDefault();
//        ev.stopPropagation();
        var topicelt = $(this).closest('.topic')
        compare_topic(topicelt)
    })

    
    if (status != "sourcelang") {
        $('.btn_compare_release_source').addClass('disabled')
    }
})
