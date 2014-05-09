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
   kolekti actions class 
   defines a user action with/wo dialog

*/

function kolekti_action(id) {
    this.id=id;
    this.hasdialog=false;
    this.dialogtype="action";
    this.selectors=new Array();
    this.ajaxregions=new Array();
    this.dialog_buttons=new Array();
    this.process=new Array();
    this.results=new Array();
    this.prname=new Array();
    this.browsers=new Array();
    this.attach_actions(id);

}

kolekti_action.prototype.attach_actions=function(id) {
    if (id) {
    var elt=document.getElementById("action_"+id);
    //    elt.kolekti=this;
    if (elt) {
        var c=elt.childNodes;
        for (var i=0;i<c.length;i++) {
        if (c.item(i).nodeType==1 && c.item(i).className=="label") {
            this.attach_action(c.item(i));
        }
        }
    }
    }
}

kolekti_action.prototype.init=function(me) {
    me.attach_actions(me.id);
}

kolekti_action.prototype.attach_action=function(elt) {
    var me=this;
    elt.addEventListener("click",function(e){me.action_init(e)},false);
    elt.style.cursor="pointer";
}

 
kolekti_action.prototype.addselector = function(id) {
    var obj=new Object();
    obj.id=id;
    this.selectors.push(obj);
    return obj;
}

kolekti_action.prototype.addajaxregion = function(id) {
    var obj=new Object();
    obj.id=id;
    this.ajaxregions.push(obj);
    return obj;
}

kolekti_action.prototype.adddialogbutton = function(label) {
    var obj=new kolekti_action_button(label);
    this.dialog_buttons.push(obj);
    return obj;
}


kolekti_action.prototype.addprocess = function(type) {
    var obj=new Object();
    obj.type=type;
    this.process.push(obj);
    return obj;
}

kolekti_action.prototype.addresult  = function(status,action) {
    var obj=new Object();
    obj.status=(status=="success"); 
    obj.action=action;
    this.results.push(obj);
    return obj;
}




/* call action */

kolekti_action.prototype.do_action= function(args) {
    if (this.hasdialog) {
    this.set_params_values(args);
    } else {
        if(!this.params)
            this.params=new Object();
        for(var a in args)
            this.params[a] = args[a];
    }
    this.action_init(null);
}

/* action handlers */

kolekti_action.prototype.action_init= function(e) {
    if (this.hasdialog) {
    this.action_dialog();
    } else {
    this.action_result(this.action_confirm(null));
    }
}


kolekti_action.prototype.set_context=function(ctxt) {
    var b,p,bt;
    // set for main action
    for (p in this.process) {
    b=this.process[p];
    if (b.with_context)
        b.context=ctxt;
    }
    for (p in this.results) {
    b=this.results[p];
    if (b.with_context)
        b.context=ctxt;
    }
    // set for actions associated to custon buttons
    for (bt in this.dialog_buttons) {
    for (p in this.dialog_buttons[bt].process) {
        b=this.dialog_buttons[bt].process[p];
        if (b.with_context)
        b.context=ctxt;
    }
    for (p in this.dialog_buttons[bt].results) {
        b=this.dialog_buttons[bt].results[p];
        if (b.with_context)
        b.context=ctxt;
    }
    }
}

kolekti_action.prototype.set_url=function(url) {
    if(url) {
        this.url = url;
        var b,p,bt;
        for (p in this.process) {
        b=this.process[p];
        if (b.type=='dav' || b.type=='http') {
            b.url=url;
        }
        if (b.type=='notify') {
            if (!b.params) b.params=new Object();
            b.params['url']=url;
        }
        }
    
        for (p in this.results) {
        b=this.results[p];
        if (b.action=='notify') {
            if (!b.params) b.params=new Object();
            b.params['url']=url;
        }
        }
        // set for actions associated to custon buttons
        for (bt in this.dialog_buttons) {
        for (p in this.dialog_buttons[bt].process) {
            b=this.dialog_buttons[bt].process[p];
            if (b.type=='dav' || b.type=='http') {
            b.url=url;
            }
            if (b.type =='notify') {
            if (!b.params) b.params=new Object();
            if (!b.params['url']) b.params['url']=url;
            }
        }
        for (p in this.dialog_buttons[bt].results) {
            b=this.dialog_buttons[bt].results[p];
            if (b.action =='notify') {
            if (!b.params) b.params=new Object();
            if (!b.params['url']) b.params['url']=url;
            }
        }
        }
        this.set_params_values({'url':url});
    }
}

kolekti_action.prototype.action_dialog= function() {
    var dlg="action_dialog_"+this.id;
    var buttons,but,b;
    var me=this;
    if (this.dialogtype=="confirm") {
        buttons=[{
                     text: i18n("[0304]Valider"),
                     click: function() {
                         me.sessionprofil('add');
                         me.action_result(me.action_confirm($(this)));
                     }
                 },
                 {
                     text: i18n("[0305]Annuler"),
                     click: function() {
                        me.action_cancel($(this));
                     }
                 }];
    } else {
    buttons=[{
                text: i18n("[0306]Fermer"),
                click: function() {
                    me.action_cancel($(this));
                }
            }];
    }
    for (b in this.dialog_buttons) {
        but=this.dialog_buttons[b];
        buttons[but.label] = function(b) {
        me.action_button($(this),b.target.textContent);
        }
    }

    this.init_browser_components();
    this.init_ajax_components();
    $('#'+dlg).dialog( {
    modal : true,
    open : function (event,ui) {kolekti.notify('dialog_open',me.id,me.objid);},
    autoOpen : true,
    resizable : false,
    width : 680,
    close: function (event,ui) {me.action_cancel($(this));},
    buttons : buttons
    });
    $('#'+dlg).unbind('keypress');
    $('#'+dlg).keypress(function(e) {
    if (e.which == 13) {
        me.action_result(me.action_confirm($(this)));
        e.cancelBubble=true;
    }
    })
}

kolekti_action.prototype.init_browser_components= function() {
    var b, browser;
    for (b in this.browsers) {
    browser=this.browsers[b];
    kolekti.browsers[browser].init_in_dialog();
    }
}

kolekti_action.prototype.init_ajax_components= function() {
    // ajax browsers
    this.ajax_browser();
    // ajax regions
    this.ajax_region();
}

kolekti_action.prototype.ajax_browser=function() {
    var i,item;  
    var me=this;
    for (i in this.selectors) {
    item=this.selectors[i];
    var dlgdiv=$('#'+this.id+'_'+item.id);
    var conn=new ajaxdav(item.url);
    var res=conn.PROPFIND([{'propname':item.property,'ns':item.nsproperty}],0);
    dlgdiv.empty();
    $(res.xml).find('option').each(function() {
        if((me.prname[item.id]) && (me.prname[item.id] == $(this).text()))
          dlgdiv.append('<option value="'+$(this).attr('value')+'" selected="selected">'+$(this).text()+'</option>');
        else
          dlgdiv.append('<option value="'+$(this).attr('value')+'">'+$(this).text()+'</option>');
    });
    }
}

kolekti_action.prototype.ajax_region=function() {
    var i,item,data;
    var me=this;
    
    for (i in this.ajaxregions) {
    item=this.ajaxregions[i];
    if (item.update) {
        $("#"+item.update).bind('change',function(e) {
        var j,data;
            for (j in me.ajaxregions) {
            data=me.ajaxregions[j];
            if(data.update == $(this).attr('id')) {
            me.prname[$(this).attr('name')] = $("#"+$(this).attr('id')+" option:selected").text();
            me.update_ajax_region(data);
            }
        }
        e.stopPropagation();
        return false;
        });
    }
    this.update_ajax_region(item);
    }
}

kolekti_action.prototype.update_ajax_region= function(item) {
    var par,hn,hv,pitem;
    this.get_params_values();
    var conn=new ajax(this.subst_params_values(item.url));
    for (hn in item.headers) {
    hv=item.headers[hn];
    conn.setHeader(hn,this.subst_params_values(hv));
    }
    for (par in this.params) {
        if (typeof(this.params[par]=='string')) {
            conn.setParameter(par,this.params[par]);
        } else {
            for (pitem in this.params[par]) {
                conn.setParameter(par,this.params[par][pitem]);
            }
        }
    }
    c=conn.syncget();
    
    var select = this.subst_params_values(item.url).split('/');
    select = select[select.length-1].split('.');
    $('input[name="save_'+this.id+'_'+item.id+'"]').attr("value", select[0]);
    document.getElementById(this.id+'_'+item.id).innerHTML=c;
    $("#"+this.id+'_'+item.id).css('display','block');
    this.post_update_ajax_region(item);

}

kolekti_action.prototype.post_update_ajax_region= function(item) {
    // override ethis method
}

kolekti_action.prototype.sessionprofil=function(method) {
    // override ethis method
}

kolekti_action.prototype.set_params_arg= function(args) {
    // get args param only for notify action
    // same for http, dav?
    for (p in this.results) {
        var b=this.results[p];
        if (b.action=='notify') {
            if (!b.params) b.params=new Object();
            for(param in args)
                b.params[param]=args[param];
        }
    }
}

kolekti_action.prototype.set_params_values= function(args) {
    this.set_params_arg(args);
    
    var input,i,fname;
    var dlg=document.getElementById("action_dialog_"+this.id);
    if (dlg) {
    var inputs=dlg.getElementsByTagName('INPUT');
    for (i=0; i< inputs.length;i++) {
        input=inputs[i];
        fname=input.getAttribute('name')
        if (args[fname]) {
            input.value=args[fname];
        }
    }
    inputs=dlg.getElementsByTagName('SELECT');
    for (i=0; i< inputs.length;i++) {
        input=inputs[i];
        fname=input.getAttribute('name')
        if (args[fname]) {
            input.value=args[fname];
        }
    }
    }
}

kolekti_action.prototype.get_params_values= function() {
    var input,i;
    this.params=new Object();
    var dlg=document.getElementById("action_dialog_"+this.id);
    var inputs=dlg.getElementsByTagName('INPUT');
    for (i=0; i< inputs.length;i++) {
    // tester si checkbox ou radio ou texte
    input=inputs[i];
    if (input.type=="checkbox"){
      if(input.checked) {
          if (this.params[input.getAttribute('name')]) 
          this.params[input.getAttribute('name')].push(input.value);
          else 
          this.params[input.getAttribute('name')]=new Array(input.value);
      }
    } else {
        this.params[input.getAttribute('name')]=input.value;
    }
    }
    inputs=dlg.getElementsByTagName('SELECT');
    for (i=0; i< inputs.length;i++) {
    input=inputs[i];
    if(input.value != "0")
      this.params[input.getAttribute('name')]=input.value;
    }
}

kolekti_action.prototype.subst_params_values= function(str) {
    var i,re;
    var s=str;
    if(typeof(str)=="string") {
        for (i in this.params) {
            re=new RegExp('\\\[\\\['+i+'\\\]\\\]','g');
            s=s.replace(re,this.params[i]);
        }
        s=s.replace("{{project}}",kolekti.project);
        s=s.replace("{{uid}}",kolekti.uid);
        try {
            var surl = this.url.split('/');
            s=s.replace("{{resource}}", surl[surl.length-1]);
        } catch(e) {}
    }
    return s;
}

kolekti_action.prototype.action_button= function(w,bl) {
    var p,proc;
    var success=true;
    var b,but;
    for (b in this.dialog_buttons) {
    but=this.dialog_buttons[b]; 
    if (but.label==bl)
        break;
    }

    this.status="";
    this.get_params_values();
    for (p in but.process) {
    proc=but.process[p];
    proc.result=null;
    success = success && this['process_'+proc.type](proc);
    }

    if (w!=null)
    w.dialog('destroy');
    this.action_result(success);

}

kolekti_action.prototype.action_confirm= function(w) {
    var p, proc;
    var success=true;
    this.status="";
    if (this.hasdialog) {
    this.get_params_values();
    }
    for (p in this.process) {
    proc=this.process[p];
    proc.result=null;
    success = success && this['process_'+proc.type](proc);
    }
    if (w!=null)
    w.dialog('destroy');
    return success;
}

kolekti_action.prototype.process_http= function(p) {
    var hn,hv,conn,url,par,pitem;
    url=p.url;
    if (p.defurl)
    url=this.subst_params_values(p.defurl);
    if (p.urlext)
    url+=this.subst_params_values(p.urlext);
    conn=new ajax(url);
    for (hn in p.headers) {
    hv=p.headers[hn];
    conn.setHeader(hn,this.subst_params_values(hv));
    }
    for (par in this.params) {
    //console.log(par+" - "+this.params[par]);
    if (typeof(this.params[par]=='string')) {
        conn.setParameter(par,this.params[par]);
    } else {
        for (pitem in this.params[par]) {
        conn.setParameter(par,this.params[par][pitem]);
        }
    }
    }
    p.result=conn.syncsend(p.method);
    this.status=this.status+"<div class='dlgstatus'>"+p.result.text+"</div>";
    return p.result.status==200;
}

kolekti_action.prototype.process_dav= function(p) {
    var hn,hv,conn,url;
    url=p.url;
    if (p.defurl)
    url=this.subst_params_values(p.defurl);
    if (p.urlext)
    url+=this.subst_params_values(p.urlext);
    conn=new ajaxdav(url);
    for (hn in p.headers) {
    hv=p.headers[hn];
    conn.setHeader(hn,this.subst_params_values(hv));
    }
    p.result=conn[p.method]();
    this.status=this.status+"<div class='dlgstatus'>"+p.result.text+"</div>";
    return (p.result.status==200 || p.result.status==201 || p.result.status==207);
}

kolekti_action.prototype.process_notify= function(p) {
    var params=new Object();
    var pp,r=true;
    for (pp in p.params) {
    params[pp]=this.subst_params_values(p.params[pp]);
    }
    for (pp in this.params) {
    params[pp]=this.subst_params_values(this.params[pp]);
    }
    if (p.with_context)
    r=kolekti.notify(p.event,params,p.context);
    else
    r=kolekti.notify(p.event,params,this.objid);
    return true;
}

kolekti_action.prototype.action_cancel= function(w) {
    w.dialog('destroy');
}

kolekti_action.prototype.action_result= function(status) {
    var r,result;
    for (r in this.results) {
    result=this.results[r];
    if ((status &&  result.status) || (!status &&  !result.status)) {
        this['result_'+result.action](result);
    }
    }
}

kolekti_action.prototype.result_notify= function(r) {
    var params=new Object();
    var pp,procid,p,proc;
    for (pp in r.params) {
        if(r.params[pp]) {
            if (r.params[pp].processresult) {
                procid=r.params[pp].processid;
                for (p in this.process) {
                    proc=this.process[p];
                    if (proc.id && proc.id==procid) {
                        params[pp]=proc.result;
                    }
                }
            } else {
                params[pp]=r.params[pp];
            }
        }
    }
    for (pp in this.params) {
    params[pp]=this.params[pp];
    }

    if (r.with_context)
    kolekti.notify(r.event,params,r.context);
    else
    kolekti.notify(r.event,params,this.objid);
}

kolekti_action.prototype.result_message= function(r) {
    this.result_status_or_message(r.status,false);
}

kolekti_action.prototype.result_status= function(r) {
    this.result_status_or_message(r.status,true);
}

kolekti_action.prototype.result_status_or_message= function(r,display) {
    var status;
    var me=this;
    if (r) status="success";
    else   status="error";
    var d="action_dialog_"+this.id+"_"+status;
    if (display)
    document.getElementById(d).innerHTML=this.status;
    $("#"+d).dialog( {
    modal : true,
    autoOpen : true,
    resizable : false,
    width : 600,
    buttons :{
        "Fermer" : function() {
            me.action_cancel($(this));
        }
    }
    })
    $("#"+d).keypress(function(e) {
    if (e.which == 13) {
        me.action_cancel($(this));
        e.cancelBubble=true;
    }
    })
}


// class for buttons in jquery dialogs

function kolekti_action_button(label) {
    this.label=label;
    this.process=new Array();
    this.results=new Array();
}

kolekti_action_button.prototype.addprocess = function(type) {
    var obj=new Object();
    obj.type=type;
    this.process.push(obj);
    return obj;
}

kolekti_action_button.prototype.addresult = function(status,action) {
    var obj=new Object();
    obj.status=(status=="success"); 
    obj.action=action;
    this.results.push(obj);
    return obj;
}
