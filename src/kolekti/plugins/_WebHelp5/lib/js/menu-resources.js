$(function(){
    $('a.resource').on('click', function(e) {
        e.preventDefault()
        e.stopPropagation()
        var ref = $(this).attr('href')
        console.log(ref)
        $('#iFrameResource').attr('src', ref)
        $('a.resource').closest('li').removeClass('active')
        $(this).closest('li').addClass('active')

    })
    
    $('.liens-menu ul li').first().addClass('active')
})
