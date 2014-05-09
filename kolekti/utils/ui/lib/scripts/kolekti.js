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
   Class for the kolekti object
*/
//author Stéphane Bonhomme <stephane@exselt.com>

function kolekti_obj() {
    this.listeners=new Object();
    this.actions=new Array();
    this.browsers=new Array();
    this.guiders=new Array();
    this.showguiders=true;
}

// translate urls from @ resource id
kolekti_obj.prototype.get_url=function(resid){
    if (resid.charAt(0)=='@') {
	return '/projects/'+this.project+'/'+resid.substring(1);
    } else {
	return resid;
    }
}

// load home page of project name
kolekti_obj.prototype.project_change=function(prjname) {
	window.location = '/projects/'+prjname;
}

// ajax call to set the work language (DEPRECATED)

kolekti_obj.prototype.worklanguage=function(lang){
    var conn=new ajax('/set/worklang?data='+lang);
    conn.header('KolektiContext','profile');
    var res=conn.get();
    window.location.reload();
}

// event notifier : objects may call this method to trigger an event
// event : name of the event to be triggered
// arg   : objet passed to all listeners 
// context : if 'ALL' : all listeners are notified of this event
//           else only listeners that have registered a context equal to this parameter are notified


kolekti_obj.prototype.notify=function(event,arg,context){
    var res=true;
    var l;
    //console.log("event "+event+" ctxt "+context);
    //console.log(arg);
    for (var o in this.listeners[event]) {
	l=this.listeners[event][o];
	if (context=="ALL" || l.context==context) {
	    res=res && l.callable(arg);
	}
    }
    return res;
}


// event listener : objects may call this method to be notified when an event is triggered
// event    : name of the event to listen
// callback : function to be called when the event is triggered
// context  : only listen for events that are triggered with this context value
 
kolekti_obj.prototype.listen=function(event,callback,context) {
    var Lobj={'context':context,"callable":callback};
    if (!this.listeners[event]) {
	this.listeners[event]=new Array();
    }
    if(!this.event_exist(event,context))
    	this.listeners[event].push(Lobj);
}

// removes all event listeners that relies on the context

kolekti_obj.prototype.unlisten=function(context) {
    var e,l;
    for (e in  this.listeners) {
	for (l in this.listeners[e])
	    if (this.listeners[e][l].context==context) {
		this.listeners[e].splice(l,1);
	    }
    }
}

kolekti_obj.prototype.event_exist=function(event,context) {
	var tabevent = this.listeners[event];
	for(var i=0; i<tabevent.length; i++) {
		if(tabevent[i].context == context)
			return true;
	}
	return false;
}

// triggers a resize event

kolekti_obj.prototype.resize=function(e) {
    this.notify('resize',null,"ALL");
}

// triggers a quit-page event

kolekti_obj.prototype.close_page=function(e) {
    if (!this.notify('quit-page',null,"ALL")){
	e.preventDefault();
    }
}

// convenience function to handle shrink of shrinkable div

kolekti_obj.prototype.shrink=function() {
    var sh=document.getElementById("shrinkablehandle");
    var state=sh.className;
    var so=document.getElementById("shrinkable");
    var ssp=document.getElementById("shrinkablespacer");
    if (state=="shrinked") {
	so.style.display="block";
	ssp.style.width=this.shrinksize;
	sh.className="";
	ssp.style.left="";
    } else {
	this.shrinksize=ssp.style.width;
	ssp.style.width="auto";
	ssp.style.left="15px";
	so.style.display="none";
	sh.className="shrinked";
    }

}


// convenience functions to show/hide elements
// in logs
kolekti_obj.prototype.log_sect=function(id) {
	if((document.getElementById("logsect"+id).style.display=="block")) {
		document.getElementById("logsect"+id).style.display="none";
		document.getElementById("img"+id).setAttribute('src', '/_lib/icons/plus.png');
		document.getElementById("img"+id).setAttribute('alt', '[+]');
	}
	else {
		document.getElementById("logsect"+id).style.display="block";
		document.getElementById("img"+id).setAttribute('src', '/_lib/icons/moins.png');
		document.getElementById("img"+id).setAttribute('alt', '[-]');
	}
}

// generic section 
kolekti_obj.prototype.show_hide=function(id) {
	if(document.getElementById("section"+id).getAttribute("class")=="section_show")
		document.getElementById("section"+id).setAttribute("class", "section_hide");
	else
		document.getElementById("section"+id).setAttribute("class", "section_show");
}


kolekti_obj.prototype.parse_info_props=function(e) {
    var res=new Object();
    var c=e.firstChild;
    while (c) {
	if (c.nodeType==1) {
	    if (c.localName=='owner') {
		res.owner={userclass:c.getAttribute('class'),username:c.getAttribute('name')};
	    }
	    if (c.localName=='title') {
		res.title=c.textContent;
	    }
	    if (c.localName=='ref') {
		res.ref={udir:c.getAttribute('udir'),name:c.getAttribute('name')};
	    }
	}
	c=c.nextSibling;
    }
    return res;
}

kolekti_obj.prototype.toggle_guiders=function () {
    this.showguiders=!this.showguiders;
}

kolekti_obj.prototype.create_guider=function (id,selector,content,title,position) {
	guider.createGuider({attachTo: selector,
						 buttons: [],
						 description: content,
						 id: id,
						 overlay: false,
						 title: title,
						 position: position});
	this.add_guider(id, selector);
}

kolekti_obj.prototype.add_guider=function (id,selector) {
	this.guiders[id] ={id:id,selector:selector};
}

kolekti_obj.prototype.update_guiders=function (rootelt) {
    var selector, g, id;
    
    for (g in this.guiders) {
	selector=this.guiders[g].selector;
	id=this.guiders[g].id;
	$(rootelt).find(selector).bind('mouseenter',{guid:id}, function(event) {
	    if (kolekti.showguiders) {
		guider.get(id).attachTo=$(this);
		$.doTimeout('guider',200,function(){
		    guider.show(event.data.guid);
		})
	    }
	});
	$(rootelt).find(selector).bind('mouseleave', function(){
	    if (kolekti.showguiders) {
		$.doTimeout('guider');
		guider.hideAll();
	    }
	});
    }
}

kolekti_obj.prototype.remove_guiders=function (guidersid) {
	var g;
	for(var gid in guidersid) {
		try {
			g = guider.get(guidersid[gid]);
			for(var i=0; i<g.elem.length; i++)
				g.elem[i].parentNode.removeChild(g.elem[i]);	
			delete this.guiders[guidersid[gid]];
		} catch(err) {}
	}
}

// instanciate a kolekti object
window.kolekti=new kolekti_obj();

//trigger some events when the user closes/resizes the window
addEventListener('beforeunload',function(e){kolekti.close_page(e);},true);
addEventListener('resize',function(e){kolekti.resize(e);},true);


function kolektiNsResolver(prefix) {  
    var ns = {  
	'd' : 'DAV:',
	'ku': 'kolekti:users',  
	'kv': 'kolekti:viewer',  
	'kb': 'kolekti:browser',  
	'km': 'kolekti:modules',  
	'comes': 'kolekti:comes',  
	'k' : 'kolekti'  
    };  
    return ns[prefix] || null;  
}  


// XML writer with attributes and smart attribute quote escaping 

function xmlcontent(text) {
    var xml=text;
    xml=xml.replace(/</g, '&lt;');
    xml=xml.replace(/>/g, '&gt;');
    xml=xml.replace(/&/g, '&amp;');
    xml=xml.replace(/'/g, '&apos;');
    xml=xml.replace(/"/g, '&quot;');
    return xml;
}

function xmlattr(text) {
   var xml=text;
   xml=xml.replace(/'/g, '&apos;');
   return xml;
}	


CKEDITOR_BASEPATH = "/_lib/kolekti/scripts/ckeditor/";
