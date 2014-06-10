﻿var CodeMirrorConfig=window.CodeMirrorConfig||{},CodeMirror=(function(){function c(j,k){for(var l in k){if(!j.hasOwnProperty(l))j[l]=k[l];}};function d(j,k){for(var l=0;l<j.length;l++)k(j[l]);};function e(j){if(document.createElementNS&&document.documentElement.namespaceURI!==null)return document.createElementNS('http://www.w3.org/1999/xhtml',j);else return document.createElement(j);};c(CodeMirrorConfig,{stylesheet:[],path:'',parserfile:[],basefiles:['util.js','stringstream.js','select.js','undo.js','editor.js','tokenize.js'],iframeClass:null,passDelay:200,passTime:50,lineNumberDelay:200,lineNumberTime:50,continuousScanning:false,saveFunction:null,onLoad:null,onChange:null,undoDepth:50,undoDelay:800,disableSpellcheck:true,textWrapping:true,readOnly:false,width:'',height:'300px',minHeight:100,onDynamicHeightChange:null,autoMatchParens:false,markParen:null,unmarkParen:null,parserConfig:null,tabMode:'indent',enterMode:'indent',electricChars:true,reindentOnLoad:false,activeTokens:null,onCursorActivity:null,lineNumbers:false,firstLineNumber:1,onLineNumberClick:null,indentUnit:2,domain:null,noScriptCaching:false,incrementalLoading:false});function f(j,k){var l=e('div'),m=e('div');l.style.position='absolute';l.style.height='100%';if(l.style.setExpression)try{l.style.setExpression('height',"this.previousSibling.offsetHeight + 'px'");}catch(n){}l.style.top='0px';l.style.left='0px';l.style.overflow='hidden';j.appendChild(l);m.className='CodeMirror-line-numbers';l.appendChild(m);m.innerHTML='<div>'+k+'</div>';return l;};function g(j){if(typeof j.parserfile=='string')j.parserfile=[j.parserfile];if(typeof j.basefiles=='string')j.basefiles=[j.basefiles];if(typeof j.stylesheet=='string')j.stylesheet=[j.stylesheet];var k=' spellcheck="'+(j.disableSpellcheck?'false':'true')+'"',l=['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"><html'+k+'><head>'];l.push('<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7"/>');var m=j.noScriptCaching?'?nocache='+new Date().getTime().toString(16):'';d(j.stylesheet,function(n){l.push('<link rel="stylesheet" type="text/css" href="'+n+m+'"/>');});d(j.basefiles.concat(j.parserfile),function(n){if(!/^https?:/.test(n))n=j.path+n;l.push('<script type="text/javascript" src="'+n+m+'"><'+'/script>');});l.push('</head><body style="border-width: 0;" class="editbox"'+k+'></body></html>');return l.join('');};var h=document.selection&&window.ActiveXObject&&/MSIE/.test(navigator.userAgent);function i(j,k){var o=this;
o.options=k=k||{};c(k,CodeMirrorConfig);if(k.dumbTabs)k.tabMode='spaces';else if(k.normalTab)k.tabMode='default';if(k.cursorActivity)k.onCursorActivity=k.cursorActivity;var l=o.frame=e('iframe');if(k.iframeClass)l.className=k.iframeClass;l.frameBorder=0;l.style.border='0';l.style.width='100%';l.style.height='100%';l.style.display='block';var m=o.wrapping=e('div');m.style.position='relative';m.className='CodeMirror-wrapping';m.style.width=k.width;m.style.height=k.height=='dynamic'?k.minHeight+'px':k.height;var n=o.textareaHack=e('textarea');m.appendChild(n);n.style.position='absolute';n.style.left='-10000px';n.style.width='10px';n.tabIndex=100000;l.CodeMirror=o;if(k.domain&&h){o.html=g(k);l.src='javascript:(function(){document.open();'+(k.domain?'document.domain="'+k.domain+'";':'')+'document.write(window.frameElement.CodeMirror.html);document.close();})()';}else l.src='javascript:;';if(j.appendChild)j.appendChild(m);else j(m);m.appendChild(l);if(k.lineNumbers)o.lineNumbers=f(m,k.firstLineNumber);o.win=l.contentWindow;if(!k.domain||!h){o.win.document.open();o.win.document.write(g(k));o.win.document.close();}};i.prototype={init:function(){var j=this;if(j.options.initCallback)j.options.initCallback(j);if(j.options.onLoad)j.options.onLoad(j);if(j.options.lineNumbers)j.activateLineNumbers();if(j.options.reindentOnLoad)j.reindent();if(j.options.height=='dynamic')j.setDynamicHeight();},getCode:function(){return this.editor.getCode();},setCode:function(j){this.editor.importCode(j);},selection:function(){this.focusIfIE();return this.editor.selectedText();},reindent:function(){this.editor.reindent();},reindentSelection:function(){this.focusIfIE();this.editor.reindentSelection(null);},focusIfIE:function(){if(this.win.select.ie_selection&&document.activeElement!=this.frame)this.focus();},focus:function(){var j=this;j.win.focus();if(j.editor.selectionSnapshot)j.win.select.setBookmark(j.win.document.body,j.editor.selectionSnapshot);},replaceSelection:function(j){this.focus();this.editor.replaceSelection(j);return true;},replaceChars:function(j,k,l){this.editor.replaceChars(j,k,l);},getSearchCursor:function(j,k,l){return this.editor.getSearchCursor(j,k,l);},undo:function(){this.editor.history.undo();},redo:function(){this.editor.history.redo();},historySize:function(){return this.editor.history.historySize();},clearHistory:function(){this.editor.history.clear();},grabKeys:function(j,k){this.editor.grabKeys(j,k);},ungrabKeys:function(){this.editor.ungrabKeys();},setParser:function(j,k){this.editor.setParser(j,k);
},setSpellcheck:function(j){this.win.document.body.spellcheck=j;},setStylesheet:function(j){if(typeof j==='string')j=[j];var k={},l={},m=this.win.document.getElementsByTagName('link');for(var n=0,o;o=m[n];n++){if(o.rel.indexOf('stylesheet')!==-1)for(var p=0;p<j.length;p++){var q=j[p];if(o.href.substring(o.href.length-q.length)===q){k[o.href]=true;l[q]=true;}}}for(var n=0,o;o=m[n];n++){if(o.rel.indexOf('stylesheet')!==-1)o.disabled=!(o.href in k);}for(var p=0;p<j.length;p++){var q=j[p];if(!(q in l)){var o=this.win.document.createElement('link');o.rel='stylesheet';o.type='text/css';o.href=q;this.win.document.getElementsByTagName('head')[0].appendChild(o);}}},setTextWrapping:function(j){var k=this;if(j==k.options.textWrapping)return;k.win.document.body.style.whiteSpace=j?'':'nowrap';k.options.textWrapping=j;if(k.lineNumbers){k.setLineNumbers(false);k.setLineNumbers(true);}},setIndentUnit:function(j){this.win.indentUnit=j;},setUndoDepth:function(j){this.editor.history.maxDepth=j;},setTabMode:function(j){this.options.tabMode=j;},setEnterMode:function(j){this.options.enterMode=j;},setLineNumbers:function(j){var k=this;if(j&&!k.lineNumbers){k.lineNumbers=f(k.wrapping,k.options.firstLineNumber);k.activateLineNumbers();}else if(!j&&k.lineNumbers){k.wrapping.removeChild(k.lineNumbers);k.wrapping.style.paddingLeft='';k.lineNumbers=null;}},cursorPosition:function(j){this.focusIfIE();return this.editor.cursorPosition(j);},firstLine:function(){return this.editor.firstLine();},lastLine:function(){return this.editor.lastLine();},nextLine:function(j){return this.editor.nextLine(j);},prevLine:function(j){return this.editor.prevLine(j);},lineContent:function(j){return this.editor.lineContent(j);},setLineContent:function(j,k){this.editor.setLineContent(j,k);},removeLine:function(j){this.editor.removeLine(j);},insertIntoLine:function(j,k,l){this.editor.insertIntoLine(j,k,l);},selectLines:function(j,k,l,m){this.win.focus();this.editor.selectLines(j,k,l,m);},nthLine:function(j){var k=this.firstLine();for(;j>1&&k!==false;j--)k=this.nextLine(k);return k;},lineNumber:function(j){var k=0;while(j!==false){k++;j=this.prevLine(j);}return k;},jumpToLine:function(j){if(typeof j=='number')j=this.nthLine(j);this.selectLines(j,0);this.win.focus();},currentLine:function(){return this.lineNumber(this.cursorLine());},cursorLine:function(){return this.cursorPosition().line;},cursorCoords:function(j){return this.editor.cursorCoords(j);},activateLineNumbers:function(){var j=this.frame,k=j.contentWindow,l=k.document,m=l.body,n=this.lineNumbers,o=n.firstChild,p=this,q=null;
n.onclick=function(y){var z=p.options.onLineNumberClick;if(z){var A=(y||window.event).target||(y||window.event).srcElement,B=A==n?NaN:Number(A.innerHTML);if(!isNaN(B))z(B,A);}};function r(){if(j.offsetWidth==0)return;for(var y=j;y.parentNode;y=y.parentNode){}if(!n.parentNode||y!=document||!k.Editor){try{t();}catch(z){}clearInterval(u);return;}if(n.offsetWidth!=q){q=n.offsetWidth;j.parentNode.style.paddingLeft=q+'px';}};function s(){n.scrollTop=m.scrollTop||l.documentElement.scrollTop||0;};var t=function(){};r();var u=setInterval(r,500);function v(y){var z=o.firstChild.offsetHeight;if(z==0)return;var A=50+Math.max(m.offsetHeight,Math.max(j.offsetHeight,m.scrollHeight||0)),B=Math.ceil(A/z);for(var C=o.childNodes.length;C<=B;C++){var D=e('div');D.appendChild(document.createTextNode(y?String(C+p.options.firstLineNumber):'\xa0'));o.appendChild(D);}};function w(){function y(){v(true);s();};p.updateNumbers=y;var z=k.addEventHandler(k,'scroll',s,true),A=k.addEventHandler(k,'resize',y,true);t=function(){z();A();if(p.updateNumbers==y)p.updateNumbers=null;};y();};function x(){var y,z,A,B,C=[],D=p.options.styleNumbers;function E(M,N){if(!z)z=o.appendChild(e('div'));if(D)D(z,N,M);C.push(z);C.push(M);B=z.offsetHeight+z.offsetTop;z=z.nextSibling;};function F(){for(var M=0;M<C.length;M+=2)C[M].innerHTML=C[M+1];C=[];};function G(){if(!o.parentNode||o.parentNode!=p.lineNumbers)return;var M=new Date().getTime()+p.options.lineNumberTime;while(y){E(A++,y.previousSibling);for(;y&&!k.isBR(y);y=y.nextSibling){var N=y.offsetTop+y.offsetHeight;while(o.offsetHeight&&N-3>B){var O=B;E('&nbsp;');if(B<=O)break;}}if(y)y=y.nextSibling;if(new Date().getTime()>M){F();I=setTimeout(G,p.options.lineNumberDelay);return;}}while(z)E(A++);F();s();};function H(M){s();v(M);y=m.firstChild;z=o.firstChild;B=0;A=p.options.firstLineNumber;G();};H(true);var I=null;function J(){if(I)clearTimeout(I);if(p.editor.allClean())H();else I=setTimeout(J,200);};p.updateNumbers=J;var K=k.addEventHandler(k,'scroll',s,true),L=k.addEventHandler(k,'resize',J,true);t=function(){if(I)clearTimeout(I);if(p.updateNumbers==J)p.updateNumbers=null;K();L();};};this.options.textWrapping||this.options.styleNumbers?x:w();},setDynamicHeight:function(){var j=this,k=j.options.onCursorActivity,l=j.win,m=l.document.body,n=null,o=null,p=2*j.frame.offsetTop;m.style.overflowY='hidden';l.document.documentElement.style.overflowY='hidden';this.frame.scrolling='no';function q(){var r=0,s=m.lastChild,t;while(s&&l.isBR(s)){if(!s.hackBR)r++;s=s.previousSibling;
}if(s){n=s.offsetHeight;t=s.offsetTop+(1+r)*n;}else if(n)t=r*n;if(t){if(j.options.onDynamicHeightChange)t=j.options.onDynamicHeightChange(t);if(t)j.wrapping.style.height=Math.max(p+t,j.options.minHeight)+'px';}};setTimeout(q,300);j.options.onCursorActivity=function(r){if(k)k(r);clearTimeout(o);o=setTimeout(q,100);};}};i.InvalidLineHandle={'toString':function(){return 'CodeMirror.InvalidLineHandle';}};i.replace=function(j){if(typeof j=='string')j=document.getElementById(j);return function(k){j.parentNode.replaceChild(k,j);};};i.fromTextArea=function(j,k){if(typeof j=='string')j=document.getElementById(j);k=k||{};if(j.style.width&&k.width==null)k.width=j.style.width;if(j.style.height&&k.height==null)k.height=j.style.height;if(k.content==null)k.content=j.value;function l(){j.value=p.getCode();};if(j.form){if(typeof j.form.addEventListener=='function')j.form.addEventListener('submit',l,false);else j.form.attachEvent('onsubmit',l);if(typeof j.form.submit=='function'){var m=j.form.submit;function n(){l();j.form.submit=m;j.form.submit();j.form.submit=n;};j.form.submit=n;}}function o(q){if(j.nextSibling)j.parentNode.insertBefore(q,j.nextSibling);else j.parentNode.appendChild(q);};j.style.display='none';var p=new i(o,k);p.save=l;p.toTextArea=function(){l();j.parentNode.removeChild(p.wrapping);j.style.display='';if(j.form){if(typeof j.form.submit=='function')j.form.submit=m;if(typeof j.form.removeEventListener=='function')j.form.removeEventListener('submit',l,false);else j.form.detachEvent('onsubmit',l);}};return p;};i.isProbablySupported=function(){var j;if(window.opera)return Number(window.opera.version())>=9.52;else if(/Apple Computer, Inc/.test(navigator.vendor)&&(j=navigator.userAgent.match(/Version\/(\d+(?:\.\d+)?)\./)))return Number(j[1])>=3;else if(document.selection&&window.ActiveXObject&&(j=navigator.userAgent.match(/MSIE (\d+(?:\.\d*)?)\b/)))return Number(j[1])>=6;else if(j=navigator.userAgent.match(/gecko\/(\d{8})/i))return Number(j[1])>=20050901;else if(j=navigator.userAgent.match(/AppleWebKit\/(\d+)/))return Number(j[1])>=525;else return null;};return i;})();