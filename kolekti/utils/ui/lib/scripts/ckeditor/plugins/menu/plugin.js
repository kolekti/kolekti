﻿CKEDITOR.plugins.add('menu',{beforeInit:function(a){var b=a.config.menu_groups.split(','),c=a._.menuGroups={},d=a._.menuItems={};for(var e=0;e<b.length;e++)c[b[e]]=e+1;a.addMenuGroup=function(f,g){c[f]=g||100;};a.addMenuItem=function(f,g){if(c[g.group])d[f]=new CKEDITOR.menuItem(this,f,g);};a.addMenuItems=function(f){for(var g in f)this.addMenuItem(g,f[g]);};a.getMenuItem=function(f){return d[f];};a.removeMenuItem=function(f){delete d[f];};},requires:['floatpanel']});(function(){CKEDITOR.menu=CKEDITOR.tools.createClass({$:function(b,c){var f=this;c=f._.definition=c||{};f.id=CKEDITOR.tools.getNextId();f.editor=b;f.items=[];f._.listeners=[];f._.level=c.level||1;var d=CKEDITOR.tools.extend({},c.panel,{css:b.skin.editor.css,level:f._.level-1,block:{}}),e=d.block.attributes=d.attributes||{};!e.role&&(e.role='menu');f._.panelDefinition=d;},_:{onShow:function(){var j=this;var b=j.editor.getSelection();if(CKEDITOR.env.ie)b&&b.lock();var c=b&&b.getStartElement(),d=j._.listeners,e=[];j.removeAll();for(var f=0;f<d.length;f++){var g=d[f](c,b);if(g)for(var h in g){var i=j.editor.getMenuItem(h);if(i&&(!i.command||j.editor.getCommand(i.command).state)){i.state=g[h];j.add(i);}}}},onClick:function(b){this.hide(false);if(b.onClick)b.onClick();else if(b.command)this.editor.execCommand(b.command);},onEscape:function(b){var c=this.parent;if(c){c._.panel.hideChild();var d=c._.panel._.panel._.currentBlock,e=d._.focusIndex;d._.markItem(e);}else if(b==27)this.hide();return false;},onHide:function(){if(CKEDITOR.env.ie){var b=this.editor.getSelection();b&&b.unlock();}this.onHide&&this.onHide();},showSubMenu:function(b){var j=this;var c=j._.subMenu,d=j.items[b],e=d.getItems&&d.getItems();if(!e){j._.panel.hideChild();return;}var f=j._.panel.getBlock(j.id);f._.focusIndex=b;if(c)c.removeAll();else{c=j._.subMenu=new CKEDITOR.menu(j.editor,CKEDITOR.tools.extend({},j._.definition,{level:j._.level+1},true));c.parent=j;c._.onClick=CKEDITOR.tools.bind(j._.onClick,j);}for(var g in e){var h=j.editor.getMenuItem(g);if(h){h.state=e[g];c.add(h);}}var i=j._.panel.getBlock(j.id).element.getDocument().getById(j.id+String(b));c.show(i,2);}},proto:{add:function(b){if(!b.order)b.order=this.items.length;this.items.push(b);},removeAll:function(){this.items=[];},show:function(b,c,d,e){if(!this.parent){this._.onShow();if(!this.items.length)return;}c=c||(this.editor.lang.dir=='rtl'?2:1);var f=this.items,g=this.editor,h=this._.panel,i=this._.element;if(!h){h=this._.panel=new CKEDITOR.ui.floatPanel(this.editor,CKEDITOR.document.getBody(),this._.panelDefinition,this._.level);
h.onEscape=CKEDITOR.tools.bind(function(t){if(this._.onEscape(t)===false)return false;},this);h.onHide=CKEDITOR.tools.bind(function(){this._.onHide&&this._.onHide();},this);var j=h.addBlock(this.id,this._.panelDefinition.block);j.autoSize=true;var k=j.keys;k[40]='next';k[9]='next';k[38]='prev';k[CKEDITOR.SHIFT+9]='prev';k[g.lang.dir=='rtl'?37:39]=CKEDITOR.env.ie?'mouseup':'click';k[32]=CKEDITOR.env.ie?'mouseup':'click';CKEDITOR.env.ie&&(k[13]='mouseup');i=this._.element=j.element;i.addClass(g.skinClass);var l=i.getDocument();l.getBody().setStyle('overflow','hidden');l.getElementsByTag('html').getItem(0).setStyle('overflow','hidden');this._.itemOverFn=CKEDITOR.tools.addFunction(function(t){var u=this;clearTimeout(u._.showSubTimeout);u._.showSubTimeout=CKEDITOR.tools.setTimeout(u._.showSubMenu,g.config.menu_subMenuDelay||400,u,[t]);},this);this._.itemOutFn=CKEDITOR.tools.addFunction(function(t){clearTimeout(this._.showSubTimeout);},this);this._.itemClickFn=CKEDITOR.tools.addFunction(function(t){var v=this;var u=v.items[t];if(u.state==CKEDITOR.TRISTATE_DISABLED){v.hide();return;}if(u.getItems)v._.showSubMenu(t);else v._.onClick(u);},this);}a(f);var m=g.container.getChild(1),n=m.hasClass('cke_mixed_dir_content')?' cke_mixed_dir_content':'',o=['<div class="cke_menu'+n+'" role="presentation">'],p=f.length,q=p&&f[0].group;for(var r=0;r<p;r++){var s=f[r];if(q!=s.group){o.push('<div class="cke_menuseparator" role="separator"></div>');q=s.group;}s.render(this,r,o);}o.push('</div>');i.setHtml(o.join(''));CKEDITOR.ui.fire('ready',this);if(this.parent)this.parent._.panel.showAsChild(h,this.id,b,c,d,e);else h.showBlock(this.id,b,c,d,e);g.fire('menuShow',[h]);},addListener:function(b){this._.listeners.push(b);},hide:function(b){var c=this;c._.onHide&&c._.onHide();c._.panel&&c._.panel.hide(b);}}});function a(b){b.sort(function(c,d){if(c.group<d.group)return-1;else if(c.group>d.group)return 1;return c.order<d.order?-1:c.order>d.order?1:0;});};CKEDITOR.menuItem=CKEDITOR.tools.createClass({$:function(b,c,d){var e=this;CKEDITOR.tools.extend(e,d,{order:0,className:'cke_button_'+c});e.group=b._.menuGroups[e.group];e.editor=b;e.name=c;},proto:{render:function(b,c,d){var k=this;var e=b.id+String(c),f=typeof k.state=='undefined'?CKEDITOR.TRISTATE_OFF:k.state,g=' cke_'+(f==CKEDITOR.TRISTATE_ON?'on':f==CKEDITOR.TRISTATE_DISABLED?'disabled':'off'),h=k.label;if(k.className)g+=' '+k.className;var i=k.getItems;d.push('<span class="cke_menuitem'+(k.icon&&k.icon.indexOf('.png')==-1?' cke_noalphafix':'')+'">'+'<a id="',e,'" class="',g,'" href="javascript:void(\'',(k.label||'').replace("'",''),'\')" title="',k.label,'" tabindex="-1"_cke_focus=1 hidefocus="true" role="menuitem"'+(i?'aria-haspopup="true"':'')+(f==CKEDITOR.TRISTATE_DISABLED?'aria-disabled="true"':'')+(f==CKEDITOR.TRISTATE_ON?'aria-pressed="true"':''));
if(CKEDITOR.env.opera||CKEDITOR.env.gecko&&CKEDITOR.env.mac)d.push(' onkeypress="return false;"');if(CKEDITOR.env.gecko)d.push(' onblur="this.style.cssText = this.style.cssText;"');var j=(k.iconOffset||0)*-16;d.push(' onmouseover="CKEDITOR.tools.callFunction(',b._.itemOverFn,',',c,');" onmouseout="CKEDITOR.tools.callFunction(',b._.itemOutFn,',',c,');" '+(CKEDITOR.env.ie?'onclick="return false;" onmouseup':'onclick')+'="CKEDITOR.tools.callFunction(',b._.itemClickFn,',',c,'); return false;"><span class="cke_icon_wrapper"><span class="cke_icon"'+(k.icon?' style="background-image:url('+CKEDITOR.getUrl(k.icon)+');background-position:0 '+j+'px;"':'')+'></span></span>'+'<span class="cke_label">');if(i)d.push('<span class="cke_menuarrow">','<span>&#',k.editor.lang.dir=='rtl'?'9668':'9658',';</span>','</span>');d.push(h,'</span></a></span>');}}});})();CKEDITOR.config.menu_groups='clipboard,form,tablecell,tablecellproperties,tablerow,tablecolumn,table,anchor,link,image,flash,checkbox,radio,textfield,hiddenfield,imagebutton,button,select,textarea,div';
