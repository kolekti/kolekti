﻿var RegexParser=Editor.Parser=(function(){var b=['unicode_blocks','unicode_scripts','unicode_categories','unicode_classes','named_backreferences','empty_char_class','mode_modifier'],c=['unicode_mode'],d='imgxs',e={},f,g,h,i,j,k,l='',m,n;e.literal_initial='/';function o(A,B){var C={state:B,take:function(D){if(typeof D=='string')D={style:D,type:D};D.content=(D.content||'')+A.get();D.value=D.content+A.get();return D;},next:function(){if(!A.more())throw StopIteration;var D;if(A.equals('\n')){A.next();return this.take('whitespace');}while(!D)D=this.state(A,function(E){C.state=E;});return this.take(D);}};return C;};function p(A,B){var C=/\w{4}/g,D=RegexParser.unicode,E=D[A];if(E.hasOwnProperty(B))return E[B].replace(C,function(F){if(F==='002D')return 'U+'+F;return String.fromCharCode(parseInt('0x'+F,16));});return false;};function q(A,B){var C={};for(var D in A){if(A.hasOwnProperty(D)){if(B&&typeof A[D]==='object'&&A[D]!==null)C[D]=q(A[D],B);else C[D]=A[D];}}return C;};function r(A,B){for(var C=0,D=A.length;C<D;C++)B(A[C],C);};function s(A,B){A=typeof A==='string'?[A]:A;r(A,function(C){e[C]=B;});};function t(A){var B=0,C=0,D=0,E=0,F,G=document,H=function(J,K){var L=J.cssRules?J.cssRules:J.rules;for(C=0,E=L.length;C<E;C++){var M=L[C];try{if(M.type===CSSRule.STYLE_RULE&&M.selectorText===K)return true;}catch(N){if(M.selectorText===K)return true;}}return false;},I;for(B=0,D=G.styleSheets.length;B<D;B++){F=G.styleSheets[B];I=H(F,A);if(I)break;}return I;};function u(A){if(/[^a-z]/.test(A))throw 'Invalid flag supplied to the regular expression parser';l+=A;};function v(A){if(/[^a-z]/.test(A))throw 'Invalid flag supplied to the regular expression parser';d=A;};function w(A){return A.replace(/"[.\\+*?\[\^\]$(){}=!<>|:\-]/g,'\\$&');};var x=(function(){function A(L){return l.indexOf(L)>-1;};function B(L,M){var N=L.lookAheadRegex(M,true);if(N&&N.length>1)for(var O=N.length-1;O>=0;O--){if(N[O]!=null)return O;}return 0;};function C(L,M,N){var O=' regex-'+L+'unicode',P='regex-unicode-class-'+M+O,Q,R=RegexParser.unicode;if(!R)throw 'Unicode plugin of the regular expression parser not properly loaded';if(e.unicode_categories){var S=N.lookAheadRegex(/^\\[pP]{\^?([A-Z][a-z]?)}/,true);if(S){Q=S[1];if(R.categories[Q])return P+'-category-'+M+O+'-category-'+Q+'-'+M;return 'regex-bad-sequence';}}if(e.unicode_blocks){var T=N.lookAheadRegex(/^\\[pP]{\^?(In[A-Z][^}]*)}/,true);if(T){Q=T[1];if(R.blocks[Q])return P+'-block-'+M+O+'-block-'+Q+'-'+M;return 'regex-bad-sequence';}}if(e.unicode_scripts){var U=N.lookAheadRegex(/^\\[pP]{\^?([^}]*)}/,true);
if(U){Q=U[1];if(R.scripts[Q])return P+'-script-'+M+O+'-script-'+Q+'-'+M;return 'regex-bad-sequence';}}return false;};function D(L,M){var N='regex-unicode-class-'+M+' ',O='';if(L.lookAheadRegex(/^\\P/)||L.lookAheadRegex(/^\\p{\^/))O='negated';else if(L.lookAheadRegex(/^\\P{\^/))return false;switch(e.unicode_mode){case 'validate':case 'store':return C(O,M,L);case 'simple':default:if(e.unicode_categories&&L.lookAheadRegex(/^\\[pP]{\^?[A-Z][a-z]?}/,true))return N+'regex-'+O+'unicode-category';if(e.unicode_blocks&&L.lookAheadRegex(/^\\[pP]{\^?In[A-Z][^}]*}/,true))return N+'regex-'+O+'unicode-block';if(e.unicode_scripts&&L.lookAheadRegex(/^\\[pP]{\^?[^}]*}/,true))return N+'regex-'+O+'unicode-script';break;}return false;};var E=/^\\(?:([0-3][0-7]{0,2}|[4-7][0-7]?)|(x[\dA-Fa-f]{2})|(u[\dA-Fa-f]{4})|(c[A-Za-z])|(-\\]^)|([bBdDfnrsStvwW0])|([^\n]))/;function F(L,M){var N;if(L.lookAhead(']',true)){M(K);return 'regex-class-end';}if(j&&L.lookAhead('^',true)){j=false;return 'regex-class-negator';}if(L.lookAhead('-',true)){if(!i)N='regex-class-initial-hyphen';else if(L.equals(']'))N='regex-class-final-hyphen';else return 'regex-class-range-hyphen';}else if(!L.equals('\\')){var O=L.next();if(e.literal&&O===e.literal_initial)return 'regex-bad-character';N='regex-class-character';}else if(f=D(L,'inside'))N=f;else if(L.lookAheadRegex(/^\\(\n|$)/)){L.next();N='regex-bad-character';}else{switch(B(L,E)){case 1:N='regex-class-octal';break;case 2:N='regex-class-hex';break;case 3:N='regex-class-unicode-escape';break;case 4:N='regex-class-ascii-control';break;case 5:N='regex-class-escaped-special';break;case 6:N='regex-class-special-escape';break;case 7:N='regex-class-extra-escaped';break;default:throw 'Unexpected character inside class, beginning '+L.lookAheadRegex(/^[\s\S]+$/)[0]+' and of length '+L.lookAheadRegex(/^[\s\S]+$/)[0].length;}}if(i){i=false;N+='-end-range';}else if(L.equals('-')){i=true;N+='-begin-range';}return N;};var G=/^(?:\\(?:(0(?:[0-3][0-7]{0,2}|[4-7][0-7]?)?)|([1-9]\d*)|(x[\dA-Fa-f]{2})|(u[\dA-Fa-f]{4})|(c[A-Za-z])|([bBdDfnrsStvwW0])|([?*+])|([.\\[$|{])|([^\n]))|([?*+]\??)|({\d+(?:,\d*)?}\??))/;function H(L,M){if(f=D(L,'outside'))return f;switch(B(L,G)){case 1:return 'regex-octal';case 2:return 'regex-ascii';case 3:return 'regex-hex';case 4:return 'regex-unicode-escape';case 5:return 'regex-ascii-control';case 6:return 'regex-special-escape';case 7:return 'regex-quantifier-escape';case 8:return 'regex-escaped-special';case 9:return 'regex-extra-escaped';case 10:return 'regex-quantifiers';
case 11:return 'regex-repetition';default:if(e.literal&&L.lookAhead(e.literal_initial,true)){if(!g){g=true;return 'regex-literal-begin';}h=true;M(I);return 'regex-literal-end';}if(L.lookAhead('|',true))return 'regex-alternator';if(L.lookAheadRegex(/^\\$/,true))return 'regex-bad-character';L.next();return 'regex-character';}};function I(L,M){var N=L.lookAheadRegex(new RegExp('^['+d+']*',''),true);if(N==null)return 'regex-bad-character';M(J);return 'regex-flags';};function J(){throw StopIteration;};function K(L,M){if(e.named_backreferences&&L.lookAheadRegex(/^\\k<([\w$]+)>/,true))return 'regex-named-backreference';if(A('x')&&L.lookAheadRegex(/^(?:#.*)+?/,true))return 'regex-free-spacing-mode';if(L.lookAhead('[',true)){if(L.lookAheadRegex(/^\^?]/,true))return e.empty_char_class?'regex-empty-class':'regex-bad-character';if(L.equals('^'))j=true;M(F);return 'regex-class-begin';}if(L.lookAhead(')',true))return 'regex-ending-group';if(L.lookAhead('(',true)){if(e.mode_modifier&&k){var N=L.lookAheadRegex(/^\?([imsx]+)\)/,true);if(N){k=false;return 'regex-mode-modifier';}}if(L.lookAheadRegex(/^\?#[^)]*\)/,true))return 'regex-comment-pattern';var O;if(L.lookAheadRegex(/^(?!\?)/,true))O='regex-capturing-group';if(L.lookAheadRegex(/^\?<([$\w]+)>/,true))O='regex-named-capturing-group';if(L.lookAheadRegex(/^\?[:=!]/,true))O='regex-grouping';if(!O)return 'regex-bad-character';return O;}return H(L,M);};return function(L,M){return o(L,M||K);};})();function y(){g=false,h=false,i=false,j=false,k=false;l='';if(e.flags)u(e.flags);m=[],n={'capturing-group':{currentCount:0},'named-capturing-group':{currentCount:0},grouping:{currentCount:0}};};function z(A){y();var B=x(A);if(e.literal&&!A.equals(e.literal_initial))throw 'Regular expression literals must include a beginning "'+e.literal_initial+'"';if(e.literal){var C=new RegExp('^[\\s\\S]*'+w(e.literal_initial)+'(['+d+']*)$',''),D=A.lookAheadRegex(C);if(D==null){}else u(D[1]);}else if(e.mode_modifier){var E=A.lookAheadRegex(/^\(\?([imsx]+)\)/,true);if(E){k=true;u(E[1]);}}var F={next:function(){try{var G,H=B.next(),I=H.style,J=H.content,K,L,M,N,O=I.replace(/^regex-/,'');switch(O){case 'ending-group':if(!m.length)H.style='regex-bad-character';else{G=e.max_levels?m.length%e.max_levels||e.max_levels:m.length;var P=m.pop();L=n[P];while(L&&L.currentChildren&&L.currentChildren.currentChildren)L=L.currentChildren;delete L.currentChildren;M=L.currentCount;M=e.max_alternating?M%e.max_alternating||e.max_alternating:M;N=G+'-'+M;H.style='regex-ending-'+P+' regex-ending-'+P+N;
if(e.inner_group_mode==='uniform')H.style+=' regex-group-'+N;}break;case 'capturing-group':case 'named-capturing-group':case 'grouping':K=n[O],L=n[O].currentChildren;while(L){K=L;L=L.currentChildren;}M=++K.currentCount;if(!K.currentChildren)K.currentChildren={currentCount:0};m.push(O);G=e.max_levels?m.length%e.max_levels||e.max_levels:m.length;M=e.max_alternating?M%e.max_alternating||e.max_alternating:M;N=G+'-'+M;var Q=' '+H.style;if(e.inner_group_mode){H.style+=e.inner_group_mode==='type'?Q+N:' regex-group-'+N;H.style+=' '+I+N;}else H.style+=Q+N;K.currentGroupStyle=N;K.currentStyle=Q;break;case 'class-octal':case 'octal':case 'class-octal-begin-range':case 'class-octal-end-range':case 'class-ascii-begin-range':case 'class-ascii-end-range':case 'class-ascii':case 'ascii':H.equivalent=String.fromCharCode(parseInt(J.replace(/^\\/,''),8));break;case 'class-hex':case 'hex':case 'class-hex-begin-range':case 'class-hex-end-range':case 'class-unicode-escape':case 'class-unicode-escape-begin-range':case 'class-unicode-escape-end-range':case 'unicode-escape':H.equivalent=String.fromCharCode(parseInt('0x'+J.replace(/^\\(x|u)/,''),16));break;case 'class-ascii-control-begin-range':case 'class-ascii-control-end-range':case 'class-ascii-control':case 'ascii-control':H.equivalent=String.fromCharCode(J.replace(/^\\c/,'').charCodeAt(0)-64);break;case 'class-special-escape':case 'class-special-escape-begin-range':case 'class-special-escape-end-range':case 'special-escape':var R=J.replace(/^\\/,''),S=fnrtv.indexOf(R),T='\f\n\r\t\v';if(S!==-1){var U=T.charAt(S),V=U.charCodeAt(0).toString(16).toUpperCase();H.display='U+'+Array(5-V.length).join('0')+V;H.equivalent=U;}break;case 'regex-class-escaped-special':case 'regex-class-escaped-special-begin-range':case 'regex-class-escaped-special-end-range':case 'class-extra-escaped-begin-range':case 'class-extra-escaped-end-range':case 'class-extra-escaped':case 'extra-escaped':H.equivalent=J.replace(/^\\/,'');break;default:if(e.unicode_mode==='store'){if(e.unicode_categories){var W=O.match(/regex-unicode-category-(\w+?)-(?:outside|inside)/);if(W){H.equivalent=p('categories',W[1])||'';H.unicode=true;break;}}if(e.unicode_blocks){var X=O.match(/regex-unicode-block-(\w+)-(?:outside|inside)/);if(X){H.equivalent=p('blocks',X[1])||'';H.unicode=true;break;}}if(e.unicode_scripts){var Y=O.match(/regex-unicode-script-(\w+)-(?:outside|inside)/);if(Y){H.equivalent=p('scripts',Y[1])||'';H.unicode=true;break;}}}break;}if(e.inner_group_mode&&O!=='ending-group'&&O!=='capturing-group'&&O!=='named-capturing-group'&&O!=='grouping'){G=e.max_levels?m.length%e.max_levels||e.max_levels:m.length;
var Z=m[m.length-1];if(Z){L=n[Z];while(L&&L.currentChildren&&L.currentChildren.currentChildren)L=L.currentChildren;H.style+=e.inner_group_mode==='type'?L.currentStyle+L.currentGroupStyle:' regex-group-'+L.currentGroupStyle;}}if(!A.more()){if(m.length)H.style='regex-bad-character';else if(e.literal&&!h)H.style='regex-bad-character';}}catch(aa){if(aa!=StopIteration)alert(aa+'::'+aa.lineNumber);throw aa;}return H;},copy:function(){var G=g,H=i,I=j,J=l,K=h,L=m,M=k,N=B.state,O=q(n,true);return function(P){g=G;i=H;j=I;l=J;h=K;m=L;k=M;B=x(P,N);n=O;return F;};}};return F;};return{make:z,configure:function(A){var B=this.unicode;s('unicode_mode','simple');s(b,false);if(A.unicode_classes)s(['unicode_blocks','unicode_scripts','unicode_categories'],true);switch(A.flavor){case 'ecma-262-ed5':s(['empty_char_class'],true);case 'ecma-262-ed3':e.possible_flags='gim';break;case 'all':default:s(b,true);break;}for(var C in A){if(/^regex_/.test(C)){e[C.replace(/^regex_/,'')]=A[C];continue;}e[C]=A[C];}if(e.possible_flags)v(e.possible_flags);if(e.unicode_mode!=='simple'){if(!B)throw 'You must include the parseregex-unicode.js file in order to use validate or storage mode Unicode';}}};})();
