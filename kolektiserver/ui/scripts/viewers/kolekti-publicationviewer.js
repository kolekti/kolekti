function publicationviewer() {
}

publicationviewer.prototype = new kolekti_viewer;

publicationviewer.prototype.list_properties.push({ns:'kolekti:browser',propname:'isprofile'});

publicationviewer.prototype.fetch_resource = function() {
    var isprofile;
    var xpr=this.props.firstChild;
    while (xpr) {
        if (xpr.localName=="isprofile" && xpr.namespaceURI=="kolekti:browser") {
            isprofile=(xpr.firstChild && xpr.firstChild.textContent=="yes");
            break;
        }
        xpr=xpr.nextSibling;
    }

    var ifrw=document.createElement('div');
    ifrw.className="iframe_container";
    var ifr=document.createElement('iframe');
    ifr.className = "iframe_container";
    var url=this.url+'?viewer='+this.viewname;
    if(isprofile)
        url += "&type=profile";
    if (this.version != null) {
    url=url+"&version="+this.version
    }

    ifr.src=url;
    //ifr.setAttribute('src',this.url);
    this.content.appendChild(ifrw);
    ifrw.appendChild(ifr);
    this.content.className="show_resource";
    this.iframe=ifr

    if(this.sidebar) {
        var sb = document.createElement('div');
        sb.className = "sidebar";
        this.context.sidebar = sb;
        this.contentactions.appendChild(sb);
    }
}

publicationviewer.prototype.init_view = function(doc) {
    var pub, li, a;
    var links = doc.getElementById("links");
    var ul = links.getElementsByTagName("ul")[0];

    var logs = doc.getElementById("logs");

    // get links of publication results
    var publinks = $(logs).find('.link a');
    for(var i=0; i<publinks.length; i++) {
        pub = publinks[i];
        li = document.createElement('li');
        a = document.createElement('a');
        a.setAttribute('href', pub.getAttribute('href'));
        a.textContent = pub.textContent;
        li.appendChild(a);
        ul.appendChild(li);
    }

    this.format_logs(logs, publinks);
}

publicationviewer.prototype.format_logs = function(logs, publinks) {
    var link;
    var child = logs.firstChild;
    while(child) {
        if(child.nodeType == 1 && child.className == "section") {
            this.logs_section(logs);
        }
        child = child.nextSibling;
    }

    var link;
    var result = $(logs).find('.result')[0];
    for(var i=0; i<publinks.length; i++) {
        link = publinks[i].parentNode;
        result.removeChild(link);
        result.insertBefore(link, result.firstChild);
    }
}

publicationviewer.prototype.logs_section = function(logs) {
    var me = this;
    var dlogs = logs.getElementsByTagName("div");
    dlogs[0].addEventListener("click", function(e) { me.section_display(dlogs[0], dlogs[1]);}, false)
}

publicationviewer.prototype.section_display = function(dtitle, dcontent) {
    var section = dtitle.getElementsByTagName('span')[0];
    $(section).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
    if(dcontent.style.display == "block")
        dcontent.style.display = "none";
    else
        dcontent.style.display = "block";
}
