function publishform() { }

publishform.prototype.initevent = function() { }

publishform.prototype.format_logs = function(arg) {
    if(arg.urlid == this.context.id) {
        var div = $(arg.doc).find('div.logs')[0];
        var divs = div.getElementsByTagName('div');
        for(var i=0; i<divs.length; i++) {
            var d = divs[i];
            if(d.className == 'profile') {
                var dd = document.createElement('div');
                dd.className = 'links';
                $(d).find(".link").each(function() {
                    var child = this;
                    this.parentNode.removeChild(this);
                    dd.appendChild(child);
                });

                if(d.firstChild)
                    this.attached_profile(d, dd);
            }
        }
    }
}

publishform.prototype.attached_profile = function(d, dd) {
    var me = this;
    var tspan = $(d).find('div.title span');
    tspan[0].addEventListener('click',function(e){me.profile_section(d)},false);
    d.insertBefore(dd, d.firstChild.nextSibling);

    if($(d).find('.result .error').length > 0) {
        $(tspan[0]).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
        $(d).find('.result')[0].style.display = "block";
        tspan[1].className = 'error';
    } else {
        $(d).find('.result')[0].style.display = "none";
        tspan[1].className = 'success';
    }
}

publishform.prototype.profile_section = function(div) {
    var icon = $(div).find('div.title span')[0];
    $(icon).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
    var res = $(div).find('.result')[0];
    if(res) {
        if(res.style.display=='block')
            res.style.display = 'none';
        else
            res.style.display = 'block';
    }
}
