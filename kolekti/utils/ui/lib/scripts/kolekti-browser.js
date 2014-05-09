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
   Class for the kolekti Browser objects
*/

//author Stéphane Bonhomme <stephane@exselt.com>

var kolekti_browser_node_type_directory=0
var kolekti_browser_node_type_file=1

function kolekti_browser_node(browser, id, url, etag, domnode, parent, type) {
    this.browser=browser;
    this.id=browser.id+'_'+id;
    this.etag=etag;
    this.url=url;
    this.resid='';
    this.domnode=domnode;
    this.parent=parent;
    this.type=type;
    this.updated=false;
    if (this.type == kolekti_browser_node_type_directory) {
    this.content= {};
    this.to_be_added= new Array();
    this.to_be_deleted= new Array();
    this.to_be_updated= new Array();
    this.is_collapsed=true;
    this.is_loaded=false;
    this.container=null;
    //this.get_dirstate();
    }
    if (parent) {
    parent.add_child(this);
    } else {
       this.root=this;
    }
}

// adds a node as child of a existing directory node
kolekti_browser_node.prototype.add_child = function(child) {
    if (this.type == kolekti_browser_node_type_file)
    return
    this.content[child.id]=child;
    this.to_be_added.push(child.id);
}

kolekti_browser_node.prototype.delete_node = function(child) {
    this.browser.remove_dom_structure(child);
    this.content[child.id] = null;
}

// get a child of a directory by its id
kolekti_browser_node.prototype.get_child = function(id) {

    if (this.type == kolekti_browser_node_type_file)
    return
    return this.content[id];
}

// get a child of a directory by its name
kolekti_browser_node.prototype.get_child_by_name = function(name) {
    var childid,childnode,n;
    if (this.type == kolekti_browser_node_type_file)
return
    for (childid in this.content) {
    childnode=this.content[childid];
    if (childnode) {
        childname=childnode.url.split('/').pop();
        if (name==childname)
        return childnode;
    }
    }
    return null;
}

// mark a node as updated
kolekti_browser_node.prototype.mark_update = function() {
    this.updated=true;
}

kolekti_browser_node.prototype.update = function() {
    var childid,childnode,n;
    for (childid in this.content) {
    childnode=this.content[childid];
    if (childnode) {
        if (!childnode.updated) {
        this.delete_node(childnode);
        }
        childnode.updated=false; 
    }
    }
}

kolekti_browser_node.prototype.update_node = function(childnode) {
    if(this.type == kolekti_browser_node_type_file)
      return;
    this.delete_node(childnode);
}

kolekti_browser_node.prototype.display = function() {
    var childid,childnode,n;
    this.sort();
    if(this.root)
        this.browser.set_behaviors(this.root);
    for (childid in this.content) {
    childnode=this.content[childid];
    if (childnode && childnode.domnode) {
        this.container.appendChild(childnode.domnode);
        this.browser.set_behaviors(childnode);
    }
    }
    if (!this.is_collapsed)
    this.browser.expand_node(this);
}

kolekti_browser_node.prototype.update_children = function() {
    var childid,childnode,n;

/*    for (n in this.to_be_updated) {
    childid=this.to_be_updated[n];
*/

    for (childid in this.content) {
    childnode=this.content[childid];
    if (childnode) {
        if (childnode.type == kolekti_browser_node_type_directory) {
        if (!childnode.is_collapsed) {
            childnode.request();
        }
        }
    }
    }
}

kolekti_browser_node.prototype.update_child = function(name) {
    var childid,childnode,n;
    var need_update = false;
    if (this.type == kolekti_browser_node_type_file)
       return null;
    for (childid in this.content) {
        childnode=this.content[childid];
        if (childnode) {
            var childname=childnode.url.split('/').pop();
            if (name==childname) {
                childnode.need_updated=true;
                need_update = true;
            }
        }
    }
    if (need_update) {
        this.is_loaded = false;
        this.request();
    }
    return null;
}

kolekti_browser_node.prototype.sort = function() { }

kolekti_browser_node.prototype.request= function(sync) {
    var conn=new ajaxdav(this.url);
    if(conn instanceof ajaxdav) {
    var me=this;
        conn.setHeader('KolektiContext','browser');
    conn.setHeader('KolektiBrowser',this.browser.id);
    if (this.is_loaded)
        conn.setHeader('If-None-Match',this.etag);
    if (!sync)
        conn.setCallback(function(req,data){me.request_callback(req)});
    this.browser.show_loading(this.id);
    var res=conn.PROPFIND(this.browser.properties,1);
    if (sync)
        this.request_callback(res);
    }
}

kolekti_browser_node.prototype.request_callback= function(req) {
    var xpr,p,pp,localprops;
    var childurl,childnode, childid,childetag,childtype, state, oldchild;

    if (req.result.status == 304) {
    // precondition failed : the etag sent was the same server-side, no update
    this.display();
    this.browser.hide_loading(this.id);
    // if recursive, recurse on sub-directories
    this.update_children();
    }
    else if (req.result.status == 207) {
    // update the directory content

    var xpr=req.object;
    while (xpr.nextResponse()) {
        // for each returned resource
        childurl=xpr.get_url();
        
        if (childurl==this.url) {
        p=xpr.get_prop('DAV:','getetag');
        if (p.status=="200") {
            pp=p.content;
            this.etag=pp.firstChild.nodeValue;
        }
        if (!this.domnode) {
            // load parent directory
            localprops=xpr.get_props('200');
            this.browser.create_dir_dom_structure(xpr,this)
            this.browser.attach_dir_behavior(this,localprops)
        }
        continue;
        }

        oldchild = null;

        // for sub elements 
        p=xpr.get_prop('kolekti','resourceid');
        if (p.status=="200") {
        childid=p.content.firstChild.nodeValue;
        }
        /*
        p=xpr.get_prop('DAV:','getetag');
        if (p.status=="200") {
        childetag=p.content.firstChild.nodeValue;
        }
            */
        p=xpr.get_prop('DAV:','resourcetype');
        childtype=kolekti_browser_node_type_file;
        if (p.status=='200')
        if (p.content.firstChild && p.content.firstChild.localName=="collection")
            childtype=kolekti_browser_node_type_directory
        
        // get the node of the child
        if(this.type == kolekti_browser_node_type_directory)
            childnode = this.get_child(this.browser.id+'_'+childid);

        // check if it is the same type of node (a collection may have been replaced with a resource or the contrary)
        if (childnode && childnode.type != childtype) {
        this.delete_node(childnode);
        childnode=null;
        }
        /*
        if (childnode) {
        // check etag change
        if (childnode.etag!=childetag) {
            if (childtype==kolekti_browser_node_type_directory) {
            this.mark_update(childnode);
            }
        }
                
        } else {
    */
        if(childnode && childnode.need_updated)
            oldchild = childnode;

        if (!childnode || childnode.need_updated) {
        //the node does not exists
        childnode=new kolekti_browser_node(this.browser,childid, childurl, '', null, this, childtype);

        localprops=xpr.get_props('200');
        if (childtype==kolekti_browser_node_type_file) {
            this.browser.create_file_dom_structure(xpr,childnode)
            this.browser.attach_file_behavior(childnode,localprops);
        } else {
            this.browser.create_dir_dom_structure(xpr,childnode)
            this.browser.attach_dir_behavior(childnode,localprops);
        }
        }

        p=xpr.get_prop('kolekti','resid');
        if (p.status=="200") {
        childnode.resid=p.content.firstChild.nodeValue;
        }

        // get the dir state
        if (childtype==kolekti_browser_node_type_directory) {
        p=xpr.get_prop('kolekti:usersession','dirstate');
        if (p.status=="200") {
            state=p.content.textContent;
            childnode.is_collapsed=(state!='1');
        }
        }

        if(oldchild && oldchild.need_updated) {
            this.browser.selection.remove_selection(oldchild.domnode);
            this.delete_node(oldchild);
            this.content[childnode.id] = childnode;
            this.browser.selection.add_selection(childnode.domnode);
        }
        childnode.mark_update();
    }
    this.is_loaded=true;
    //this.set_dirstate('1');
    this.update();
    this.display();
    this.browser.hide_loading(this.id);
    this.update_children();
    } else {
    this.browser.hide_loading(this.id);
    this.browser.display_error(kobj.id);
    }
}

kolekti_browser_node.prototype.set_dirstate=function() {
    var conn=new ajaxdav(this.url);
    conn.setHeader('KolektiContext','browser');
    conn.setHeader('KolektiBrowser',this.browser.id);
    conn.setCallback(function(req,data){});
    conn.PROPPATCH([{ns:'kolekti:usersession',propname:'dirstate',propval:(this.is_collapsed?'0':'1')}],[]);
}

kolekti_browser_node.prototype.collapse=function() {
    if (this.is_collapsed)
    return;
    this.is_collapsed=true;
    this.set_dirstate();
}

kolekti_browser_node.prototype.expand=function() {
    if (!this.is_collapsed)
    return;
    this.is_collapsed=false;
    this.set_dirstate();
}

kolekti_browser_node.prototype.expand_to=function(path) {
    if (this.type == kolekti_browser_node_type_file)
    return this;
    var next=path.split('/')[0];
    var tail=path.substr(next.length+1);
    if (this.is_collapsed) {
    this.is_collapsed=false;
    this.request();
    this.set_dirstate();
    } else {
    this.request();
    }
    var child=this.get_child_by_name(next)
    if (child)
        return child.expand_to(tail);
};

// browser object


function kolekti_browser(id) {
    this.id=id;
    this.tabs=new Array();
    this.behaviors=new Array();
    this.actions=new Array();
    this.actionspara=null;
    this.is_in_dialog=false;
    //this.displayresource=this.show_restab;
    this.currenttab=null;
    this.currenttabid=null;
    this.rootdir=null;
    this.tabnb=0;
    this.selection=new kolekti_browser_selection();
 }


// elements set by dialogs.xsl in page header (TODO : reduce as much as possible)

/*
-> instanciate the browser (browserid)
-> calls initevent()
-> sets .display property
-> sets .inittab property
-> Add Event to result of .init() on end page load

-> inits behaviors[] with objects
   - type
   - /params/  : sets with attributes (name=value)

-> inits actions[] with objects
  - shortname (if specified)
  - icon
  - /params/  : sets with attributes (name=value)

-> inits tabs[]  with objects
  - dir (if specfied)
 or
  - object : instanciate the object class, and calls object.init()

*/

 // list of properties to retreive 
 // browser global properties
     kolekti_browser.prototype.browserproperties=[
                       {ns:'kolekti:browser',propname:'mainbrowseractions'},
                       {ns:'kolekti:browser',propname:'rootdirbrowseractions'},
                       {ns:'kolekti:usersession',propname:'sorting'},
                       ];

 // ressources / collections properties 
kolekti_browser.prototype.properties=[
    {ns:'kolekti:browser',propname:'browseractions'},
    {ns:'kolekti:browser',propname:'browserbehavior'},
    {ns:'kolekti:browser',propname:'browsericon'},
    {ns:'kolekti:usersession',propname:'dirstate'},
    {ns:'kolekti',propname:'resourceid'},
    {ns:'kolekti',propname:'resid'},
    {ns:'DAV:',propname:'getetag'},
    {ns:'DAV:',propname:'displayname'},
    {ns:'DAV:',propname:'getcontenttype'},
    {ns:'DAV:',propname:'resourcetype'}
    //{ns:'DAV:',propname:'getlastmodified'}
];

// check if this browser uses some specific properties
kolekti_browser.prototype.has_property= function(ns,propname,propertyset) {
    if (!propertyset)
    propertyset=this.properties;
    for (p in propertyset) 
    if (propertyset[p].ns==ns && propertyset[p].propname==propname)
        return true;
    return false;
}

// get the first browsernode in ancestors
kolekti_browser.prototype.get_browser_node= function(elt) {
    while (elt && !elt.kolekti && !(elt.kolekti instanceof kolekti_browser_node)) {
    elt=elt.parentNode;
    }
    if (elt)
    return elt.kolekti;
}

// register all events incoming to the browser

 kolekti_browser.prototype.initevent= function() {
     var me=this;
     kolekti.listen('browser-highlight',function(arg){me.highlight(arg);return true;},null);
     kolekti.listen('browser-refresh',function(arg){me.refresh(arg);return true;},null);
     kolekti.listen('panelcontrol-change',function(arg){me.changepanel(arg);return true;},null);
 }

 // init function, called after page load
 kolekti_browser.prototype.init= function() {
     var me=this;
     return function attachobject(e) {
     document.getElementById('browser_'+me.id).kolektiobj=me;
     me.rootdir=document.getElementById(me.id+'_rootdir');
     if (me.inittab!=null)
         me.show_tab(me.inittab)
     if(!me.is_in_dialog)
         // no need to refresh on event when browser is in dialog
         me.initevent();
     }
 };

// init function, called at dialog opening
// called from the action object on dialog_open event
// the call is generated by xslt in dialog-actions.xsl
 kolekti_browser.prototype.init_in_dialog= function() {
     if (this.inittab_dialog)
     this.show_tab(this.inittab_dialog);
 
}

// handler for kolekti client event

kolekti_browser.prototype.refresh= function(args) {
    var path=args.url;
    var ctab,cdir;

    // select the tab

    for (ctab in this.tabs) {
    cdir=this.tabs[ctab].dir;
    
    if (cdir && path.substr(0,cdir.length)==cdir) {
        break;
    }
    }
    if (! this.currenttabid == ctab) {
    this.show_tab(ctab,true)
    }
    var tab=this.tabs[ctab];
    
    if (!tab || !tab.rootnode)
    return;

    if(args.file)
       tab.rootnode.update_child(path.substr(cdir.length+1));
    else
       tab.rootnode.expand_to(path.substr(cdir.length+1));
};

kolekti_browser.prototype.highlight= function(args) {
    var ctab,cdir;
    var path=args.url;

    // select the tab
    for (ctab in this.tabs) {
        cdir=this.tabs[ctab].dir;
        if (cdir && path.substr(0,cdir.length)==cdir)
            break;
    }

    var tab=this.tabs[ctab];
    if(tab && tab.rootnode) {
        var node = tab.rootnode.expand_to(path.substr(cdir.length+1));
        if(node) {
            if(args.del && this.selection.is_selected(node.domnode))
                this.selection.remove_selection(node.domnode);
            else
                this.selection.set_selection(node.domnode);
        }
    }
}

// displays or refresh a tab
kolekti_browser.prototype.show_tab= function(idtab) {
    if (this.currenttabid != idtab) {
    // remove directory content
    while(this.rootdir.firstChild)
        this.rootdir.removeChild(this.rootdir.firstChild)

    // if the tab is not the active tab
    if (this.currenttab) {
        this.currenttab.className="tab_"+this.currenttabid;
    }
    this.currenttab=document.getElementById('browsertab_'+this.id+'_'+idtab);
    this.currenttabid=idtab;
    if (this.currenttab)
        this.currenttab.className="selected tab_"+idtab;
    }

    var tab=this.tabs[idtab];
    if (tab.dir) { 
    if (!tab.rootnode) {
        tab.rootnode=new kolekti_browser_node(this,
                          'root', 
                          tab.dir, 
                          '', 
                          null, 
                          null, 
                          kolekti_browser_node_type_directory);

    } else {
        this.rootdir.appendChild(tab.rootnode.domnode);
    }

    tab.rootnode.request(true); // make sync connection for root node
    this.init_ui(tab);
    // the following has been moved into the end of create_dir_dom_structure
    // otherwise behaviors using jquery did not work
    //this.rootdir.appendChild(tab.rootnode.domnode); // insert the loaded node into the dom tree

    tab.rootnode.is_collapsed=false;
    this.expand_node(tab.rootnode);
    } else {
    if(tab.object)
        tab.object.display()
    }
};

kolekti_browser.prototype.init_ui = function(tab) {
    this.reset_ui(tab);

    var conn=new ajaxdav(tab.rootnode.url);
    if(conn instanceof ajaxdav) {
    var me=this;
    conn.setHeader('KolektiContext','browser');
    conn.setHeader('KolektiBrowser',this.id);
    conn.setCallback(function(req,data){me.init_ui_callback(req,data)});
    conn.setData(tab);
    conn.PROPFIND(this.browserproperties,0); 
    }
}

kolekti_browser.prototype.init_ui_callback = function(req,tab) {
    if (req.result.status == 207) {
    if (this.has_property('kolekti:browser','mainbrowseractions',this.browserproperties)) {
        var actionsp=document.createElement('p');
        actionsp.className="browseractions";
        
        var browseractions=document.createElement('span');
        browseractions.className="mainbrowseractions";
        actionsp.appendChild(browseractions);
        
        var clientactions=document.createElement('span');
        clientactions.className="clientactions";
        actionsp.appendChild(clientactions);

        this.attach_tab_behavior(actionsp,req.object,tab.rootnode.url)
        this.rootdir.parentNode.insertBefore(actionsp, this.rootdir);
        this.actionspara=actionsp;
    }
    }
}

kolekti_browser.prototype.reset_ui = function() {
    if(this.actionspara && this.actionspara.parentNode) 
    this.actionspara.parentNode.removeChild(this.actionspara);
    this.actionspara=null;
}

// removes structure from the dom tree (delete)
kolekti_browser.prototype.remove_dom_structure=function(node) {
    var elt=node.domnode;
    elt.parentNode.removeChild(elt);
}

// creates a file structure in the dom tree
kolekti_browser.prototype.create_file_dom_structure=function(xpr,node) {
    var e_direlt, parent
    e_direlt=document.createElement('li');
    e_direlt.kolekti=node;
    node.domnode=e_direlt;
    e_direlt.setAttribute('class','fileitem');
    e_direlt.setAttribute('id',node.id);
    
    // get the display name
    p=xpr.get_prop('DAV:','displayname');
    if (p.status=="200") {
    pp=p.content;
    if (pp && pp.firstChild)
        name=pp.firstChild.nodeValue;
    else
        name="??";
    }

    // get the icon
    p=xpr.get_prop('kolekti:browser','browsericon');
    icon='file';
    if (p.status=="200") {
    pp=p.content.firstChild;
    while (pp && pp.localName !='icon')
        pp=pp.nextSibling;
    if (pp) {
        icon=pp.getAttribute('src');
    } else {
        icon='mimetypes/gnome-mime-text';
        p=xpr.get_prop('DAV:','getcontenttype');
        if (p.status=="200") {
        pp=p.content;
        if (pp && pp.firstChild) {
            icon='mimetypes/gnome-mime-'+pp.firstChild.nodeValue.replace(/\//g,'-');
        } 
        }
    }
    }

    // create icon for files
    e_icon=document.createElement('img');
    e_icon.setAttribute('class','fileicon');
    e_icon.setAttribute('src','/_lib/kolekti/icons/'+icon+'.png');
    e_icon.setAttribute('alt','F');
    e_direlt.appendChild(e_icon);
    e_container=e_direlt;

    // create span with object name
    e_spanname=document.createElement('span');
    e_spanname.setAttribute('class','filename');
    e_spanname.appendChild(document.createTextNode(name));
    e_container.appendChild(e_spanname);

}

// creates a directory structure in the dom tree
kolekti_browser.prototype.create_dir_dom_structure=function(xpr,node) {
    var e_direlt, e_nameline, e_icon,  parent;
    var p,pp,icon,name;
    var me=this;
    e_direlt=document.createElement('li');
    e_direlt.kolekti=node;
    node.domnode=e_direlt;
    e_direlt.setAttribute('id',node.id);
    
    // get the display name
    p=xpr.get_prop('DAV:','displayname');
    if (p.status=="200") {
    pp=p.content;
    if (pp && pp.firstChild)
        name=pp.firstChild.nodeValue;
    else
        name="??";
    }

    // get the icon
    icon='dir';
    p=xpr.get_prop('kolekti:browser','browsericon');
    if (p.status=="200") {
    pp=p.content.firstChild;
    while (pp && pp.localName !='icon')
        pp=pp.nextSibling;
    if (pp) {
        icon=pp.getAttribute('src');
    }
    }

    // create p for directory line
    e_nameline=document.createElement('p');
    e_nameline.setAttribute('class','browserdirectoryline');

    // insert icon for dir closed
    e_icon=document.createElement('img');
    e_icon.setAttribute('class','diricon off');
    e_icon.setAttribute('src','/_lib/kolekti/icons/'+icon+'.png');
    e_icon.setAttribute('id','show_'+node.id);
    e_icon.setAttribute('alt','+');
    e_icon.addEventListener("click",function(e){me.expand_dir(e)},false)
    e_nameline.appendChild(e_icon);

    // insert icon for dir opened
    e_icon=document.createElement('img');
    e_icon.setAttribute('class','diricon on');
    e_icon.setAttribute('src','/_lib/kolekti/icons/'+icon+'_open.png');
    e_icon.setAttribute('id','hide_'+node.id);
    e_icon.setAttribute('style','display:none');
    e_icon.setAttribute('alt','-');
    e_icon.addEventListener("click",function(e){me.collapse_dir(e)},false)
    e_nameline.appendChild(e_icon);

    // insert directory name
    e_spanname=document.createElement('span');
    e_spanname.setAttribute('class','dirname');
    e_spanname.appendChild(document.createTextNode(name));
    e_nameline.appendChild(e_spanname);

    // insert icon for dir loading
    e_icon=document.createElement('img');
    e_icon.setAttribute('class','loadingicon');
    e_icon.setAttribute('src','/_lib/kolekti/icons/browser_loading.gif');
    e_icon.setAttribute('id','loading_'+node.id);
    e_icon.setAttribute('style','display:none;padding-left:5px');
    e_icon.setAttribute('alt',' *');
    e_nameline.appendChild(e_icon);

    // insert icon for dir loading error
    e_icon=document.createElement('img');
    e_icon.setAttribute('class','loadingerroricon');
    e_icon.setAttribute('src','/_lib/kolekti/icons/browser_error.png');
    e_icon.setAttribute('id','loading_'+node.id);
    e_icon.setAttribute('style','display:none;padding-left:5px');
    e_icon.setAttribute('alt',' /!\\');
    e_icon.setAttribute('title',' Erreur lors du chargement du dossier');
    e_nameline.appendChild(e_icon);

    // insert name line in dir element
    e_direlt.appendChild(e_nameline);

    // create div for directory content
    e_dircontent=document.createElement('div');
    e_dircontent.setAttribute('style','display:none');
    e_dircontent.setAttribute('id',"subdir_"+node.id);
    e_direlt.appendChild(e_dircontent);
    e_dircontent2=document.createElement('div');
    e_dircontent2.setAttribute('id',"subdir_content_"+node.id);
    e_dircontent.appendChild(e_dircontent2);

    // create ul for directory items
    var e_dirlist=document.createElement('ul');
    e_dirlist.setAttribute('class','directorylisting');
    e_dircontent2.appendChild(e_dirlist);
    node.container=e_dirlist;

    // particular case when node is the root node
    // immediatly insert it in the browser rootdir
    // otherwise behaviors won't works

    if (node.id==this.id+'_root')
    this.rootdir.appendChild(node.domnode);
}

kolekti_browser.prototype.display_error= function(id) {
    var icon=document.getElementById('loading_error'+id);
    if (icon) {
    icon.style.display='inline';
    }
}

kolekti_browser.prototype.show_loading= function(id) {
    var icon=document.getElementById('loading_'+id);
    if (icon) {
    icon.style.display='inline';
    }
}

kolekti_browser.prototype.hide_loading= function(id) {
    var icon=document.getElementById('loading_'+id);
    if (icon) {
    icon.style.display='none';
    }
}

// expand a directory in the dom
kolekti_browser.prototype.expand_node= function(node) {
    //node.is_collapsed=false;

    // show the content
    node.container.parentNode.parentNode.style.display='block';
    
    // show the hiding button
    var picto=document.getElementById("hide_"+node.id);
    if (picto)
    picto.style.display="inline";

    // hide the showing button
    picto=document.getElementById("show_"+node.id);
    if (picto)
    picto.style.display="none";
}

// collapse a directory in the dom
kolekti_browser.prototype.collapse_node= function(node) {
    //node.is_collapsed=true;

    // hide the content
    node.container.parentNode.parentNode.style.display='none';

    // hide the hiding button
    var picto=document.getElementById("hide_"+node.id);
    if (picto)
    picto.style.display="none";

    // show the showing button
    picto=document.getElementById("show_"+node.id);
    if (picto)
    picto.style.display="inline";
}

kolekti_browser.prototype.basc_dir= function(node) {
    if (node.is_collapsed) {
    this.expand_node(node);    
    node.expand();
    node.request();
    } else {
    this.collapse_node(node);
    node.collapse();
    }
};

kolekti_browser.prototype.collapse_dir= function(e) {
    var node=this.get_browser_node(e.currentTarget);
    if (node) {
    this.collapse_node(node);
    node.collapse();
    }
};

kolekti_browser.prototype.expand_dir= function(e) {
    var node=this.get_browser_node(e.currentTarget);
    if (node) {
    this.expand_node(node);
    node.expand();
    node.request();
    }
};

kolekti_browser.prototype.attach_tab_behavior = function(elt,xpr,url) {
    var pp,act,action,actspan,button,bhv;
    var done=false;
    xpr.nextResponse();
    pp=xpr.get_prop('kolekti:browser','mainbrowseractions');

    if(pp.status=="200") {
        actspan=elt.firstChild;
        act=pp.content.firstChild;
        while (act) {
        action=act.getAttribute('id');
        if (this.actions[action]) {
        button=this.create_action_button(this.actions[action]);
        this.set_kolekti_params(button, xpr, url);
        actspan.appendChild(button,actspan.firstChild);
        done=true;
        }
        act=act.nextSibling;
    }
    }

    pp=xpr.get_prop('kolekti:browser','browserbehavior');
    if(pp.status=="200") {
        elt.firstChild.style.cursor="pointer";
        bhv=pp.content.firstChild;
        while (bhv) {
        if (this.behaviors[bhv.getAttribute('id')]) {
        this.set_behavior_deffered(bhv.getAttribute('id'),elt.firstChild);
        done=true;
        }
        bhv=bhv.nextSibling;
        }
    }
    return done;
}

kolekti_browser.prototype.attach_file_behavior = function(node,props) {
    var i = 1;
    var pp,act,action,actspan,button,bhv;
    var elt=node.domnode;
    pp=props.firstChild;
    while (pp) {
    if (pp.localName=="browseractions" && pp.namespaceURI=="kolekti:browser") {
        actspan=document.createElement('span');
        act=pp.firstChild;
        while (act) {
        action=act.getAttribute('id');
        if (this.actions[action]) {
            button=this.create_action_button(this.actions[action]);
            button.kolekti.url=node.url;
            button.className += " action"+i;
            actspan.appendChild(button,actspan.firstChild);
            i++;
        }
        act=act.nextSibling;
        }
        elt.insertBefore(actspan,elt.firstChild);
    }

    if (pp.localName=="browserbehavior" && pp.namespaceURI=="kolekti:browser") {
        elt.style.cursor="pointer";
        bhv=pp.firstChild;
        while (bhv) {
        if (this.behaviors[bhv.getAttribute('id')]) {
            this.set_behavior(node,bhv.getAttribute('id'),elt);
        }
        bhv=bhv.nextSibling;
        }
        
    }
    pp=pp.nextSibling;
    }
}

kolekti_browser.prototype.attach_dir_behavior = function(node,props) {
    var i = 1;
    var pp,act,action,actspan,button,bhv,elt;
    var behaviorclick=false;
    var eltd=node.domnode;
    var eltp=eltd.firstChild
    while (eltp && eltp.nodeType!=1) eltp=eltp.nextSibling;
    if (eltp) {
    elt=eltp.firstChild
    while (elt && (elt.nodeType!=1 || elt.nodeName.toLowerCase()!='span')) elt=elt.nextSibling;
    if (elt) {
        pp=props.firstChild;
        while (pp) {
        if ((pp.localName=="browseractions" || pp.localName=="rootdirbrowseractions") && pp.namespaceURI=="kolekti:browser") {
            actspan=document.createElement('span');
            act=pp.firstChild;
            while (act) {
            action=act.getAttribute('id');
            if (this.actions[action]) {
                button=this.create_action_button(this.actions[action]);
                button.kolekti.url=node.url;
                button.className += " action"+i;
                actspan.appendChild(button,actspan.firstChild);
                i++;
            }
            act=act.nextSibling;
            }
            eltp.insertBefore(actspan,eltp.firstChild);
        }

        if (pp.localName=="browserbehavior" && pp.namespaceURI=="kolekti:browser") {
            elt.style.cursor="pointer";
            bhv=pp.firstChild;
            while (bhv) {
            if (this.behaviors[bhv.getAttribute('id')]) {
                elt.setAttribute('id','item_'+node.id);
                if (this.behaviors[bhv.getAttribute('id')].type=="click" || this.behaviors[bhv.getAttribute('id')].type=="drag" )
                behaviorclick=true;
                this.set_behavior(node,bhv.getAttribute('id'),elt);
            }
            bhv=bhv.nextSibling;
            }
        }
        pp=pp.nextSibling;
        }

        if (!behaviorclick) {
        var me=this;
        elt.addEventListener('click',function(e){me.basc_dir(node)},false);
        }
    }
    }
}

// Fixed default values of kolekti object
kolekti_browser.prototype.set_kolekti_params = function(elem, xpr ,url) {
    elem.kolekti.url=url;
    //get the resid
    p=xpr.get_prop('kolekti','resid');
    if (p.status=="200")
    elem.kolekti.resid=p.content.firstChild.nodeValue;
    // get the urlid
    p=xpr.get_prop('kolekti','resourceid');
    if (p.status=="200")
    elem.kolekti.urlid=p.content.firstChild.nodeValue;
}

kolekti_browser.prototype.add_properties = function(elt,uri,props) { }

// register a behavior on a node for later (when the node will be present in the dom structure)
kolekti_browser.prototype.set_behavior = function(node,bhv,elt) {
    if (!node.deffered_behaviors)
    node.deffered_behaviors=[];
    node.deffered_behaviors.push({bhv:bhv,elt:elt});
}

// deffered behavior association to dom nodes
// should be called when the node.domnode actually is in the document tree
kolekti_browser.prototype.set_behaviors = function(node) {
    var i;
    for (i in node.deffered_behaviors) {
    this.set_behavior_deffered(node.deffered_behaviors[i].bhv,node.deffered_behaviors[i].elt);
    }
    node.deffered_behaviors=null;
}

// associates the behavior to the dom nodeOA
kolekti_browser.prototype.set_behavior_deffered = function(bhv,elt) {
    var b=this.behaviors[bhv];
    var action,event;
    var me=this;
    // if the object is draggable
    if (b.type=="drag") {
    var dragprops={
        helper:'clone', 
        refreshPositions: true, 
        opacity: 0.8,
        revert: 'invalid',
        appendTo: 'body'
    };
    jQuery(function() {
        $("#"+elt.getAttribute('id')).draggable(dragprops);
    })

    } else {
    if (b.action=="notify") {
        action=function(e){me.notify_event(e,b.event,b.context)};
    }
    if (b.action=="select") {
        action=function(e){me.click_select_file(e)};
    }
    if (b.action=="action") {
        action=function(e){me.browseraction(e)};
    }
    
    elt.addEventListener(b.type,action,false);
    }
}

kolekti_browser.prototype.create_action_button = function(action) {
    var eltact=document.createElement('span');
    eltact.className="browseritemaction";
    if (action['icon']) {
    iconact=document.createElement('img');
    iconact.setAttribute('src',action['icon']);
    iconact.setAttribute('alt',action['name']);
    iconact.setAttribute('title',action['name']);
    eltact.appendChild(iconact);
    } else {
    textact=document.createTextNode(action['name']);
    eltact.appendChild(textact);
    }
    if (action['shortname']) {
        snameact=document.createElement('span');
        snameact.className="viewershortnameaction";
        snameact.textContent = '['+action['shortname']+']';
        eltact.appendChild(snameact);
    }
    eltact.kolekti=new Object();
    eltact.kolekti.browseraction=action.id;

    var me=this;
    eltact.addEventListener('click',function(e){me.browseraction(e)},false);
    eltact.style.cursor="pointer";
    return eltact;
}

/* Behavior manager */

// Behavior callbacks

kolekti_browser.prototype.display_file= function(e,viewer) {
    e.stopPropagation();
    var node=this.get_browser_node(e.currentTarget)
    viewer.displayresource(node.url);
};

kolekti_browser.prototype.display_dir= function(e,viewer) {
    e.stopPropagation();
    var node=this.get_browser_node(e.currentTarget)
    viewer.displayresource(node.url);
};

kolekti_browser.prototype.notify_event= function(e,event,context) {
    e.stopPropagation();
    var arg=new Object();
    var node=this.get_browser_node(e.currentTarget)

    arg['url']=node.url;
    arg['urlid']=node.id;
    arg['resid']=node.resid;
    
    if (context)
    kolekti.notify(event,arg,context);
    else
    kolekti.notify(event,arg);
};

kolekti_browser.prototype.click_select_file= function(e) {
    e.stopPropagation();
    var node=this.get_browser_node(e.currentTarget)
    if(e.ctrlKey) {
    if (this.selection.is_selected(e.target.parentNode)) {
        this.selection.remove_selection(e.target.parentNode);
    } else {
        this.selection.add_selection(e.target.parentNode);
    }
    } else {
    this.selection.set_selection(e.target.parentNode);
    }
}

kolekti_browser.prototype.browseraction = function(e) {
    e.stopPropagation();
    var action=e.currentTarget.kolekti.browseraction;
    var arg=new Object();
    var curelem = e.currentTarget;
    while(curelem && curelem.nodeName != "LI")
        curelem = curelem.parentNode;
    if(!curelem)
        curelem = e.currentTarget;
    var node=this.get_browser_node(curelem);
    arg['url']=node.url;
    arg['urlid']=node.id;
    arg['resid']=node.resid;

    kolekti.actions[action].set_url(node.url);
    kolekti.actions[action].do_action(arg);

};

// end of kolekti browser class


// Selection management

kolekti_browser_selection= function() {
    this.selected_items=new Array();
    this.keep_active_items=true;
}

kolekti_browser_selection.prototype.set_selection= function(elt) {
    for(var i in this.selected_items) {
        old=this.selected_items[i];
        if(this.keep_active_items)
            old.style.backgroundColor="#D0E09D";
        else
            old.style.backgroundColor="";
        old.kolekti_selected=false;
    }
    
    if(!this.keep_active_items)
        this.selected_items=new Array();
    this.add_selection(elt);
}

kolekti_browser_selection.prototype.is_selected= function(elt) {
    return elt.kolekti_selected;
}

kolekti_browser_selection.prototype.add_selection= function(elt) {
    var i;
    if(elt.kolekti_selected_index && this.selected_items[elt.kolekti_selected_index])
        i = elt.kolekti_selected_index;
    else
        i = this.selected_items.push(elt);
    elt.style.backgroundColor="#8BBB60";
    elt.kolekti_selected=true;
    elt.kolekti_selected_index=i;
    this.lastselected=elt;
}

kolekti_browser_selection.prototype.remove_selection= function(elt) {
    if (!elt.kolekti_selected==true) return;
    this.selected_items=new Array();
    for(var i=0; i<this.selected_items.length; i++) {
        if(this.selected_items[i] != elt)
            this.selected_items.push(this.selected_items[i]);
        }
    elt.style.backgroundColor="";
    elt.kolekti_selected=false;
}
