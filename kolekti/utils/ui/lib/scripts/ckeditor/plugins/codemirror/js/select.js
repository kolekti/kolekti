﻿var select={};(function(){select.ie_selection=!(window.getSelection&&document.createRange&&document.createRange().endContainer);function b(m,n){while(m&&m.parentNode!=n)m=m.parentNode;return m;};function c(m,n){while(!m.previousSibling&&m.parentNode!=n)m=m.parentNode;return b(m.previousSibling,n);};var d='\xa0\xa0\xa0\xa0';select.scrollToNode=function(m,n){if(!m)return;var o=m,p=document.body,q=document.documentElement,r=!o.nextSibling||!o.nextSibling.nextSibling||!o.nextSibling.nextSibling.nextSibling,s=0;while(o&&!o.offsetTop){s++;o=o.previousSibling;}if(s==0)r=false;if(webkit&&o&&o.offsetTop==5&&o.offsetLeft==5)return;var t=s*(o?o.offsetHeight:0),u=0,v=m?m.offsetWidth:0,w=o;while(w&&w.offsetParent){t+=w.offsetTop;if(!isBR(w))u+=w.offsetLeft;w=w.offsetParent;}var x=p.scrollLeft||q.scrollLeft||0,y=p.scrollTop||q.scrollTop||0,z=false,A=window.innerWidth||q.clientWidth||0;if(n||v<A){if(n){var B=select.offsetInNode(m),C=nodeText(m).length;if(C)u+=v*(B/C);}var D=u-x;if(D<0||D>A){x=u;z=true;}}var E=t-y;if(E<0||r||E>(window.innerHeight||q.clientHeight||0)-50){y=r?1000000:t;z=true;}if(z)window.scrollTo(x,y);};select.scrollToCursor=function(m){select.scrollToNode(select.selectionTopNode(m,true)||m.firstChild,true);};var e=null;select.snapshotChanged=function(){if(e)e.changed=true;};function f(m){var n=m.nextSibling;if(n){while(n.firstChild)n=n.firstChild;if(n.nodeType==3||isBR(n))return n;else return f(n);}else{var o=m.parentNode;while(o&&!o.nextSibling)o=o.parentNode;return o&&f(o);}};select.snapshotReplaceNode=function(m,n,o,p){if(!e)return;function q(r){if(m==r.node){e.changed=true;if(o&&r.offset>o)r.offset-=o;else{r.node=n;r.offset+=p||0;}}else if(select.ie_selection&&r.offset==0&&r.node==f(m))e.changed=true;};q(e.start);q(e.end);};select.snapshotMove=function(m,n,o,p,q){if(!e)return;function r(s){if(m==s.node&&(!q||s.offset==0)){e.changed=true;s.node=n;if(p)s.offset=Math.max(0,s.offset+o);else s.offset=o;}};r(e.start);r(e.end);};if(select.ie_selection){function g(){var m=document.selection;if(!m)return null;if(m.createRange)return m.createRange();else return m.createTextRange();};function h(m){var n=g();n.collapse(m);function o(v){var w=null;while(!w&&v){w=v.nextSibling;v=v.parentNode;}return p(w);};function p(v){while(v&&v.firstChild)v=v.firstChild;return{node:v,offset:0};};var q=n.parentElement();if(!isAncestor(document.body,q))return null;if(!q.firstChild)return p(q);var r=n.duplicate();r.moveToElementText(q);r.collapse(true);for(var s=q.firstChild;s;s=s.nextSibling){if(s.nodeType==3){var t=s.nodeValue.length;
r.move('character',t);}else{r.moveToElementText(s);r.collapse(false);}var u=n.compareEndPoints('StartToStart',r);if(u==0)return o(s);if(u==1)continue;if(s.nodeType!=3)return p(s);r.setEndPoint('StartToEnd',n);return{node:s,offset:t-r.text.length};}return o(q);};select.markSelection=function(){e=null;var m=document.selection;if(!m)return;var n=h(true),o=h(false);if(!n||!o)return;e={start:n,end:o,changed:false};};select.selectMarked=function(){if(!e||!e.changed)return;function m(p){var q=document.body.createTextRange(),r=p.node;if(!r){q.moveToElementText(document.body);q.collapse(false);}else if(r.nodeType==3){q.moveToElementText(r.parentNode);var s=p.offset;while(r.previousSibling){r=r.previousSibling;s+=(r.innerText||'').length;}q.move('character',s);}else{q.moveToElementText(r);q.collapse(true);}return q;};var n=m(e.start),o=m(e.end);n.setEndPoint('StartToEnd',o);n.select();};select.offsetInNode=function(m){var n=g();if(!n)return 0;var o=n.duplicate();try{o.moveToElementText(m);}catch(p){return 0;}n.setEndPoint('StartToStart',o);return n.text.length;};select.selectionTopNode=function(m,n){var o=g();if(!o)return false;var p=o.duplicate();o.collapse(n);var q=o.parentElement();if(q&&isAncestor(m,q)){p.moveToElementText(q);if(o.compareEndPoints('StartToStart',p)==1)return b(q,m);}function r(x,y){if(y.nodeType==3){var z=0,A=y.previousSibling;while(A&&A.nodeType==3){z+=A.nodeValue.length;A=A.previousSibling;}if(A){try{x.moveToElementText(A);}catch(B){return false;}x.collapse(false);}else x.moveToElementText(y.parentNode);if(z)x.move('character',z);}else try{x.moveToElementText(y);}catch(C){return false;}return true;};var n=0,s=m.childNodes.length-1;while(n<s){var t=Math.ceil((s+n)/2),u=m.childNodes[t];if(!u)return false;if(!r(p,u))return false;if(o.compareEndPoints('StartToStart',p)==1)n=t;else s=t-1;}if(n==0){var v=g(),w=v.duplicate();try{w.moveToElementText(m);}catch(x){return null;}if(v.compareEndPoints('StartToStart',w)==0)return null;}return m.childNodes[n]||null;};select.focusAfterNode=function(m,n){var o=document.body.createTextRange();o.moveToElementText(m||n);o.collapse(!m);o.select();};select.somethingSelected=function(){var m=g();return m&&m.text!='';};function i(m){var n=g();if(n){n.pasteHTML(m);n.collapse(false);n.select();}};select.insertNewlineAtCursor=function(){i('<br>');};select.insertTabAtCursor=function(){i(d);};select.cursorPos=function(m,n){var o=g();if(!o)return null;var p=select.selectionTopNode(m,n);while(p&&!isBR(p))p=p.previousSibling;
var q=o.duplicate();o.collapse(n);if(p){q.moveToElementText(p);q.collapse(false);}else{try{q.moveToElementText(m);}catch(r){return null;}q.collapse(true);}o.setEndPoint('StartToStart',q);return{node:p,offset:o.text.length};};select.setCursorPos=function(m,n,o){function p(r){var s=document.body.createTextRange();if(!r.node){s.moveToElementText(m);s.collapse(true);}else{s.moveToElementText(r.node);s.collapse(false);}s.move('character',r.offset);return s;};var q=p(n);if(o&&o!=n)q.setEndPoint('EndToEnd',p(o));q.select();};select.getBookmark=function(m){var n=select.cursorPos(m,true),o=select.cursorPos(m,false);if(n&&o)return{from:n,to:o};};select.setBookmark=function(m,n){if(!n)return;select.setCursorPos(m,n.from,n.to);};}else{function j(m,n){while(m.nodeType!=3&&!isBR(m)){var o=m.childNodes[n]||m.nextSibling;n=0;while(!o&&m.parentNode){m=m.parentNode;o=m.nextSibling;}m=o;if(!o)break;}return{node:m,offset:n};};select.markSelection=function(){var m=window.getSelection();if(!m||m.rangeCount==0)return e=null;var n=m.getRangeAt(0);e={start:j(n.startContainer,n.startOffset),end:j(n.endContainer,n.endOffset),changed:false};};select.selectMarked=function(){var m=e;function n(){if(m.start.node==m.end.node&&m.start.offset==m.end.offset){var q=window.getSelection();if(!q||q.rangeCount==0)return true;var r=q.getRangeAt(0),s=j(r.startContainer,r.startOffset);return m.start.node!=s.node||m.start.offset!=s.offset;}};if(!m||!(m.changed||webkit&&n()))return;var o=document.createRange();function p(q,r){if(q.node){if(q.offset==0)o['set'+r+'Before'](q.node);else o['set'+r](q.node,q.offset);}else o.setStartAfter(document.body.lastChild||document.body);};p(m.end,'End');p(m.start,'Start');k(o);};function k(m){var n=window.getSelection();if(!n)return;n.removeAllRanges();n.addRange(m);};function l(){var m=window.getSelection();if(!m||m.rangeCount==0)return false;else return m.getRangeAt(0);};select.selectionTopNode=function(m,n){var o=l();if(!o)return false;var p=n?o.startContainer:o.endContainer,q=n?o.startOffset:o.endOffset;if(window.opera&&!n&&o.endContainer==m&&o.endOffset==o.startOffset+1&&m.childNodes[o.startOffset]&&isBR(m.childNodes[o.startOffset]))q--;if(p.nodeType==3){if(q>0)return b(p,m);else return c(p,m);}else if(p.nodeName.toUpperCase()=='HTML')return q==1?null:m.lastChild;else if(p==m)return q==0?null:p.childNodes[q-1];else if(q==p.childNodes.length)return b(p,m);else if(q==0)return c(p,m);else return b(p.childNodes[q-1],m);};select.focusAfterNode=function(m,n){var o=document.createRange();
o.setStartBefore(n.firstChild||n);if(m&&!m.firstChild)o.setEndAfter(m);else if(m)o.setEnd(m,m.childNodes.length);else o.setEndBefore(n.firstChild||n);o.collapse(false);k(o);};select.somethingSelected=function(){var m=l();return m&&!m.collapsed;};select.offsetInNode=function(m){var n=l();if(!n)return 0;n=n.cloneRange();n.setStartBefore(m);return n.toString().length;};select.insertNodeAtCursor=function(m){var n=l();if(!n)return;n.deleteContents();n.insertNode(m);webkitLastLineHack(document.body);if(window.opera&&isBR(m)&&isSpan(m.parentNode)){var o=m.nextSibling,p=m.parentNode,q=p.parentNode;q.insertBefore(m,p.nextSibling);var r='';for(;o&&o.nodeType==3;o=o.nextSibling){r+=o.nodeValue;removeElement(o);}q.insertBefore(makePartSpan(r,document),m.nextSibling);}n=document.createRange();n.selectNode(m);n.collapse(false);k(n);};select.insertNewlineAtCursor=function(){select.insertNodeAtCursor(document.createElement('BR'));};select.insertTabAtCursor=function(){select.insertNodeAtCursor(document.createTextNode(d));};select.cursorPos=function(m,n){var o=l();if(!o)return;var p=select.selectionTopNode(m,n);while(p&&!isBR(p))p=p.previousSibling;o=o.cloneRange();o.collapse(n);if(p)o.setStartAfter(p);else o.setStartBefore(m);var q=o.toString();return{node:p,offset:q.length};};select.setCursorPos=function(m,n,o){var p=document.createRange();function q(r,s,t){if(s==0&&r&&!r.nextSibling){p['set'+t+'After'](r);return true;}if(!r)r=m.firstChild;else r=r.nextSibling;if(!r)return;if(s==0){p['set'+t+'Before'](r);return true;}var u=[];function v(y){if(y.nodeType==3)u.push(y);else forEach(y.childNodes,v);};for(;;){while(r&&!u.length){v(r);r=r.nextSibling;}var w=u.shift();if(!w)return false;var x=w.nodeValue.length;if(x>=s){p['set'+t](w,s);return true;}s-=x;}};o=o||n;if(q(o.node,o.offset,'End')&&q(n.node,n.offset,'Start'))k(p);};}})();
