
function kolekti_publicationsidebar(id, context) {
    this.id=id;
    this.context=context;
    this.properties = new Array();
    this.dom = null;
    this.section_state = new Object();
    this.currentlang = null;
}

kolekti_publicationsidebar.prototype=new kolekti_sidebar;

kolekti_publicationsidebar.prototype.refresh=function(sidebar) {
    var child, e;
    var me=this;
    sidebar.innerHTML = "";
    var conn=new ajaxdav(this.context.currenttab.url);
    conn.setHeader('KolektiForceView', '1');
    var req=conn.PROPFIND(this.properties,0); 

    if(req.result.status == "207") {
        var xpr = req.object;
        while (xpr.nextResponse()) {
            // Format languages
            pp=xpr.get_prop('kolekti:publication','languages');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
                this.languages = e;
                this.init_languages(e);
            }
            // Format versions
            pp=xpr.get_prop('kolekti:publication','versions');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
                this.versions = e;
                this.init_versions(e);
            }
        }
        
        var titles = sidebar.getElementsByTagName("h3");
    }
    this.init_ui();
}

/* init languages */
kolekti_publicationsidebar.prototype.init_languages=function(elt) {
    var li = elt.getElementsByTagName('li');
    for(var i=0; i<li.length; i++)
        this.init_event_languages(li[i], li[i].textContent);
}

/* init event for languages */
kolekti_publicationsidebar.prototype.init_event_languages=function(li, lang) {
    var me = this;
    if(lang == kolekti.locale) {
        li.setAttribute("style", "font-weight: bold;");
        this.currentlang = li;
    }
    li.addEventListener("click", function(e) { me.select_lang(e, lang); }, false);
}

/* display selected lang publication */
kolekti_publicationsidebar.prototype.select_lang=function(evt, lang) {
    var li = evt.currentTarget;
    if(this.currentlang)
    	this.currentlang.removeAttribute("style");
    li.setAttribute("style", "font-weight: bold;");
    this.currentlang = li;
    var ifr = this.context.currenttab.domview.getElementsByTagName("iframe")[0];
    var newsrc = this.replace_lang(ifr.src, lang);
    ifr.src = this.replace_version(newsrc, '');
    this.refresh_versions(lang);
}

/* refresh versions section */
kolekti_publicationsidebar.prototype.refresh_versions=function(lang) {
    var li, newli;
    // reset list of publications
    var ul = this.versions.getElementsByTagName('ul')[0];
    while(ul.firstChild)
        ul.removeChild(ul.firstChild);

    var conn=new ajaxdav(this.context.currenttab.url);
    conn.setHeader('KolektiForceView', '1');
    conn.setParameter("lang", lang);
    var req=conn.PROPFIND([{ns:'kolekti:publication', propname:'versions'}],0);

    if(req.result.status == "207") {
        var xpr = req.object;
        while (xpr.nextResponse()) {
            // Format versions
            var pp=xpr.get_prop('kolekti:publication','versions');
            if (pp.status=='200' && pp.content.firstChild)
                ul.innerHTML = pp.content.firstChild.getElementsByTagName("ul")[0].innerHTML;
        }
        this.init_versions(this.versions);
    }
}

/* init versions */
kolekti_publicationsidebar.prototype.init_versions=function(versions) {
    var li = versions.getElementsByTagName('li');
    for(var i=0; i<li.length; i++)
        this.init_event_versions(li[i], li[i].className);
}

/* init event for versions */
kolekti_publicationsidebar.prototype.init_event_versions=function(li, version) {
    var me = this;
    li.addEventListener("click", function(e) { me.display_version(version); }, false);
}

/* display selected version */
kolekti_publicationsidebar.prototype.display_version=function(version) {
    var ifr = this.context.currenttab.domview.getElementsByTagName("iframe")[0];
    ifr.src = this.replace_version(ifr.src, version);
}

/* replace lang param in url */
kolekti_publicationsidebar.prototype.replace_lang=function(url, lang) {
    var dlang = url.search(/lang=/);
    if(dlang > -1)
        return url.replace(/lang=[a-zA-Z]+/, "lang="+lang);
    else
        return url+"&lang="+lang;
}

/* replace version param in url */
kolekti_publicationsidebar.prototype.replace_version=function(url, version) {
    var dvers = url.search(/version=/);
    if(dvers > -1)
        return url.replace(/version=[0-9 -:]*/, "version="+version+"&");
    else
        return url+"&version="+version;
}
