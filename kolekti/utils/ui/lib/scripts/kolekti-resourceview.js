/*
 *    kOLEKTi : a structural documentation generator
 *    Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Affero General Public License as
 *   published by the Free Software Foundation, either version 3 of the
 *   License, or any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the GNU Affero General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/*
   Class for the kolekti ResourceView component manager
*/
//author Stéphane Bonhomme <stephane@exselt.com>

// resource view component : handles the main component, 
// able to display several resources

function kolekti_resview(id) {
    this.id=id;
    this.tabnb=0;
    this.tabs=new Array();
    this.actions=new Array();
    this.currenttab = null;
    this.initopen=new Array();
    this.context='viewer';
    this.overlay=true; // 
    //this.initevent();
}

kolekti_resview.prototype.initevent = function() {
    var me=this;
    kolekti.listen('resource-display-open',function(arg){me.cb_open(arg);return true;},null);
    kolekti.listen('resource-delete',function(arg){me.cb_close(arg);return true;},null);    
}

// asked for opening a resource
kolekti_resview.prototype.cb_open = function(arg) {
    if (arg['version'])
    this.displayresource(arg['url'],arg['urlid'],null,arg['version']);
    else
    this.displayresource(arg['url'],arg['urlid']);
}

// asked for closing a resource
kolekti_resview.prototype.cb_close = function(arg) {
    if(!arg['urlid']) {
        for(var tab in this.tabs) {
            if(this.tabs[tab].url == arg['url'])
                arg['urlid'] = this.tabs[tab].id;
        }
    }
    if (!this.tabs[arg['urlid']]) return;
    this.tabs[arg['urlid']].close();
}

// unique timestamp
kolekti_resview.prototype.unique = function() {
    d=new Date();
    return d.getTime();
}

// at initialisation add a resource to be displayed
kolekti_resview.prototype.addinitopen= function(url,urlid,version) {
    var ts=new Object();
    ts.url=url;
    ts.urlid=urlid;
    ts.version=version;
    this.initopen.push(ts);
}

// init function,called after full page is loaded
kolekti_resview.prototype.init= function() {
    var me=this;
    this.initsession();
    return function attachobject(e) {
    var i;
    var rv;
    rv=document.getElementById("resourceview_"+me.id)
    rv.kolekti=me;

    // backrefences from dom nodes to kolekti objects
    me.domtabs=document.getElementById('resourceview_tabs_'+me.id);
    me.domview=document.getElementById('resourceview_view_'+me.id);
    me.domroot=document.getElementById('resourceview_'+me.id);
    me.domroot.kolektiobj=me;
    me.menu=new kolekti_resview_menu(me);

    // open tabs that where stored in session
    for (i=0;i<me.initopen.length;i++) {
        if(me.initopen[i].url != "")
            me.displayresource(me.initopen[i].url,me.initopen[i].urlid,true,me.initopen[i].version);
    }

    // displays the current tab
    if (me.currenttab) {
        me.currenttab.show();
    }
    };
}

// init tabs in session
kolekti_resview.prototype.initsession= function() {
    var props=[{ns:'kolekti:session',propname:'sessionvalue'}];
    var conn = new ajaxdav('/_session/'+this.id);
    var req=conn.PROPFIND(props,0); 
    if (req.result.status == 207) {
    var dirs=req.object;
    dirs.nextResponse();
    var p=dirs.get_prop('kolekti:session','sessionvalue');
    try {
        var tab=p.content.firstChild.firstChild;
        while(tab) {
        this.addinitopen(tab.getAttribute('url'),
                 tab.getAttribute('urlid'),
                 tab.getAttribute('version'))
            tab=tab.nextSibling;
        }
    }
    catch (e){}
    }
}

// data to be stored in session
kolekti_resview.prototype.session_data=function() {
    var buf="<tabs xmlns='kolekti:sessiondata'>";
    for (var urlid in this.tabs) {
    buf+=this.tabs[urlid].session_data();
    }
    buf+="</tabs>";
    return buf
}

// data to be stored in session
kolekti_resview.prototype.update_session=function() {
    var conn = new ajaxdav('/_session/'+this.id);
    var props = conn.PROPPATCH([{ns:'kolekti:session',propname:'sessionvalue',propval:this.session_data()}],[]);
}

// actually display a resource
kolekti_resview.prototype.displayresource= function(url,urlid,noload,version) {
    // hide the current tab if any
    this.hide_current();
    this.menu.hide_menu();
    if (!this.tabs[urlid]) {
    // if no tab exists for the resource, create a tab
    var newtabobj=this.newtab(url,urlid);
    this.tabs[urlid]=newtabobj;
    this.currenttab=newtabobj;
    if (!noload){
        newtabobj.show(version);
    } else {
        newtabobj.set_title(version);
    }
    this.menu.add_item(urlid,newtabobj);
    //this.sessionaddtab(urlid,url,version);
    } else {
    // show the existing tab
    this.tabs[urlid].show(version);
    }
}

// create a new tab
kolekti_resview.prototype.newtab= function(url,urlid) {
    var tab;
    if (typeof(this.custom_resource_tab)=="function") {
    // if the viewer has a custom tab creation function
    tab=this.custom_resource_tab(this,url,urlid,this.overlay);
    } else {
    // creates a standard kolekti resource tab
    tab=new kolekti_resource_tab(this,url,urlid,this.overlay);
    }
    tab.create();
    return tab;
}

// hide the current tab
kolekti_resview.prototype.hide_current= function() {
    if (this.currenttab)
    this.currenttab.hide();
}

// destroys a tab, to be called after all resources are free
kolekti_resview.prototype.remove= function(urlid) {
    delete this.tabs[urlid];
    this.update_session();
    this.menu.hide_menu();
    this.menu.remove_item(urlid);
}


// -----------------------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------------------

// resource view menu : drop down 

function kolekti_resview_menu(resview) {
    this.parent=resview;
    this.id=resview.id;
    this.entries=new Array();
    this.dommenu=document.getElementById('resourceview_menu_'+resview.id);
    var me=this;
    //this.dommenu.addEventListener("mouseout",function(e){e.cancelBubble=true;me.hide_menu(e)},false);
}

kolekti_resview_menu.prototype.show_menu = function() {
    var i,e,item,itemlbl;
    var me=this;
    //empty the menu
    while (this.dommenu.firstChild)
    this.dommenu.removeChild(this.dommenu.firstChild);
    
    //build the menu
    for (i in this.entries) {
    e=this.entries[i];
    if (e.tab != this.parent.currenttab) {
        item=document.createElement('li')
        itemlbl=document.createTextNode(e.tab.get_title());
        item.appendChild(itemlbl);
        if (this.dommenu.firstChild)
        this.dommenu.insertBefore(item,this.dommenu.firstChild);
        else
            this.dommenu.appendChild(item);
        item.addEventListener("click",function(e){e.cancelBubble=true;me.select_entry(e)},false);
        item.kolekti={urlid:e.urlid,tab:e.tab};
    }
    }

    //show the menu
    this.dommenu.style.display="block";
}

kolekti_resview_menu.prototype.hide_menu = function() {
    this.dommenu.style.display="none";
}

kolekti_resview_menu.prototype.basc_menu = function() {
    if (this.dommenu.style.display=="none") 
    this.show_menu();
    else
    this.hide_menu();
}

kolekti_resview_menu.prototype.select_entry = function(e) {
    var item=e.currentTarget;
    this.hide_menu();
    item.kolekti.tab.click(null);
}

kolekti_resview_menu.prototype.add_item = function(urlid, tab) {
    for (i in this.entries) {
    e=this.entries[i];
    if (e.urlid==urlid)
        this.entries.splice(i,1);
    }
    this.entries.push({urlid:urlid,tab:tab});
}

kolekti_resview_menu.prototype.remove_item = function(urlid) {
    var i,e;
    for (i in this.entries) {
    e=this.entries[i];
    if (e.urlid==urlid) {
        this.entries.splice(i,1);
        return;
    }
    }
}



// -----------------------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------------------

// Tab object

function kolekti_resource_tab(component,url,id,overlay) {
    this.id=id;
    this.url=url;
    this.parent=component;
    this.view=component;
    this.overlay=overlay;
    this.version=null;
    this.viewok=false;
    this.active=false;
    this.initevent();
}

// list of properties to get at tab creation
kolekti_resource_tab.prototype.list_properties=[
    {ns:'kolekti:viewer',propname:'views'},
    {ns:'DAV:',propname:'displayname'},
    {ns:'kolekti',propname:'owner'},
    {ns:'kolekti:modules',propname:'version'},
    {ns:'kolekti',propname:'resourceid'}
];

kolekti_resource_tab.prototype.session_data=function() {
    buf="<tab ";
    buf+="url='"+this.url+"' ";
    buf+="urlid='"+this.id+"' ";
    buf+="version='"+this.version+"' ";
    buf+="view='"+this.viewerclass+"' ";
    if (this.active) {
    buf+="active='1' ";
    }
    buf+="/>";
    return buf;
}

// initialize the kolekti events 
kolekti_resource_tab.prototype.initevent= function() {
    var me=this;
    kolekti.listen('resource-display-rename',function(arg){me.cb_renamed(arg);return true;},this.id);
    kolekti.listen('resource-display-move',function(arg){me.cb_moved(arg);return true;},this.id);
    kolekti.listen('resource-display-delete',function(arg){me.cb_deleted(arg);return true;},this.id);
    kolekti.listen('resource-change-view',function(arg){me.change_view(arg);return true;},this.id);
    kolekti.listen('resource-substitute',function(arg){me.cb_substitute(arg);return true;},this.id);
}

// get properties 
kolekti_resource_tab.prototype.init_properties = function() {
    var conn=new ajaxdav(this.url);
    if(conn instanceof ajaxdav) {
        var req=conn.PROPFIND(this.list_properties,0);

        if (req.result.status == 207) {
        var xpr=req.result.xml.evaluate( '/d:multistatus/d:response/d:propstat[starts-with(d:status,"HTTP/1.1 200")]/d:prop', req.result.xml, kolektiNsResolver, XPathResult.FIRST_ORDERED_NODE_TYPE, null );
        this.properties=xpr.singleNodeValue;
        }

        return true;
    }
    return false;
}

// get a text property
kolekti_resource_tab.prototype.gettextprop = function(name,ns) {
    var xpr=this.properties.firstChild;
    while (xpr) {
    if (xpr.localName==name && xpr.namespaceURI==ns) {
        return xpr.textContent;
    }
    xpr=xpr.nextSibling;
    }
    return null;
}

// Create a new tab
kolekti_resource_tab.prototype.create = function() {
    var me=this;
    // get the properties of the resource
    if(this.init_properties()) {
        // create the tab dom nodes
        this.domtabclass="resource-tab";
        this.domtab=document.createElement('li');
        this.parent.domtabs.appendChild(this.domtab);
        this.domtab.setAttribute('id', this.id);
        this.domtab.setAttribute('class', this.domtabclass+' selected');
        this.domtab.setAttribute('title', this.url);
        this.domtab.addEventListener("click",function(e){me.click(e)},false);
        this.domtab.kolektiobj=this;

        // tab creation
        var linktab=document.createElement('span');
        linktab.setAttribute('class', 'tab resourceview-tab-label');

        // menu button
        var btnmenu=document.createElement('img');
        btnmenu.setAttribute('src', '/_lib/kolekti/icons/btn_menu.png');
        btnmenu.setAttribute('alt', 'V ');
        btnmenu.setAttribute('class', 'tab_button_menu ');
        btnmenu.addEventListener("click",function(e){e.cancelBubble=true;me.tabmenu()},false);
        linktab.appendChild(btnmenu);

        // label
        var linktab2=document.createElement('span');
        //linktab2.addEventListener("click",function(e){me.click(e)},false);
        this.title=document.createTextNode(this.gettextprop('displayname','DAV:'));
        linktab2.appendChild(this.title);
        linktab.appendChild(linktab2);

        // close button
        var closetab=document.createElement('img');
        closetab.setAttribute('src', '/_lib/kolekti/icons/btn_close.png');
        closetab.setAttribute('alt', 'X');
        closetab.addEventListener("click",function(e){e.cancelBubble=true;me.close()},false);
        linktab.appendChild(closetab);

        this.domtab.appendChild(linktab);

        // if overlay : create a new resourceview content (display area attached to tab)
        if (this.overlay) {
        this.domview=document.createElement('div');
        this.domview.setAttribute('id', "resview_content"+this.id);        
        this.domview.setAttribute('class', 'resourceview_view resourceview_content');
        this.parent.domview.appendChild(this.domview);
        }
    }
}

// get the viewerclass to apply 
kolekti_resource_tab.prototype.get_viewerclass = function() {
    // checks if the resource viewclass is allowed, 
    // otherwise select the default / first viewerclass available for this resource
    var xpr,vc,vn,vid;
    var viewerclass=this.viewerclass;
    this.viewerclass=false;

    xpr=this.properties.firstChild;
    while (xpr) {
    if (xpr.localName=="views" && xpr.namespaceURI=="kolekti:viewer") {
        vn=xpr.firstChild;
        while (vn) {
        if (vn.nodeType==1) {
            vc=vn.getAttribute('id');
            if (!this.viewerclass)
            this.viewerclass=vc;
            if (vc==viewerclass) {
            this.viewerclass=vc;
            break;
            }
            vid=vn.getAttribute('active');
            if (vid=="yes") {
            this.viewerclass=vn.getAttribute('id');
            }
        }
        vn=vn.nextSibling;
        }
    }
    xpr=xpr.nextSibling;
    }
}

// the displayed resource has changed of name/url/ower, re-init without reloading (save as..)
kolekti_resource_tab.prototype.cb_substitute = function(url) {
    var v, xpr,vc,vn,vid;
    var viewerclass=this.viewerclass;
    var oldurl=this.url;
    this.url=url;
    if(this.init_properties()) {
        var oldid=this.id;
        this.id=oldid.split('_')[0]+'_'+this.gettextprop('resourceid','kolekti');
        var version=this.gettextprop('version','kolekti:modules');
        this.set_title(version);

        this.parent.tabs[this.id]=this;
        this.initevent();

        kolekti.notify('browser-highlight',{'url':oldurl, 'urlid':oldid, 'del':true},null);
        kolekti.unlisten(oldid);
        delete this.parent.tabs[oldid];
        //this.parent.sessiondeltab(oldid);
        //this.parent.sessionaddtab(this.id,url,version);
        //kolekti.del_session_value('/'+this.view.id+'/'+oldid);
        //kolekti.set_session_value('/'+this.view.id+'/'+this.id, url+'?version='+version);
        this.parent.update_session()

        this.get_viewerclass();

        if (this.viewerclass  == viewerclass) {
        // did not change the view : re-init actions
        this.viewer.url=url;
        this.viewer.reset_ui();
        this.viewer.getresprops();
        this.viewer.init_ui();
        } else {
        // the previous view was not allowed for the new resource, change the view
        v=this.context.get_dom_view();
        while(v.firstChild)
            v.removechild(v.firstChild);
        this.viewer=this.parent.getViewer(this.viewerclass, this.id);
        this.viewer.init(this.viewerclass,this);
        }
        this.domtab.setAttribute('class', this.domtabclass+' selected');
    }
}

// a resource has been renamed: refresh the tab name
kolekti_resource_tab.prototype.cb_renamed = function(arg) {
    kolekti.notify('browser-refresh-dir',arg,null);
    if(arg.urlid.search(/[a-zA-Z]+_[a-zA-Z0-9]+/) < 0)
        arg.urlid = this.context.id.split('_')[0]+'_'+arg.urlid;
    this.parent.displayresource(arg.url, arg.urlid); 
    this.close();
}

// a resource has been deleted : close and destroy the tab
kolekti_resource_tab.prototype.cb_deleted = function(arg) {
    kolekti.notify('browser-refresh-dir',arg,null);
    this.close();
}

// a resource has been moved, refresh the tab content
kolekti_resource_tab.prototype.cb_moved = function(arg) {
    kolekti.notify('browser-refresh-dir',arg,null);
    this.parent.displayresource(arg.url, arg.urlid); 
    this.close();
}

// a tab has benn clicked, update content
kolekti_resource_tab.prototype.click = function(e) {
    this.parent.hide_current()
    this.show(this.version);
    kolekti.notify('browser-refresh-dir',{'url':this.url},null);
}

// the tab menu button has been clicked, display all tabs 
kolekti_resource_tab.prototype.tabmenu = function(e) {
    this.parent.menu.basc_menu();
}

kolekti_resource_tab.prototype.set_title = function(version) {
    this.version=version;
    this.title.nodeValue=this.gettextprop('displayname','DAV:');
}

kolekti_resource_tab.prototype.get_title = function() {
    return this.title.nodeValue;
}

kolekti_resource_tab.prototype.set_view = function(view) {
    // removes all listeners associated to this tab
    kolekti.unlisten(this.id);

    this.initevent();

    this.viewerclass=view;
    this.get_viewerclass();
    this.viewok=false;
    this.show(this.version);
}

kolekti_resource_tab.prototype.change_view = function(arg) {
    var do_change=false;
    if (!kolekti.notify('quit-page',null,this.id)){
    if (confirm(i18n("[0307]%(title)s a été modifié, voulez-vous réellement fermer sans enregistrer ?", {'title':this.title.textContent}))) {
        do_change=true;
    }
    } else {
    do_change=true;
    }
    if (do_change) {
    this.viewok=false;
    this.set_view(arg.view);
    }
}

kolekti_resource_tab.prototype.get_dom_view = function() {
    if (this.overlay) {
    return this.domview;
    } else {
    return this.parent.domview;
    }
}

// display a resource, in a given version
kolekti_resource_tab.prototype.show = function(version) {
    var view,viewer,viewerclass,vid;
    view=this.get_dom_view();

    if (version == null)
    version =  this.gettextprop('version','kolekti:modules');
    if (this.version == null)
    this.version=version;

    if (this.version != version) {
    this.viewok=false;
    this.version=version;
    }

    if(version==null)
        version = "";

    //kolekti.set_session_value('/'+this.view.id+'/'+this.id,this.url+'?version='+version);
    //this.parent.sessionaddtab(this.id,this.url,version);

    if (!this.overlay || !this.viewok) {
    // fetch the content of the tab

    // remove all existing content
    while (view.firstChild) {
        view.removeChild(view.firstChild);
    }

    this.domtabclass="resource-tab";
    this.set_title(version);
    this.get_viewerclass();

    // calls the generated function (dialog-resourceview.xsl)
    this.viewer=this.parent.getViewer(this.viewerclass, this.id);

    // inits the viewer
    this.viewer.init(this.viewerclass,this);
    this.viewok=true;
    }

    var tabview = view.parentNode;
    tabview.className = "resourceview "+this.domtabclass.split(' ')[0];

    view.setAttribute('style', 'display:block;');
    this.active=true;
    this.domtab.setAttribute('class', this.domtabclass+' selected');
    this.parent.currenttab=this;
    this.parent.menu.add_item(this.id,this)
    this.init_ui();
    this.parent.update_session();
    kolekti.notify('browser-highlight',{'url':this.url, 'urlid':this.id}, null);
    if(this.viewer.sidebar)
        kolekti.notify('sidebar-refresh-ui',this.viewer.sidebar.dom,this.viewer.sidebar.id);

}

kolekti_resource_tab.prototype.init_ui = function() { }

// hide a tab
kolekti_resource_tab.prototype.hide = function() {
    this.domtab.setAttribute('class', this.domtabclass);
    if (this.overlay)
    this.domview.setAttribute('style', 'display:none;');
    this.active=false;
}

// close a tab
kolekti_resource_tab.prototype.close = function() {
    if (!kolekti.notify('quit-page',null,this.id)){
    if (!confirm(i18n("[0307]%(title)s a été modifié, voulez-vous réellement fermer sans enregistrer ?", {'title':this.title.textContent})))
        return;
    }
    kolekti.unlisten(this.id);
    var newtab=null;
    if (this.overlay)
    this.domview.parentNode.removeChild(this.domview);
    if (this.parent.currenttab==this) {
    if (!this.overlay)
        this.parent.domview.innerHTML="";
    if (this.domtab.previousSibling && this.domtab.previousSibling.nodeType==1) {
        newtab=this.domtab.previousSibling.kolektiobj;
    } else if (this.domtab.nextSibling && this.domtab.nextSibling.nodeType==1) {
        newtab=this.domtab.nextSibling.kolektiobj;
    }
    }
    this.domtab.parentNode.removeChild(this.domtab);
    this.parent.remove(this.id);
    kolekti.notify('browser-highlight',{'url':this.url, 'urlid':this.id, 'del':true},null);
    newtab && newtab.show();
}



// -----------------------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------------------
function kolekti_viewer() { }

kolekti_viewer.prototype.list_properties = [{ns:'kolekti:viewer',propname:'views'},
                        {ns:'kolekti:viewer',propname:'vieweractions'},
                        {ns:'kolekti:viewer',propname:'clientactions'},
                        {ns:'kolekti:modules',propname:'version'}];

kolekti_viewer.prototype.getresprops= function() {
    var conn=new ajaxdav(this.url);
    if(conn instanceof ajaxdav) {
        this.props=false;

        var req=conn.PROPFIND(this.list_properties,0);
        
        if (req.result.status == 207) {
        var xpr=req.result.xml.evaluate( '/d:multistatus/d:response/d:propstat[starts-with(d:status,"HTTP/1.1 200")]/d:prop', req.result.xml, kolektiNsResolver, XPathResult.FIRST_ORDERED_NODE_TYPE, null );
        this.props=xpr.singleNodeValue;
        }
    }
}

kolekti_viewer.prototype.getversion = function() {
    var xpr=this.props.firstChild;
    while (xpr) {
    if (xpr.localName=="version" && xpr.namespaceURI=="kolekti:modules") {
        return xpr.textContent;
    }
    xpr=xpr.nextSibling;
    }
    return null;
}

kolekti_viewer.prototype.init = function(viewname,tab) {
    this.context=tab;
    this.viewname=viewname;
    this.url=this.context.url;
    this.version=this.context.version;
    this.load();
    var me=this;
}

kolekti_viewer.prototype.load = function(url) {
    this.getresprops();

    // creer les éléments d'interface de la vue
    this.create_ui();
    //var latest=this.getversion()
    //if (latest == null || latest == this.version) { 
    this.init_ui();
    //} 

    // afficher la ressource
    this.load_resource();
}

kolekti_viewer.prototype.load_resource = function() {
    var e_wait=document.getElementById('ajax-indicator');
    var e_waitlocal=e_wait.cloneNode(true);
    this.content.appendChild(e_waitlocal);
    e_waitlocal.style.display='block';
    this.load_resource_wait();
    try {
    this.content.removeChild(e_waitlocal);
    } catch (e) {
    }
}

kolekti_viewer.prototype.load_resource_wait = function() {
    this.fetch_resource();
}

kolekti_viewer.prototype.fetch_resource = function() {
    var ifrw=document.createElement('div');
    ifrw.className="iframe_container";
    var ifr=document.createElement('iframe');
    var url=this.url+'?viewer='+this.viewname;
    //if (this.version != null)
        //url=url+"&rev="+this.version;

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

kolekti_viewer.prototype.create_ui = function() {
    var c=this.context.get_dom_view();
    var actionsp=document.createElement('p');
    actionsp.className="vieweractions";
    this.vieweractions=document.createElement('span');
    this.vieweractions.className="vieweractions";
    actionsp.appendChild(this.vieweractions);

    this.clientactions=document.createElement('span');
    this.clientactions.className="clientactions";
    actionsp.appendChild(this.clientactions);

    this.content=document.createElement('div');
    this.contentactions=document.createElement('div');
    this.contentactions.className="contentactions";
    c.appendChild(this.content);
    this.contentactions.appendChild(actionsp);
    this.content.appendChild(this.contentactions);
}

kolekti_viewer.prototype.reset_ui = function() {
    while (this.vieweractions.firstChild)
    this.vieweractions.removeChild(this.vieweractions.firstChild);
    while (this.clientactions.firstChild)
    this.clientactions.removeChild(this.clientactions.firstChild);
    if(this.sidebar)
        this.sidebar.dom.parentNode.removeChild(this.sidebar.dom);
}

kolekti_viewer.prototype.init_ui = function(props) {
    this.init_viewer_actions();
    if(this.sidebar)
        this.init_sidebar();
}

kolekti_viewer.prototype.init_viewer_actions = function() {
    // recupérer les actions
    this.altviews=new Array();
    var vn;
    var xpr=this.props.firstChild;
    while (xpr) {
    if (xpr.localName=="views" && xpr.namespaceURI=="kolekti:viewer") {
        vn=xpr.firstChild;
        while (vn) {
        if (vn.nodeType==1) {
            v=new Object();
            vact=vn.getAttribute('active');
            if (vact=="yes") {
            v.active=true;
            }
            v.class=vn.getAttribute('id');
            this.altviews.push(v)
        }
        vn=vn.nextSibling;
        }
    }
    if (xpr.localName=="vieweractions" && xpr.namespaceURI=="kolekti:viewer") {
        vn=xpr.firstChild;
        while (vn) {
        if (vn.nodeType==1) {
            var act=vn.getAttribute('id');
            if (kolekti.actions[act] && this.actions[act]) {
            var but=this.create_action_button(act);
            this.vieweractions.appendChild(but);
            }
        }
        vn=vn.nextSibling;
        }
    }
    if (xpr.localName=="clientactions" && xpr.namespaceURI=="kolekti:viewer") {
        vn=xpr.firstChild;
        while (vn) {
            if (vn.nodeType==1) {
                var act=vn.getAttribute('id');
                if (kolekti.actions[act] && this.actions[act]) {
                    var but=this.create_action_button(act);
                    this.clientactions.appendChild(but);
                }
            }
            vn=vn.nextSibling;
        }
    }
    xpr=xpr.nextSibling;
    }
}

kolekti_viewer.prototype.init_sidebar = function() {
    var sb = document.createElement('div');
    sb.className = "sidebar";
    this.sidebar.dom = sb;
    this.contentactions.appendChild(sb);
    this.sidebar.refresh(this.sidebar.dom);
}

kolekti_viewer.prototype.create_action_button = function(act) {
    var action=this.actions[act];
    var eltact=document.createElement('span');
    eltact.className="vieweritemaction";
    if (action['icon']) {
    var iconact=document.createElement('img');
    iconact.setAttribute('src',action['icon']);
    iconact.setAttribute('alt',action['name']);
    iconact.setAttribute('title',action['name']);
    eltact.appendChild(iconact);
    } else {
    var textact=document.createTextNode(action['name']);
    eltact.appendChild(textact);
    }
    if (action['shortname']) {
        snameact=document.createElement('span');
        snameact.className="viewershortnameaction";
        snameact.textContent = action['shortname'];
        eltact.appendChild(snameact);
    }
    eltact.kolekti=new Object();
    eltact.kolekti.browseraction=action.id;

    var me=this;

    eltact.addEventListener('click',function(e){me.vieweraction(e)},false);
    return eltact;
}

kolekti_viewer.prototype.vieweraction = function(e) {
    var action=e.currentTarget.kolekti.browseraction;
    kolekti.actions[action].set_url(this.url);
    kolekti.actions[action].set_context(this.context.id);
    kolekti.actions[action].do_action(this.action_args(action));
    kolekti.actions[action].viewer=this;
}

kolekti_viewer.prototype.action_args = function(action) {
    var params=new Object();
    params.version=this.version;
    return params;
}



// -----------------------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------------------
function kolekti_editor() {
}

kolekti_editor.prototype = new kolekti_viewer;

kolekti_editor.prototype.load_resource_wait = function() {
    if (this.check_lock()) {
    this.etag=this.get_etag();
    this.fetch_resource();
    }
}

kolekti_editor.prototype.check_lock = function() {
    return true;
}

kolekti_editor.prototype.get_etag = function() {
    var conn=new ajaxdav(this.url);
    if(conn instanceof ajaxdav) {
        var req=conn.PROPFIND([{ns:'DAV:',propname:'getetag'}],'0');
        if (req.result.status == 207) {
        xpr=req.result.xml.evaluate( '//d:getetag', req.result.xml, kolektiNsResolver, XPathResult.ANY_TYPE, null );
        thisNode = xpr.iterateNext();  
        if (thisNode) {
            return thisNode.textContent;
        }
        }
    }
}

kolekti_editor.prototype.init_ui = function() {
    this.init_editor_actions();
    this.init_viewer_actions();
    if(this.sidebar)
        this.init_sidebar();
}

kolekti_editor.prototype.get_owner_uid = function() {
    /*var xpr=this.context.properties.firstChild;
    while (xpr) {
        if (xpr.localName=="owner" && xpr.namespaceURI=="kolekti")
            return xpr.textContent;
        xpr=xpr.nextSibling;
    }    
    return '';*/
    return kolekti.uid;
}

kolekti_editor.prototype.can_save = function() {
    return kolekti.uid == this.get_owner_uid();
}

kolekti_editor.prototype.init_editor_actions = function() {
    var me=this;

    if (kolekti.uid != '0') {
    if(this.can_save()) {
        var eltact=document.createElement('span');
        eltact.className="vieweritemaction";
        iconact=document.createElement('img');
        iconact.setAttribute('src','/_lib/kolekti/icons/icon-save-off.png');
        iconact.setAttribute('alt',i18n("[0083]Enregistrer"));
        iconact.setAttribute('title',i18n("[0083]Enregistrer"));
        eltact.appendChild(iconact);
        var save=document.createElement('span');
        save.className="viewershortnameaction disabled";
        save.setAttribute('title',i18n("[0083]Enregistrer"));
        save.textContent=i18n("[0083]Enregistrer");
        eltact.appendChild(save);
        var act = new Object();
        act.icon = iconact;
        act.elt = save;
        this.save_action_button=act;
        this.vieweractions.appendChild(eltact);
        eltact.addEventListener('click',function(e){me.do_save(e)},false);
    }
    kolekti.listen('editor-resourcemodified',function(arg){me.cb_modified(arg);return true;},this.context.id);
    eltact=document.createElement('span');
    eltact.className="vieweritemaction";
    iconact=document.createElement('img');
    iconact.setAttribute('src','/_lib/kolekti/icons/icon-saveas-on.png');
    iconact.setAttribute('alt',i18n("[0285]Enregistrer sous..."));
    iconact.setAttribute('title',i18n("[0285]Enregistrer sous..."));
    eltact.appendChild(iconact);
    var saveas=document.createElement('span');
    saveas.className="viewershortnameaction enabled";
    saveas.setAttribute('title',i18n("[0285]Enregistrer sous..."));
    saveas.textContent=i18n("[0285]Enregistrer sous...");
    eltact.appendChild(saveas);
    var act = new Object();
    act.icon = iconact;
    act.elt = saveas;
    this.save_as_action_button=act;
    this.vieweractions.appendChild(eltact);
    this.contentactions.appendChild(this.vieweractions.parentNode);

    eltact.addEventListener('click',function(e){me.do_save_as(e)},false);
    kolekti.listen('quit-page',function(arg){return me.quit_page(arg);},this.context.id);
    }
    this.statesaved=true;
    kolekti.listen('save-as',function(arg){return me.do_save_as_cb(arg);},this.context.id);
}

kolekti_editor.prototype.quit_page = function(arg) {
    return this.statesaved;    
}

kolekti_editor.prototype.cb_modified = function(arg) {
    this.statesaved=false;
    if (this.save_action_button) {
        this.save_action_button.icon.setAttribute('src','/_lib/kolekti/icons/icon-save-on.png');
        this.save_action_button.elt.setAttribute('class','viewershortnameaction enabled');
    }
}

kolekti_editor.prototype.do_save_as=function() {
    var action='save_as'
    kolekti.actions[action].set_context(this.context.id);
    kolekti.actions[action].do_action(this.action_args(action));
}

kolekti_editor.prototype.do_save_as_cb=function(args) {
    var newdir, newid;
    var newurl=args.dirname+"/"+args.resname+'.'+args.extension;
    this.url = newurl;
    if (this.send_data(this.save_as_action_button)) {
    this.statesaved=true;
    this.etag=this.get_etag();
    kolekti.notify('resource-substitute',newurl,this.context.id);
    kolekti.notify('browser-refresh',{'url':args.dirname},null);
    kolekti.notify('browser-highlight',{'url':this.url, 'urlid':this.context.id}, null);
    if(kolekti.svnrevision)
        kolekti.notify('svnrevision-change',{'url':this.url}, null);
    
    return true;
    } else {
        alert(i18n("[0308]Echec lors de la sauvegarde"));
        return false;
    }
}

kolekti_editor.prototype.do_save=function() {
    // vérifier si y'a un lock
    // vérifer le etag

    var etag=this.get_etag();
    if (etag!=this.etag) {
    if(!confirm(i18n("[0309]La ressource a été modifiée sur le serveur, voulez-vous continuer ?")))
        return;
    }
    if (this.send_data(this.save_action_button)) {
    this.statesaved=true;
    this.save_action_button.icon.setAttribute('src','/_lib/kolekti/icons/icon-save-off.png');
    this.save_action_button.elt.setAttribute('class','viewershortnameaction disabled');
    this.etag=this.get_etag();
    if(this.sidebar)
        kolekti.notify('sidebar-refresh',this.sidebar.dom,this.sidebar.id);
    if(kolekti.svnrevision)
        kolekti.notify('svnrevision-change',{'url':this.url}, null);
    } else {
        alert(i18n("[0308]Echec lors de la sauvegarde"));
    }
}

kolekti_editor.prototype.send_data=function(action) {
    var progress;
    var d=this.get_data();
    var conn=new ajaxdav(this.url);
    if(conn instanceof ajaxdav) {
        if (this.sidebar && this.sidebar.commitmsg) {
            conn.setHeader('KOLEKTICOMMIMSG', this.sidebar.commitmsg.value);
        }
        // Display progress icon during send data
        if(action) {
            progress = document.createElement('span');
            progress.className = "progress";
            action.elt.appendChild(progress);
        }

        var res=conn.PUT(d);

        // Remove progress icon
        if(action)
            action.elt.removeChild(progress);
        return res.status == 200;
    }
    return false;
}

kolekti_editor.prototype.get_data=function() {
    return "Dummy!";
}

kolekti_editor.prototype.action_args = function(action) {
    var args=new Object();
    if(action=="save_as") {
    var comps=this.url.split('/')
    var f=comps.pop();
    var fc=f.split('.');
    args.dirname=comps.join('/');
    args.extension=fc.pop();
    args.resname=decodeURI(fc.join('.'));
    }
    return args;
}
