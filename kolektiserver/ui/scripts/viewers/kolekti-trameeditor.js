function trameeditor() {}

trameeditor.prototype=new kolekti_editor;

trameeditor.prototype.search_module = function(urlid) {
    var i,p,para,spans,span,u;
    var paras=this.content.getElementsByTagName('P');
    for (p=0;p<paras.length;p++) {
    para=paras.item(p);
    spans=para.getElementsByTagName('SPAN');
    for (i=0;i<spans.length;i++) {
        span=spans.item(i);
        if (span.className=='urlid') {
        u=span.textContent;
        if (u==urlid)
            return para;
        }
    }
    }
}

trameeditor.prototype.fetch_resource = function() {
    var c=new ajax(this.url);
    c.setParameter("viewer",this.viewname);
    c.setHeader('KolektiContext','trameeditor');
    var content=c.syncget();
    var div = document.createElement('div');
    div.innerHTML=content.text;
    this.content.appendChild(div);

    this.init_dnd();
    this.init_properties();
}

trameeditor.prototype.init_ui=function() {
    var me=this;
    kolekti.listen('trame-new-section',function(arg){me.add_section(arg.newsectiontitle);return true;},this.context.id);
    kolekti.listen('trame-new-tdm',function(arg){me.add_var("TDM", "kolekti://TDM");return true;},this.context.id);
    kolekti.listen('trame-new-index',function(arg){me.add_var("INDEX", "kolekti://INDEX");return true;},this.context.id);
    kolekti.listen('trame-new-revnotes',function(arg){me.add_var("REVNOTES", "kolekti://REVNOTES");return true;},this.context.id);
    kolekti.listen('trame-rename-section',function(arg){me.set_title_section(arg);return true;},this.context.id);
    kolekti.listen('publish',function(arg){me.publish(arg);return true;},this.context.id);
    kolekti.listen('trame-publish-success',function(arg){me.publication_result(arg);return true;},null);
    this.init_editor_actions();
    this.init_viewer_actions();
    this.init_trameeditor_actions();
    if(this.sidebar)
        this.init_sidebar();
}

trameeditor.prototype.init_trameeditor_actions = function() {
    var me=this;
    // Poubelle (suppression d'objet de la trame)
    var eltact=document.createElement('span');
    eltact.className="vieweritemaction";
    eltact.setAttribute('title',i18n("[0321]Glissez un objet ici pour le supprimer de la trame"));
    var iconact=document.createElement('img');
    iconact.setAttribute('src',"/_lib/kolekti/icons/icon_del.png");
    iconact.setAttribute('alt',"Poubelle");
    iconact.setAttribute('title',i18n("[0321]Glissez un objet ici pour le supprimer de la trame"));
    iconact.className="trash";
    eltact.appendChild(iconact);
    var del=document.createElement('span');
    del.className="trash";
    del.textContent=i18n("[0322]Poubelle");
    eltact.appendChild(del);
    this.clientactions.appendChild(eltact);
}

trameeditor.prototype.publication_result=function(arg) {
    var pres=arg.result.text;
    document.getElementById('result-publication-dialog-content').innerHTML=pres;
}

trameeditor.prototype.droptrash= function(ev, ui) {
    var orig=ui.draggable[0];
    if(ui.draggable.hasClass("title"))
       orig=orig.parentNode;
    var dest=ev.target;
    orig.parentNode.removeChild(orig);
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

trameeditor.prototype.title_section=function(e) {
    var title=e.target;
    this.edittitlesect=title;
    var args={"newName":title.textContent}
    kolekti.actions['trame_rename_section'].set_context(this.context.id);
    kolekti.actions['trame_rename_section'].do_action({"newName":title.textContent});
}

trameeditor.prototype.set_title_section=function(arg) {
    if (this.edittitlesect!=null) {
    this.edittitlesect.textContent=arg['newName'];
    this.edittitlesect=null;
    }
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

trameeditor.prototype.init_dnd=function() {
    var i,div,title;
    var me=this;
    var dragprops={
    helper:'clone',
    axis: 'y', 
    scroll: false,
    refreshPositions: true,
    opacity: 0.8,
    revert: 'invalid',
    delay:200
    };

    jQuery("#resview_content"+this.context.id+" .section>p.title>span.ui-icon").unbind("click", me.displaysection).bind("click", me.displaysection);

    jQuery("#resview_content"+this.context.id+" .section>p.title").draggable(dragprops);
    jQuery("#resview_content"+this.context.id+" .module").draggable(dragprops);

    this.dragmodule = null;
    this.dragsection = null;

    jQuery("#resview_content"+this.context.id+" .dropsection").droppable({
    accept: ".section p.title",
    tolerance: 'touch',
    activeClass: 'droppable-active',
    //hoverClass: 'droppable-hover',
    drop: function(ev, ui) {
        me.dropsection(ev,ui);
    },
    over: function(ev, ui) {
        me.oversection(ev,ui);
    },
    deactivate: function(ev, ui) {
        me.deactivatesection(ev, ui);
    }
    });
    jQuery("#resview_content"+this.context.id+" .dropmodule").droppable({
    accept: ".module,.fileitem,.dirname",
    tolerance: 'touch',
    activeClass: 'droppable-active',
    drop: function(ev, ui) {
        me.dropmodule(ev,ui);
    },
    over: function(ev, ui) {
        me.overmodule(ev,ui);
    },
    deactivate: function(ev, ui) {
        me.deactivatemodule(ev, ui);
    }
    });

    jQuery("#resview_content"+this.context.id+" .section>p.title>span.label").bind("click", function(e){me.title_section(e)});
    jQuery("#resview_content"+this.context.id+" .trash").parent().droppable({
    accept: ".module,.section p.title",
    tolerance:'pointer',
    activeClass: 'trash-active',
    hoverClass: 'trash-hover',
    drop: function(ev, ui) {
        me.droptrash(ev, ui);
    }
    })
    jQuery("#resview_content"+this.context.id+" .mod>.modtitle").bind("click",function(e){me.open_module(e)});
    /* init enabled/disabled module action */
    //jQuery("#resview_content"+this.context.id+" .mod>.modactions>span[class='enabled']").bind("click", function(e){me.enabled_module(e)});
}

trameeditor.prototype.displaysection=function() {
    $(this).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
    $(this).parents(".section:first").find(".module, .section, .tplaceholder").toggleClass("hide_item");
}

trameeditor.prototype.open_module=function(e) {
    var url,version,resid,urlid;
    var m=e.target.parentNode;
    var res=this.get_resid(m);

    if(res.url.substr(0, 10) == "kolekti://")
        return;

    var splitModuleUrl =  res.url.split('/modules/');
    window.location = splitModuleUrl[0]+'/modules?open='+splitModuleUrl[1];
}

trameeditor.prototype.enabled_module=function(e) {
    var m=e.target.parentNode;
}

trameeditor.prototype.get_resid=function(m) {
    var url,version,resid,urlid;
    var spans=m.getElementsByTagName("SPAN");
    for (i=0;i<spans.length;i++) {
    span=spans.item(i);
    if (span.className=='resid') {
        resid=span.textContent;
        url=kolekti.get_url(resid);
    }
    else if (span.className=='urlid') {
        urlid=span.textContent;
    }
    else if (span.className=='version') {
        version=span.textContent;
    }
    }
    return {'url':url,'urlid':urlid,'resid':resid,'version':version};
}

trameeditor.prototype.init_properties=function() {
}

// Dropped elements callbacks
trameeditor.prototype.dropsection= function(ev, ui) {
    this.dragsection.removeClass("droppable-hover");
    var orig=ui.draggable[0].parentNode;
    var dest=this.dragsection.context.parentNode;
    var n=dest;
    while (n!=document) {
    if (n==orig)
        return
    n=n.parentNode;
    }
    orig.parentNode.removeChild(orig);
    dest.parentNode.insertBefore(orig,dest);
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

trameeditor.prototype.oversection=function(ev, ui) {
    if(this.dragsection)
        this.dragsection.removeClass("droppable-hover");
    this.dragsection = $(ev.target);
    this.dragsection.addClass("droppable-hover");
}

trameeditor.prototype.deactivatesection=function(ev, ui) {
    if(this.dragsection)
        this.dragsection.removeClass("droppable-hover");
}

trameeditor.prototype.dropmodule= function(ev,ui) {
    this.dragmodule.removeClass("droppable-hover");
    var orig=ui.draggable[0];
    var dest=this.dragmodule.context.parentNode;
    if (dest.parentNode==null || dest == orig) {
    return;
    }

    if (orig.className=="fileitem ui-draggable") {
    // drop a file
    this.addKolektiModule(dest,orig.kolekti.url);
    } else if (orig.className=="dirname ui-draggable") {
    // drop a module (reference)
    orig=orig.parentNode.parentNode;
    this.addKolektiModule(dest,orig.kolekti.url);
    } else {
    // move a module inside trame
    orig.parentNode.removeChild(orig);
    dest.parentNode.insertBefore(orig,dest);
    }
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

trameeditor.prototype.overmodule=function(ev, ui) {
    if(this.dragmodule)
        this.dragmodule.removeClass("droppable-hover");
    this.dragmodule = $(ev.target);
    this.dragmodule.addClass("droppable-hover");
}

trameeditor.prototype.deactivatemodule=function(ev, ui) {
    if(this.dragmodule)
        this.dragmodule.removeClass("droppable-hover");
}

trameeditor.prototype.add_section=function(title) {
    var me = this;
    var tramediv = $(this.context.domview).find("div.trame")[0];

    var newsect=document.createElement('DIV');
    newsect.className = 'section';
    newsect.innerHTML='<div class="dropsection"><div><!--drop zone--></div></div>                                                   \
        <p class="title"><span class="ui-icon ui-icon-minusthick"><!-- --></span><span class="label">'+title+'</span></p>    \
        <div class="tplaceholder"><div class="dropmodule ui-droppable"><div> </div></div></div>                                    \
        <div class="tplaceholder"><div class="dropsection ui-droppable"><div> </div></div></div>';

    var sectionactive = null;
    var dropsections = $(this.context.domview).find(".dropsection");

    if(dropsections.length == 0) {
        tramediv.appendChild(newsect);
        this.init_new_section(newsect);
        return;
    }

    var p = document.createElement("p");
    p.className = "title ui-draggable ui-draggable-dragging";
    p.setAttribute("style", "position: absolute; opacity: 0.8; left: 25px;");
    var sp = document.createElement("span");
    sp.className = "ui-icon ui-icon-minusthick";
    var splabel = document.createElement("span");
    splabel.className = "label";
    splabel.textContent = title;
    p.appendChild(sp);
    p.appendChild(splabel);
    tramediv.appendChild(p);

    dropsections.addClass("droppable-active");

    $(tramediv).bind("mousemove", function(event) {
        var offtop;

        var ptop = event.pageY-$(this).offset().top;
        p.style.top = ptop;

        if(sectionactive) {
            $(sectionactive).removeClass('droppable-hover');
            sectionactive = null;
        }

        var offset = p.offsetHeight/2;
        for(var i=0; i<dropsections.length; i++) {
            offtop = dropsections[i].offsetTop;
            if(ptop >= offtop-offset && ptop <= offtop+offset) {
                sectionactive = dropsections[i];
                $(sectionactive).addClass("droppable-hover");
                break;
            }
        }
    });

    $("#content").bind("mousedown", function(event) {
        $(tramediv).unbind("mousemove");
        $(this).unbind("mousedown");

        if(sectionactive)
            $(sectionactive).removeClass("droppable-hover");
        $(event.target).parent('.trame');

        var node = event.target.parentNode;
        while(node) {
            if(node.className == "resourceview_content tramesview")
                break;
            node = node.parentNode;
        }
        if(node) {
            if(sectionactive) {
                sectionactive.parentNode.parentNode.insertBefore(newsect,sectionactive.parentNode);
                me.init_new_section(newsect);
            }
        }
        p.parentNode.removeChild(p);
        dropsections.removeClass("droppable-active");
    });
}

trameeditor.prototype.init_new_section=function(newsect) {
    var me=this;

    jQuery("#resview_content"+this.context.id+" .section>p.title>span.ui-icon").unbind("click", me.displaysection).bind("click", me.displaysection);
    jQuery("#resview_content"+this.context.id+" .section>p.title>span.label").bind("click", function(e){me.title_section(e)});

    jQuery(newsect).find(">p.title").draggable({
    helper:'clone', 
    axis: 'y', 
    refreshPositions: true, 
    opacity: 0.8,
    revert: 'invalid',
    delay:200
    });

    jQuery(newsect).find(".dropsection").droppable({
        accept: ".section p.title",
        tolerance: 'touch',
        activeClass: 'droppable-active',
        //hoverClass: 'droppable-hover',
        drop: function(ev, ui) {
            me.dropsection(ev,ui);
        },
        over: function(ev, ui) {
            me.oversection(ev,ui);
        },
        deactivate: function(ev, ui) {
            me.deactivatesection(ev, ui);
        }
        });

    jQuery(newsect).find(".dropmodule").droppable({
        accept: ".module,.fileitem,.dirname",
        tolerance: 'touch',
        activeClass: 'droppable-active',
        drop: function(ev, ui) {
            me.dropmodule(ev,ui);
        },
        over: function(ev, ui) {
            me.overmodule(ev,ui);
        },
        deactivate: function(ev, ui) {
            me.deactivatemodule(ev, ui);
        }
        });
}

//Add var element
trameeditor.prototype.add_var=function(name, content) {
    var div;
    var divs=this.context.domview.getElementsByTagName('DIV');
    for (i=0; i< divs.length; i++) {
        div=divs.item(i);
        if (div.className=="trame")
            break;
    }

    this.createPropertiesSpan(div.firstChild, name, "", content, content);
}

trameeditor.prototype.addKolektiModule=function(dest,url) {
    var props=[{propname:"displayname", ns:"DAV:"},
               {propname:"version", ns:"kolekti:modules"},
               {propname:"resid", ns:"kolekti"},
               {propname:"resourceid", ns:"kolekti"},
               {propname:"valid", ns:"kolekti:modules"}
    ];

    this.getModuleProperties(props,url,dest);
}

trameeditor.prototype.getModuleProperties=function(props,url,dest) {
    var modname,modversion,modinfo,modurlid,modresid,modvalid;
   // get module properties
   props.push({propname:"objectinfos", ns:"kolekti:modules"});
   var conn=new ajaxdav(url);
   var req=conn.PROPFIND(props,0);
   var xp="/d:multistatus//d:propstat[d:status='HTTP/1.1 200 Ok']/d:prop/*"
   if (req.result.status == 207) {
    var props=req.result.xml.evaluate(xp, req.result.xml, kolektiNsResolver, XPathResult.ANY_TYPE, null );
     var thisNode = props.iterateNext();
    while (thisNode) {
        if (thisNode.localName=="resid") {
        modresid=thisNode.textContent;
        }
        if (thisNode.localName=="resourceid") {
        modurlid=thisNode.textContent;
        }
        if (thisNode.localName=="displayname") {
        modname=thisNode.textContent;
        }
        if (thisNode.localName=="version") {
        modversion=thisNode.textContent;
        }
        if (thisNode.localName=="valid") {
        modvalid=thisNode.textContent;
        }
        thisNode = props.iterateNext();
    }
   }

   this.createPropertiesSpan(dest,modname,modversion,modurlid,modresid,modvalid);
}

trameeditor.prototype.createPropertiesSpan=function(dest,modname,modversion,modurlid,modresid,modvalid) {
    var mod=document.createElement('div');
    mod.className = 'module ui-draggable';
    var drop=document.createElement('div');
    drop.className = 'dropmodule ui-droppable';
    mod.appendChild(drop);
    drop.appendChild(document.createElement('div'));

    var p=document.createElement('p');
    p.className = 'mod';

    //create span for ident
    var span=document.createElement('span');
    span.className = 'resident';
    span.setAttribute('style','display:none');

    var sspan=document.createElement('span');
    sspan.className = 'resid';
    sspan.appendChild(document.createTextNode(modresid));
    span.appendChild(sspan);

    sspan=document.createElement('span');
    sspan.className = 'urlid';
    sspan.appendChild(document.createTextNode(modurlid));
    span.appendChild(sspan);

    sspan=document.createElement('span');
    sspan.className = 'version';
    sspan.appendChild(document.createTextNode(modversion));
    span.appendChild(sspan);
    p.appendChild(span);

    if(modvalid == "") {
        span=document.createElement('span');
        span.className = 'modvalid';
        var img = document.createElement('img');
        img.setAttribute("src", "/_lib/kolekti/icons/dialog-warning.png");
        img.setAttribute("title", i18n("[0346]Module mal formé"));
        span.appendChild(img);
        p.appendChild(span);
    }

    //create span for displayname
    span=document.createElement('span');
    span.className = 'modtitle';
    span.setAttribute('title',modresid.replace('@', ''));
    span.appendChild(document.createTextNode(modname));
    span.addEventListener('click',function(e){me.open_module(e)},false);
    p.appendChild(span);

    this.addopenevent(span, modresid, modurlid);

    //create actions
    span=document.createElement('span');
    span.className = 'tramemodactions';
    p.appendChild(span);

    mod.appendChild(p);
    dest.parentNode.insertBefore(mod,dest);
    //this.initjq();
    this.init_dnd();
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

trameeditor.prototype.update_mod_title=function(mod) {
    var url,span,titlespan,modinfo,i;
    // get url of the module, as well as the span that carries the title
    var spans=mod.getElementsByTagName('SPAN');
    for (i=0;i<spans.length;i++) {
    span=spans.item(i);
    if (span.className=='resid') {
        url=kolekti.get_url(span.firstChild.nodeValue);
    }
    else if (span.className=='modtitle') {
        titlespan=span;
    }
    }

    // get module properties
    var props=[ 
        {propname:"objectinfos", ns:"kolekti:comes"},
        {propname:"version", ns:"kolekti:modules"}
    ];
    var conn=new ajaxdav(url);
    var req=conn.PROPFIND(props,0);
    var xp="/d:multistatus//d:propstat[d:status='HTTP/1.1 200 Ok']/d:prop/*"
    if (req.result.status == 207) {
    var props=req.result.xml.evaluate(xp, req.result.xml, kolektiNsResolver, XPathResult.ANY_TYPE, null );
      var thisNode = props.iterateNext();
    while (thisNode) {
        if (thisNode.localName=="version") {
        modversion=thisNode.textContent;
        }
        if (thisNode.localName=="objectinfos") {
        modinfo=kolekti.parse_info_props(thisNode);
        if (modinfo.owner.userclass=='self') modinfo.owner.picto='/_lib/icons/comes/MEicon.png';
        if (modinfo.owner.userclass=='other') modinfo.owner.picto='/_lib/icons/comes/Usericon.png';
        if (modinfo.owner.userclass=='ref') modinfo.owner.picto='/_lib/icons/comes/TReficon.png';
        }
        thisNode = props.iterateNext();
    }
    modinfo.resume=url.replace('@', '');
    }
    titlespan.setAttribute('title',modinfo.resume);
}

trameeditor.prototype.addopenevent=function(span,resid,urlid,version) {
    var url=kolekti.get_url(resid,version);
    span.addEventListener('click',function(e){kolekti.notify('resource-display-open',{"url":url,"resid":urlid},null)},false);
}

trameeditor.prototype.localurl=function(url) {
    var parts=url.split('/');
    return parts[parts.length-1];
}

// Serialization to xml
trameeditor.prototype.get_data=function() {
    var xmlbuf="";
    xmlbuf='<trame xmlns="kolekti:trames">';
    xmlbuf+='<head><title>'+xmlcontent(this.context.title.nodeValue)+'</title></head>';
    xmlbuf+="<body>";
    var n;
    var trame=$(this.context.domview).find(".trame")[0];
    var c=$(trame).children('.section, .module').get();
    for (n in c) {
    if ($(c[n]).hasClass('module')) {
        xmlbuf+=this.xml_module($(c[n]).get());
    }
    else 
    {
        xmlbuf+=this.xml_sect($(c[n]).get())
    }
    }
    xmlbuf+="</body>";
    xmlbuf+="</trame>";
    return xmlbuf;
}

trameeditor.prototype.xml_sect=function(elt) {
    var xmlbuf="<section>";
    xmlbuf+='<title>'+xmlcontent($(elt).children('p.title').text().replace(/^\s*|\s*$/g, ""))+'</title>';
    var n;
    var c=jQuery(elt).children('.section, .module').get();
    for (n in c) {
    if ($(c[n]).hasClass('module')) {
        xmlbuf+=this.xml_module($(c[n]).get());
    }
    else 
    {
        xmlbuf+=this.xml_sect($(c[n]).get())
    }
    }
    return xmlbuf+'</section>';
}

trameeditor.prototype.xml_module=function(elt) {
    var xmlbuf="<module resid='";
    xmlbuf+=xmlattr($(elt).find('span.resid').text());
    /*xmlbuf+="' version='";
    xmlbuf+=xmlattr($(elt).find('span.version').text());*/
    xmlbuf+="' type='";
    xmlbuf+=xmlattr($(elt).find('p').attr('class'));
    /*xmlbuf+="' enabled='";
    xmlbuf+=$(elt).find('span.modactions .enabled')[0].display == "inline" ? 0:1;*/
    xmlbuf+="'/>";

    return xmlbuf;
}

trameeditor.prototype.publish = function(arg) {
    if (!this.statesaved){
        if (confirm(i18n("[0318]%(title)s a été modifié, voulez-vous sauvegarder avant ?", {"title": this.context.title.textContent}))) {
            this.do_save();
            this.open_publish_view(arg.url);
        }
    } else {
        this.open_publish_view(arg.url);
    }
}

//Open publish view on new window
trameeditor.prototype.open_publish_view = function(url) {
    // Store current tab in session
    var splitUrl = url.split('trames/');
    var orderurl = splitUrl[0];
    orderurl += 'configuration/orders/_';
    var arg = new Object();
    arg['urlid'] = this.context.id;
    window.open(orderurl+"?viewer=orderseditor&mode=detached&trame="+splitUrl[1], null, config='height=400, width=800, toolbar=no, menubar=no, scrollbars=no, resizable=no, location=no, directories=no, status=no');
}
