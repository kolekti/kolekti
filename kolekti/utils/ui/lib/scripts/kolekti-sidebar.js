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
   Class for the kolekti sidebar component
*/
//author Stéphane Bonhomme <stephane@exselt.com>

function kolekti_sidebar(id, context) {
    this.id=id;
    this.context=context;
    this.properties = new Array();
    this.dom = null;
    this.section_state = new Object();
}

kolekti_sidebar.prototype.initevent= function() {
    var me=this;
    kolekti.listen('sidebar-refresh',function(arg){me.refresh(arg);return true;},this.id);
    kolekti.listen('sidebar-refresh-ui',function(arg){me.refresh_ui(arg);return true;},this.id);
}

kolekti_sidebar.prototype.refresh_ui=function(sidebar) {
    var refresh = false;
    for(var action in this.context.sidebar) {
        if(this.context.sidebar[action].section_open != this.section_state[action]) {
            refresh = true;
            this.section_state[action] = this.context.sidebar[action].section_open;
        }
    }
    if(refresh)
        this.refresh(sidebar);
}

kolekti_sidebar.prototype.refresh=function(sidebar) {
}

kolekti_sidebar.prototype.init_ui= function() {
    var d;

    if(!this.context.sidebar)
        this.context.sidebar = new Object();

    var div = this.dom.getElementsByTagName("div");
    for(var i=0; i<div.length; i++) {
        d = div[i];
        if(d.className=="sidebar_section" || d.className=="sidebar_section_hide")
            this.init_section(d);
    }
}

kolekti_sidebar.prototype.init_section= function(d) {
    var me = this;
    var elt = d.previousSibling.previousSibling;
    if(elt && elt.className == "sidebar_section_holder")
        return;

    var sp = document.createElement("span");
    sp.className = "sidebar_section_holder";

    var sp_show = document.createElement("span");
    sp_show.className="sidebar_section_show";
    var img = document.createElement("img");
    img.setAttribute("src", "/_lib/kolekti/icons/sidebar_section_show.png");
    img.setAttribute("alt", "V");
    sp_show.appendChild(img);
    sp.appendChild(sp_show);

    var sp_hide = document.createElement("span");
    sp_hide.className="sidebar_section_hide";
    img = document.createElement("img");
    img.setAttribute("src", "/_lib/kolekti/icons/sidebar_section_hide.png");
    img.setAttribute("alt", ">");
    sp_hide.appendChild(img);
    sp.appendChild(sp_hide);

    if(!this.context.sidebar[d.parentNode.className]) {
        this.context.sidebar[d.parentNode.className] = new Object();
        this.context.sidebar[d.parentNode.className].section_open = false;
        this.section_state[d.parentNode.className] = false;
    }

    d.parentNode.insertBefore(sp, d.previousSibling);

    d.previousSibling.addEventListener('click',function(e){me.change_section(sp_show, sp_hide, d);},false);
    sp.addEventListener('click',function(e){me.change_section(sp_show, sp_hide, d);},false);

    if(this.context.sidebar[d.parentNode.className].section_open) {
        sp_show.className = "sidebar_section_show";
        sp_hide.className = "sidebar_section_hide";
        d.className = "sidebar_section";
        this.section_state[d.parentNode.className] = true;
    } else {
        this.change_section(sp_show, sp_hide, d);
    }
}

kolekti_sidebar.prototype.change_section= function(sp_show, sp_hide, d) {
    if(d.className=="sidebar_section") {
        sp_show.className = "sidebar_section_hide";
        sp_hide.className = "sidebar_section_show";
        d.className = "sidebar_section_hide";
        this.context.sidebar[d.parentNode.className].section_open = false;
        this.section_state[d.parentNode.className] = false;
    } else {
        sp_show.className = "sidebar_section_show";
        sp_hide.className = "sidebar_section_hide";
        d.className = "sidebar_section";
        this.context.sidebar[d.parentNode.className].section_open = true;
        this.section_state[d.parentNode.className] = true;
    }
}

kolekti_sidebar.prototype.set_state=function() {
    var conn=new ajaxdav(this.url);
    conn.setHeader('KolektiContext','browser');
    conn.setHeader('KolektiBrowser',this.browser.id);
    conn.setCallback(function(req,data){});
    conn.PROPPATCH([{ns:'kolekti:usersession',propname:'dirstate',propval:(this.is_collapsed?'0':'1')}],[]);
}
