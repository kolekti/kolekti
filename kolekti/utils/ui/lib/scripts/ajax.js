/*
 *    kOLEKTi : a structural documentation generator
 *    Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
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
   Class for ajax xmlhttprequests
*/
//author Stéphane Bonhomme <stephane@exselt.com>


/* Compilation conditionnelle d'IE */
/*@cc_on
@if (@_jscript_version >= 5) {

  var MS_XMLHTTP_PROGID = ["Msxml2.XMLHTTP.5.0", "Msxml2.XMLHTTP.4.0", "MSXML2.XMLHTTP.3.0", "MSXML2.XMLHTTP", "Microsoft.XMLHTTP"];
  var MS_XSLT_PROGID = ["Msxml2.XSLTemplate.5.0", "Msxml2.XSLTemplate.4.0", "MSXML2.XSLTemplate.3.0", " MSXML2.XSLTemplate"];
  var MS_THDOM_PROGID = ["Msxml2.FreeThreadedDOMDocument.5.0", "MSXML2.FreeThreadedDOMDocument.4.0", "MSXML2.FreeThreadedDOMDocument.3.0","MSXML2.FreeThreadedDOMDocument"];
  var MS_DOM_PROGID = ["Msxml2.DOMDocument.5.0", "Msxml2.DOMDocument.4.0", "Msxml2.DOMDocument.3.0", "MSXML2.DOMDocument", "MSXML.DOMDocument", "Microsoft.XmlDom"];

  function get_ms_implem(list) {
    var msimplem = false;
    for(var i=0; !msimplem && i < list.length; i++){
      try{
        msimplem = new ActiveXObject(list[i]);
      }
      catch (e) {
       msimplem = false;
      }
    }
    return msimplem;
  }

  function XMLSerializer(){};
  XMLSerializer.prototype.serializeToString = function(n) {
    return n.xml;
  }

  function XMLHttpRequest() {
    return get_ms_implem(MS_XMLHTTP_PROGID);
  }

  if (!window.Node) {
    var Node = {            // If there is no Node object, define one
        ELEMENT_NODE: 1,    // with the following properties and values.
        ATTRIBUTE_NODE: 2,  // Note that these are HTML node types only.
        TEXT_NODE: 3,       // For XML-specific nodes, you need to add
        COMMENT_NODE: 8,    // other constants here.
        DOCUMENT_NODE: 9,
        DOCUMENT_FRAGMENT_NODE: 11
    }
  }
}
@else
 var vacuum;
@end @*/


// ajax object
function ajax(url) {    
    if(url == '')
    	return new Object();
    this.req=new XMLHttpRequest();
    this.baseurl=url;
    this.qs='';
    this.content='';
    this.headers={};
    this.data=null;
    this.callback=[];
}

// sets the query string
// param str : the query string to be appendend to the url
//             ex : param1=value1&param2=value2
// Note : this will erase any query string and parameters set before

ajax.prototype.setQueryString=function(str) {
  this.qs=str;
}

// setHeader : sets an HTTP header 
// param name  : header name
// param value : header value

ajax.prototype.setHeader=function(name,value) {
  this.headers[name]=value;
}

// adds a parameter 
// param name  : name of the parameter
// param value : value of the parameter, may be a string or
//               an array of values, in this case, 
//               a list of couples name=value1&name=value2
// Note : this fonction url-encodes values
 
ajax.prototype.setParameter=function(name,value) {
    var firstv=true;
    if (this.qs!='')
	this.qs=this.qs+"&";
    if (typeof(value)=='string')
	this.qs=this.qs+name+"="+encodeURIComponent(value);
    else
	for (v in value) {
	    if (!firstv) {
		this.qs=this.qs+"&";
	    } else {
		firstv=false;
	    }
	    this.qs=this.qs+name+"="+encodeURIComponent(value[v]);
	}
}

// setContent : set the content to be sent to the server
// param str : the content.
ajax.prototype.setContent=function(str) {
  this.content=str;
}

// setCallback : sets the callback function
//               this causes the request to be send asyncronously
// param fun   : the function to be called when resquest is completed
// the prortype of the callback funtion is function(req,data), where
// req a response object  and the data set by the caller (see setData)

    ajax.prototype.setCallback=function(fun,state) {
	if (state==null) state=4;
	this.callback[state]=fun;
	
}

// sets data to be passed to the callback function
// param obj : the data to be passed as the second arg 
// to the callback function
ajax.prototype.setData=function(obj) {
  this.data=obj;
}

// send : makes the connexion to the server

ajax.prototype.send=function(method) {
    var url=this.baseurl;
    var async=Boolean(this.callback.length);
    if(method!="POST" && this.qs != "")
    	url+="?"+this.qs;
    this.req.open(method, url, async);
    if (method=="POST" && this.qs!='' && this.content==''){
	this.content=this.qs;
	this.req.setRequestHeader('content-type',"application/x-www-form-urlencoded");
    }
    for (h in this.headers) 
	this.req.setRequestHeader(h, this.headers[h]);
    if (async) {
	var me=this;
	this.req.onreadystatechange=function()
	{
	    if (typeof(me.callback[me.req.readyState]) == 'function')
            {
            	me.applyCallback(method, me.req, me.callback[me.req.readyState])
	    }
	}
	this.req.send(this.content);
    } else {
	// synchronous request
	this.req.send(this.content);
	var res=new Object();
	res.status=this.req.status;
	res.xml=this.req.responseXML;
	res.text=this.req.responseText;
	res.headers=this.req.getAllResponseHeaders();
	return res;
    }
}

    ajax.prototype.applyCallback=function(method, request, func) {
	var res=new Object();
	res.state=request.readyState;
	res.status=request.status;
	res.xml=request.responseXML;
	res.text=request.responseText;
	try {
	    res.headers=request.getAllResponseHeaders();
	}
	catch(e) {
	    res.headers=null;
	}
	func(res,this.data);
}

ajax.prototype.get=function() {
    this.send('GET');
}

ajax.prototype.post=function() {
    this.send('POST');
}

ajax.prototype.put=function() {
    this.send('PUT');
}

// methods that forces sync requests
ajax.prototype.syncsend=function(method) {
    this.callback=false;
    return this.send(method);
}

ajax.prototype.syncget=function() {
    this.callback=false;
    return this.send('GET');    
}

ajax.prototype.syncpost=function() {
    this.callback=false;
    return this.send('POST');
}

ajax.prototype.syncput=function() {
    this.callback=false;
    return this.send('PUT');
}


ajax.prototype.getResponseHeader=function(name) {
    if (this.req.readyState=='4') {
	return this.req.getResponseHeader(name);
    }
    return null;
}

ajax.prototype.syncpostXML=function() {
    var r=this.syncpost();
    return r.xml;
}

ajax.prototype.syncputXML=function() {
    var r=this.syncput();
    return r.xml;
}

ajax.prototype.syncgetXML=function() {
    var r=this.syncget();
    return r.xml;
}
 
ajax.prototype.auth=function(login,passw) {
    var url=this.baseurl;
    this.req.open("GET", url, false, login, passw);
    for (h in this.headers) 
      this.req.setRequestHeader(h, this.headers[h]);
    this.req.send(null);
    return this.req.status;
}
