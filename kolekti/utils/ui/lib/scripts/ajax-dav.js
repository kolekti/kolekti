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
   Class for handling DAV requests over ajax
*/
//author Stéphane Bonhomme <stephane@exselt.com>


// class definition, inits with an URL

function ajaxdav(url) {
    if(url == '')
      return new Object();
    this.req=new XMLHttpRequest();
    this.baseurl=url;
    this.qs='';
    this.content='';
    this.callback=[];
    this.headers={'Dav':'1,2'};
    this.data=null;
    if (!ajaxdav.prototype.options) {
      ajaxdav.prototype.options=new Object();
      var optr=new ajax('/');
      optr.setHeader("Dav","1,2");
      optr.send('OPTIONS');
      var rh=optr.getResponseHeader('Allow');
      if (rh!=null) {
        var opts=rh.replace(/ /g,'').split(',')
        for (o in opts) {
        ajaxdav.prototype.options[opts[o]]=true;
        }
    }
    }
}

ajaxdav.prototype= new ajax();
ajaxdav.prototype.constructor=ajaxdav;

// makes a PROPFIND call to the server
ajaxdav.prototype.PROPFIND= function(properties,depth) {
    var prop,cprop;
    if (!this.options['PROPFIND']) return null;
    var body='<D:propfind xmlns:D="DAV:"><D:prop>';
    for (prop in properties) {
    cprop=properties[prop];
    if (cprop.ns=="DAV:") 
        body=body+'<D:'+cprop.propname+'/>';
    else
        body=body+'<'+cprop.propname+' xmlns="'+cprop.ns+'"/>';
    }
    body=body+'</D:prop></D:propfind>';
    this.setContent(body);
    if (typeof depth !="undefined")
    this.setHeader('Depth',depth);
    var res = this.send('PROPFIND');
    if(res)
        return {result: res, object:new dav_get_props(res.xml)};
    else
        return {result: res};
}

// makes a PROPPATCH call to the server
ajaxdav.prototype.PROPPATCH= function(setproperties,delproperties) {
    var prop,cprop;
    if (!this.options['PROPPATCH']) return null;
    var body='<D:propertyupdate xmlns:D="DAV:">';
    if (setproperties && setproperties.length) {
    body=body+'<D:set><D:prop>';
    for (prop in setproperties) {
        cprop=setproperties[prop];
        if (cprop.ns=="DAV:") 
        body=body+'<D:'+cprop.propname+'>';
        else
        body=body+'<'+cprop.propname+' xmlns="'+cprop.ns+'">';
        
        switch(typeof cprop.propval) {
        case 'boolean':
        body=body+(cprop.propval?"1":"0");
        break;
        case 'number':
        case 'string':
        body=body+cprop.propval;
        break;
        default:
        body=body+cprop.propval.tostring();
        break;
        }

        if (cprop.ns=="DAV:") 
        body=body+'</D:'+cprop.propname+'>';
        else
        body=body+'</'+cprop.propname+'>';
    }
    body=body+'</D:prop></D:set>';
    }
    if (delproperties && delproperties.length) {
    body=body+'<D:remove><D:prop>';
    for (prop in delproperties) {
        cprop=delproperties[prop];
        if (cprop.ns=="DAV:") 
        body=body+'<D:'+cprop.propname+'/>';
        else
        body=body+'<'+cprop.propname+' xmlns="'+cprop.ns+'"/>';
    }
    body=body+'</D:prop></D:remove>';
    }

    body=body+'</D:propertyupdate>';
    this.setContent(body);
    return this.send('PROPPATCH');
}

ajaxdav.prototype.LOCK = function(ownerid) {
    this.getlock();
    var body='<D:lockinfo xmlns:D="DAV:">';
    body=body+'<D:lockscope><D:exclusive/></D:lockscope> ';
    body=body+'<D:locktype><D:write/></D:locktype>'; 
    body=body+'<D:owner>';
    body=body+ownerid;
    body=body+'</D:owner>';
    body=body+'</D:lockinfo>';

    this.setContent(body);
    return this.send('LOCK');
}

ajaxdav.prototype.UNLOCK = function() {
    this.getlock();
    return this.send('UNLOCK');
}

ajaxdav.prototype.MOVE = function() {
    this.getlock();
    return this.send('MOVE');
}

ajaxdav.prototype.COPY = function() {
    this.getlock();
    return this.send('COPY');
}

ajaxdav.prototype.DELETE = function() {
    this.getlock();
    return this.send('DELETE');
}

ajaxdav.prototype.PUT = function(data) {
    this.getlock();
    this.setContent(data);
    return this.send('PUT');
}

ajaxdav.prototype.MKCOL = function() {
    this.getlock();
    return this.send('MKCOL');
}

ajaxdav.prototype.getlock = function() {
    if (!this.options.LOCK)
        return
    var p, token;
    var lp=this.PROPFIND([{ns:'DAV:',propname:'lockdiscovery'}]);
    var xpr = lp.result.xml.evaluate('/d:multistatus/d:response/d:propstat[starts-with(d:status,"HTTP/1.1 200")]/d:prop/d:lockdiscovery/d:activelock', lp.result.xml, kolektiNsResolver, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
    var actlock = xpr.singleNodeValue;
    if(actlock) {
        var child = actlock.firstChild;
        while(child) {
            if(child.nodeType == 1 && child.namespaceURI == 'DAV:' && child.localName == 'timeout') {
                this.setHeader("Timeout", "Second-"+child.textContent);
            } else if(child.nodeType == 1 && child.namespaceURI == 'DAV:' && child.localName == 'locktoken') {
                this.setHeader("If", '<'+child.firstChild.textContent+'>');
                token = child.firstChild.textContent.split(':')[1];
                this.setHeader("Lock-Token", token);
            }
            child = child.nextSibling;
        }
    }
    this.setContent('');
}

    ajaxdav.prototype.applyCallback=function(method, request, func) {
    var req;
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

    if(res.state==4 && method=='PROPFIND') 
        req = {result: res, object:new dav_get_props(res.xml)}
    else
        req = res;
    func(req,this.data);
}

//class for props parsing 
function dav_get_props(props) {
  this.props=props;
  this.resp=null;
}

dav_get_props.prototype.nextResponse = function() {
  if (this.resp==null) {
    var e_ms=this.props.documentElement;
    this.resp=e_ms.firstChild;
  } else {
    this.resp=this.resp.nextSibling;
  }
  while (this.resp && !this._okresp()) {
    this.resp=this.resp.nextSibling;
  }
  return this.resp;
}

dav_get_props.prototype._okresp= function() {
  if (this.resp.nodeType != 1)
    return false;
  if (this.resp.namespaceURI != 'DAV:')
    return false;
  if (this.resp.localName != 'response')
    return false;
  return true;
}

dav_get_props.prototype.get_url = function() {
  var e_href=this.resp.firstChild;
  while (e_href && e_href.nodeType != 1 && e_href.namespaceURI != 'DAV:' && e_href.localName != 'href') {
        e_href=e_href.nextSibling;
  }
  if (e_href) {
    return e_href.textContent;
  }
  return null;
}

dav_get_props.prototype.get_props = function(s) {
  var e_status,status;
  var e_prop;
  var e_propstat=this.resp.firstChild;
  while (e_propstat) {
    // loop on groups of propterties with same status
    if (e_propstat.nodeType != 1 || e_propstat.namespaceURI != 'DAV:' || e_propstat.localName != 'propstat') {
        e_propstat=e_propstat.nextSibling;
        continue;
    }

    // get status of the group
    e_status=e_propstat.firstChild;
    while(e_status && (e_status.nodeType != 1 || e_status.namespaceURI != 'DAV:' || e_status.localName != 'status'))
        e_status=e_status.nextSibling;
    if (e_status) {
        status=e_status.textContent.split(" ",2)[1];
    }
    if (status==s) {
        // get the properties
        e_prop=e_propstat.firstChild;
        while(e_prop && (e_prop.nodeType != 1 || e_prop.namespaceURI != 'DAV:' || e_prop.localName != 'prop'))
        e_prop=e_prop.nextSibling;
        return e_prop;
    }
    e_propstat=e_propstat.nextSibling;
  }
  return null;
}

dav_get_props.prototype.get_prop = function(ns,name) {
  var e_status,status;
  var e_prop,e_sprop;
  var e_propstat=this.resp.firstChild;
  while (e_propstat) {
    // loop on groups of propterties with same status
    if (e_propstat.nodeType != 1 || e_propstat.namespaceURI != 'DAV:' || e_propstat.localName != 'propstat') {
        e_propstat=e_propstat.nextSibling;
        continue;
    }

    // get status of the group
    e_status=e_propstat.firstChild;
    while(e_status && (e_status.nodeType != 1 || e_status.namespaceURI != 'DAV:' || e_status.localName != 'status'))
        e_status=e_status.nextSibling;
    if (e_status) {
        status=e_status.textContent.split(" ",2)[1];
    } else {
        // d:status not present in propstat
        return {status:'500',content:null};
    }
    // get the properties
    e_prop=e_propstat.firstChild;
    while(e_prop && (e_prop.nodeType != 1 || e_prop.namespaceURI != 'DAV:' || e_prop.localName != 'prop'))
        e_prop=e_prop.nextSibling;
    if (e_prop) {
        // loop on properties 
        e_sprop=e_prop.firstChild;
        while(e_sprop && (e_sprop.nodeType != 1 || e_sprop.namespaceURI != ns || e_sprop.localName != name)) {
        e_sprop=e_sprop.nextSibling;
        }
        if (e_sprop) 
        // found !
        return {status:status,content:e_sprop};
    } else {
        // d:prop not present in propstat
        return {status:'500',content:null};
    }
    e_propstat=e_propstat.nextSibling;
  }
  return {status:'404',content:null};
}
