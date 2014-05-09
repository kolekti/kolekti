function publicationprofileseditor() {
}

publicationprofileseditor.prototype=new kolekti_editor;

// Load resource
publicationprofileseditor.prototype.fetch_resource = function() {
    var c=new ajax(this.url);
    c.setParameter("viewer",this.viewname);
    c.setHeader('KolektiContext','publicationprofileseditor');
    var content=c.syncget();

    var div = document.createElement('div');
    div.innerHTML=content.text;
    this.content.appendChild(div);

    this.init_notify();
}

//Make notification change for each input
publicationprofileseditor.prototype.init_notify = function() {
   var inputs = this.content.getElementsByTagName('input');
   for(var i=0; i<inputs.length; i++) {
      var inp = inputs[i];
      if(inp.type == "text")
         this.change_input(inp, 'keyup');
      else if(inp.type == "checkbox")
         this.change_input(inp, 'change');
   }

   var select = this.content.getElementsByTagName('select');
   for(var i=0; i<select.length; i++) {
      var s = select[i];
      if(s.name != "script")
         this.change_input(s, 'change');
   }
}

//Set event type to notify changed
publicationprofileseditor.prototype.change_input = function(input, type) {
   var me = this;
   this.init_input(input);
   input.addEventListener(type,function(e){kolekti.notify('editor-resourcemodified',null,me.context.id);},false);
}

//Init input with param
publicationprofileseditor.prototype.init_input = function(input) {
   if(input.name == "enabled") {
      var me = this;
      var fv = $(input.parentNode.parentNode).find(".formvalue");
      if(fv.length > 0) {
         this.display_criteria_values(input, fv[0]);
         input.addEventListener('change',function(e){me.display_criteria_values(input, fv[0])},false);
      }
   }
}

//Show/Hide values of criteria
publicationprofileseditor.prototype.display_criteria_values = function(input, fv) {
 if(input.checked)
     fv.style.display = "inline";
 else
     fv.style.display = "none";
}

// Send data after save action
publicationprofileseditor.prototype.send_data=function() {
   if(this.verify_data()) {
       var d=this.get_data();
       var conn=new ajaxdav(this.url);
       var res=conn.PUT(d);
       return res.status == 200;
   }

   confirm(i18n("[0319]Echec lors de la sauvegarde."));
   return false;
}

publicationprofileseditor.prototype.verify_data=function() {
    return true;
}

// Generate xml file before save
publicationprofileseditor.prototype.get_data=function() {
   var val, code, min, max;
   var xmlbuf = '<publicationprofile>';
   var label = $(this.content).find("input[name='label']")[0];
   xmlbuf += '<label>'+label.value+'</label>';
   xmlbuf += "<criterias>";
   var criterias = $(this.content).find(".criteria span.formvalue");
   for(var j=0; j<criterias.length; j++) {
       var crit = criterias[j];
       var values = crit.getElementsByTagName("select");
       var checked = $(crit.parentNode).find("input[name='enabled']")[0].checked? 1 : 0;
       // enum criteria
       if(values.length == 1) {
           val = values[0].options[values[0].selectedIndex].value;
           code = values[0].name;
       } else {
           values = crit.getElementsByTagName("input");
           val = values[0].value;
           code = values[0].name;
       }

       xmlbuf += '<criteria checked="'+checked+'" code="'+code+'" value="'+val+'" />';
   }
   xmlbuf += '</criterias>';
   xmlbuf += '</publicationprofile>';

   return xmlbuf;
}
