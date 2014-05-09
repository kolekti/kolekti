﻿var XMLParser=Editor.Parser=(function(){var b={autoSelfClosers:{br:true,img:true,hr:true,link:true,input:true,meta:true,col:true,frame:true,base:true,area:true},doNotIndent:{pre:true,'!cdata':true}},c={autoSelfClosers:{},doNotIndent:{'!cdata':true}},d=b,e=false,f=(function(){function h(l,m){var n=l.next();if(n=='<'){if(l.equals('!')){l.next();if(l.equals('[')){if(l.lookAhead('[CDATA[',true)){m(k('xml-cdata',']]>'));return null;}else return 'xml-text';}else if(l.lookAhead('--',true)){m(k('xml-comment','-->'));return null;}else if(l.lookAhead('DOCTYPE',true)){l.nextWhileMatches(/[\w\._\-]/);m(k('xml-doctype','>'));return 'xml-doctype';}else return 'xml-text';}else if(l.equals('?')){l.next();l.nextWhileMatches(/[\w\._\-]/);m(k('xml-processing','?>'));return 'xml-processing';}else{if(l.equals('/'))l.next();m(i);return 'xml-punctuation';}}else if(n=='&'){while(!l.endOfLine()){if(l.next()==';')break;}return 'xml-entity';}else{l.nextWhileMatches(/[^&<\n]/);return 'xml-text';}};function i(l,m){var n=l.next();if(n=='>'){m(h);return 'xml-punctuation';}else if(/[?\/]/.test(n)&&l.equals('>')){l.next();m(h);return 'xml-punctuation';}else if(n=='=')return 'xml-punctuation';else if(/[\'\"]/.test(n)){m(j(n));return null;}else{l.nextWhileMatches(/[^\s\u00a0=<>\"\'\/?]/);return 'xml-name';}};function j(l){return function(m,n){while(!m.endOfLine()){if(m.next()==l){n(i);break;}}return 'xml-attribute';};};function k(l,m){return function(n,o){while(!n.endOfLine()){if(n.lookAhead(m,true)){o(h);break;}n.next();}return l;};};return function(l,m){return tokenizer(l,m||h);};})();function g(h){var i=f(h),j,k=[y],l=0,m=0,n=null,o=null,p;function q(H){for(var I=H.length-1;I>=0;I--)k.push(H[I]);};function r(){q(arguments);p=true;};function s(){q(arguments);p=false;};function t(){j.style+=' xml-error';};function u(H){return function(I,J){if(J==H)r();else{t();r(arguments.callee);}};};function v(H,I){var J=d.doNotIndent.hasOwnProperty(H)||o&&o.noIndent;o={prev:o,name:H,indent:m,startOfLine:I,noIndent:J};};function w(){o=o.prev;};function x(H){return function(I,J){var K=H;if(K&&K.noIndent)return J;if(e&&/<!\[CDATA\[/.test(I))return 0;if(K&&/^<\//.test(I))K=K.prev;while(K&&!K.startOfLine)K=K.prev;if(K)return K.indent+indentUnit;else return 0;};};function y(){return s(A,y);};var z={'xml-text':true,'xml-entity':true,'xml-comment':true,'xml-processing':true,'xml-doctype':true};function A(H,I){if(I=='<')r(B,E,D(l==1));else if(I=='</')r(C,u('>'));else if(H=='xml-cdata'){if(!o||o.name!='!cdata')v('!cdata');
if(/\]\]>$/.test(I))w();r();}else if(z.hasOwnProperty(H))r();else{t();r();}};function B(H,I){if(H=='xml-name'){n=I.toLowerCase();j.style='xml-tagname';r();}else{n=null;s();}};function C(H,I){if(H=='xml-name'){j.style='xml-tagname';if(o&&I.toLowerCase()==o.name)w();else t();}r();};function D(H){return function(I,J){if(J=='/>'||J=='>'&&d.autoSelfClosers.hasOwnProperty(n))r();else if(J=='>'){v(n,H);r();}else{t();r(arguments.callee);}};};function E(H){if(H=='xml-name'){j.style='xml-attname';r(F,E);}else s();};function F(H,I){if(I=='=')r(G);else if(I=='>'||I=='/>')s(D);else s();};function G(H){if(H=='xml-attribute')r(G);else s();};return{indentation:function(){return m;},next:function(){j=i.next();if(j.style=='whitespace'&&l==0)m=j.value.length;else l++;if(j.content=='\n'){m=l=0;j.indentation=x(o);}if(j.style=='whitespace'||j.type=='xml-comment')return j;for(;;){p=false;k.pop()(j.style,j.content);if(p)return j;}},copy:function(){var H=k.concat([]),I=i.state,J=o,K=this;return function(L){k=H.concat([]);l=m=0;o=J;i=f(L,I);return K;};}};};return{make:g,electricChars:'/',configure:function(h){if(h.useHTMLKludges!=null)d=h.useHTMLKludges?b:c;if(h.alignCDATA)e=h.alignCDATA;}};})();
