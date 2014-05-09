function kolekti_uploadtranslateform(url, id, prj) {
    this.url = url;
    this.id = id;
    this.prj = prj;
    this.multiple = 0;
    this.pubdg = null;
}

kolekti_uploadtranslateform.prototype=new kolekti_uploadform;


kolekti_uploadtranslateform.prototype.publish= function(file) {
    this.pubdg = window.parent.document.body;
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
    var conn = new ajax(this.url);
    conn.setParameter("publish", '1');
    conn.setParameter("file", decodeURIComponent(file));
    conn.setCallback(this.callback_log,3);
    conn.setCallback(this.callback_result,4);
    conn.setData(this);
    var req=conn.post();
}

kolekti_uploadtranslateform.prototype.callback_log = function(res,me) {
    var div=$('#publish_dialog')[0];
    div.style.display='block';
    div.innerHTML=res.text;
}

kolekti_uploadtranslateform.prototype.callback_result = function(res,me) {
    if(me.pubdg)
        me.pubdg.removeChild(me.pubdg.waiting);
    document.firstChild.innerHTML=res.text;
    me.format_links(document.body);
    me.refresh_history();
}

kolekti_uploadtranslateform.prototype.format_links = function(div) {
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

kolekti_uploadtranslateform.prototype.attached_profile = function(d, dd) {
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

kolekti_uploadtranslateform.prototype.profile_section = function(div) {
    $(div.firstChild).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
    var res = $(div.parentNode).find('.result')[0];
    if(res) {
        if(res.style.display=='block')
            res.style.display = 'none';
        else
            res.style.display = 'block';
    }
}

kolekti_uploadtranslateform.prototype.refresh_history = function() {
    var contentright = window.parent.document.getElementById("splitcontentright");
    var history = $(contentright).find(".logs")[0];
    var conn = new ajaxdav('/projects/'+this.prj+'/masters');
    conn.setHeader("KOLEKTIFORCEVIEW", "1");
    conn.setParameter("history", "1");
    var req = conn.PROPFIND([{"ns": "kolekti", "propname":"history"}]);
    if(req.result.status == 207) {
        var xpr=req.result.xml.evaluate( '/d:multistatus/d:response/d:propstat[starts-with(d:status,"HTTP/1.1 200")]/d:prop', req.result.xml, kolektiNsResolver, XPathResult.FIRST_ORDERED_NODE_TYPE, null );
        var lhisto = xpr.singleNodeValue.firstChild;
        history.innerHTML = "";
        history.appendChild(lhisto.getElementsByTagName("table")[0]);
    }
    var b;
}
