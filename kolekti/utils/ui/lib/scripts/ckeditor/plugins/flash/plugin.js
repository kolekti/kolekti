﻿(function(){var a=/\.swf(?:$|\?)/i;function b(d){var e=d.attributes;return e.type=='application/x-shockwave-flash'||a.test(e.src||'');};function c(d,e){return d.createFakeParserElement(e,'cke_flash','flash',true);};CKEDITOR.plugins.add('flash',{init:function(d){d.addCommand('flash',new CKEDITOR.dialogCommand('flash'));d.ui.addButton('Flash',{label:d.lang.common.flash,command:'flash'});CKEDITOR.dialog.add('flash',this.path+'dialogs/flash.js');d.addCss('img.cke_flash{background-image: url('+CKEDITOR.getUrl(this.path+'images/placeholder.png')+');'+'background-position: center center;'+'background-repeat: no-repeat;'+'border: 1px solid #a9a9a9;'+'width: 80px;'+'height: 80px;'+'}');if(d.addMenuItems)d.addMenuItems({flash:{label:d.lang.flash.properties,command:'flash',group:'flash'}});d.on('doubleclick',function(e){var f=e.data.element;if(f.is('img')&&f.data('cke-real-element-type')=='flash')e.data.dialog='flash';});if(d.contextMenu)d.contextMenu.addListener(function(e,f){if(e&&e.is('img')&&!e.isReadOnly()&&e.data('cke-real-element-type')=='flash')return{flash:CKEDITOR.TRISTATE_OFF};});},afterInit:function(d){var e=d.dataProcessor,f=e&&e.dataFilter;if(f)f.addRules({elements:{'cke:object':function(g){var h=g.attributes,i=h.classid&&String(h.classid).toLowerCase();if(!i&&!b(g)){for(var j=0;j<g.children.length;j++){if(g.children[j].name=='cke:embed'){if(!b(g.children[j]))return null;return c(d,g);}}return null;}return c(d,g);},'cke:embed':function(g){if(!b(g))return null;return c(d,g);}}},5);},requires:['fakeobjects']});})();CKEDITOR.tools.extend(CKEDITOR.config,{flashEmbedTagOnly:false,flashAddEmbedTag:true,flashConvertOnEdit:false});
