﻿var PHPHTMLMixedParser=Editor.Parser=(function(){var b=['<?php'];if(!(PHPParser&&CSSParser&&JSParser&&XMLParser))throw new Error('PHP, CSS, JS, and XML parsers must be loaded for PHP+HTML mixed mode to work.');XMLParser.configure({useHTMLKludges:true});function c(d){var e=XMLParser.make(d),f=null,g=false,h=null,i=null,j={next:k,copy:m};function k(){var n=e.next();if(n.content=='<')g=true;else if(n.style=='xml-tagname'&&g===true)g=n.content.toLowerCase();else if(n.style=='xml-attname')h=n.content;else if(n.type=='xml-processing')for(var o=0;o<b.length;o++){if(b[o]==n.content){j.next=l(PHPParser,'?>');break;}}else if(n.style=='xml-attribute'&&n.content=='"php"'&&g=='script'&&h=='language')g='script/php';else if(n.content=='>'){if(g=='script/php')j.next=l(PHPParser,'</script>');else if(g=='script')j.next=l(JSParser,'</script');else if(g=='style')j.next=l(CSSParser,'</style');h=null;g=false;}return n;};function l(n,o){var p=e.indentation();if(n==PHPParser&&i)f=i(d);else f=n.make(d,p+indentUnit);return function(){if(d.lookAhead(o,false,false,true)){if(n==PHPParser)i=f.copy();f=null;j.next=k;return k();}var q=f.next(),r=q.value.lastIndexOf('<'),s=Math.min(q.value.length-r,o.length);if(r!=-1&&q.value.slice(r,r+s).toLowerCase()==o.slice(0,s)&&d.lookAhead(o.slice(s),false,false,true)){d.push(q.value.slice(r));q.value=q.value.slice(0,r);}if(q.indentation){var t=q.indentation;q.indentation=function(u){if(u=='</')return p;else return t(u);};}return q;};};function m(){var n=e.copy(),o=f&&f.copy(),p=j.next,q=g,r=h,s=i;return function(t){d=t;e=n(t);f=o&&o(t);i=s;j.next=p;g=q;h=r;return j;};};return j;};return{make:c,electricChars:'{}/:',configure:function(d){if(d.opening!=null)b=d.opening;}};})();