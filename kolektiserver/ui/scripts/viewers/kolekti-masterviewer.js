function masterviewer() {
    this.pubdg = null;
}

masterviewer.prototype=new kolekti_viewer;

masterviewer.prototype.init = function(viewname, tab) {
    this.context = tab;
    this.viewname = viewname;
    this.url = this.context.url;
    this.version = this.context.version;
    this.load();
    var me = this;
    kolekti.listen('get-master',function(arg){me.getmaster(arg);},this.context.id);
    kolekti.listen('publish-master',function(arg){me.dialog(arg);},this.context.id);
    kolekti.listen('dialog-publish-master',function(arg){me.publishmaster(arg);},this.context.id);
}

masterviewer.prototype.getmaster = function(arg) {
    window.open(arg.url);
}

masterviewer.prototype.publishmaster = function(arg) {
    if(this.pubdg) {
       var div = document.createElement("div");
       div.className = "publish_waiting";
       var img = document.createElement("img");
       img.setAttribute("src", "/_lib/kolekti/icons/wait.gif");
       img.setAttribute("alt", "...");
       div.appendChild(img);
       var p = document.createElement("p");
       p.textContent = i18n("[0354]Publication en cours");
       div.appendChild(p);
       this.pubdg.appendChild(div);
       this.pubdg.waiting = div;
    }

    var conn = new ajax(arg.url+'?publish=1');
    conn.setParameter('file', decodeURIComponent(arg.url));
    conn.setCallback(this.callback_log,3);
    conn.setCallback(this.callback_result,4);
    conn.setData(this);
    var req=conn.post(); 
}

masterviewer.prototype.dialog = function(arg) {
    var me = this;
    this.pubdg = document.getElementById('publish_dialog');
    // reset dialog content
    this.pubdg.innerHTML = "";
    var div = document.createElement("div");
    div.className = "publication_log";
    this.pubdg.appendChild(div);
    div = document.createElement("div");
    div.className = "publication_result";
    this.pubdg.appendChild(div);

    // init dialog
    $(this.pubdg).dialog( {
        title : i18n("[0312]Publier l'enveloppe"),
        modal : true,
        open : function (event,ui) {kolekti.notify('dialog-publish-master',arg,me.context.id);},
        autoOpen : true,
        resizable : true,
        width : 680,
        close: function (event,ui) {$('#publish_dialog').dialog('destroy');},
        buttons: [{ text: i18n("[0306]Fermer"),
                    click: function() {
                       $('#publish_dialog').dialog('destroy');
                    }
                 }]
    });
    $(this.pubdg).dialog('open');
}

masterviewer.prototype.callback_log = function(res,me) {
    var div=$('#publish_dialog').find(".publication_log")[0];
    div.style.display='block';
    div.innerHTML=res.text;
}

masterviewer.prototype.callback_result = function(res,me) {
    if(me.pubdg)
        me.pubdg.removeChild(me.pubdg.waiting);
    var div=$('#publish_dialog').find(".publication_log")[0];
    div.style.display='none';
    div=$('#publish_dialog').find(".publication_result")[0];
    div.innerHTML=res.text;
    me.format_links(div);
    div.style.display='block';
}

masterviewer.prototype.format_links = function(div) {
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
                this.attached_profile(d, dd)
        }
    }
}

masterviewer.prototype.attached_profile = function(d, dd) {
    var me = this;
    d.firstChild.addEventListener('click',function(e){me.profile_section(d.firstChild)},false);
    d.insertBefore(dd, d.firstChild.nextSibling);

    if($(d).find('.result .error').length > 0) {
        $(d.firstChild.firstChild).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
        $(d).find('.result')[0].style.display = "block";
        d.firstChild.firstChild.nextSibling.className = 'error';
    } else {
        $(d).find('.result')[0].style.display = "none";
        d.firstChild.firstChild.nextSibling.className = 'success';
    }
}

masterviewer.prototype.profile_section = function(div) {
    $(div.firstChild).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
    var res = $(div.parentNode).find('.result')[0];
    if(res) {
        if(res.style.display=='block')
            res.style.display = 'none';
        else
            res.style.display = 'block';
    }
}
