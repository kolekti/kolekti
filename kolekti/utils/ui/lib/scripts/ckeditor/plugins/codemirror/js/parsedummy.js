﻿var DummyParser=Editor.Parser=(function(){function b(d){while(!d.endOfLine())d.next();return 'text';};function c(d){function e(h){return function(){return h;};};d=tokenizer(d,b);var f=0,g={next:function(){var h=d.next();if(h.type=='whitespace')if(h.value=='\n')h.indentation=e(f);else f=h.value.length;return h;},copy:function(){var h=f;return function(i){f=h;d=tokenizer(i,b);return g;};}};return g;};return{make:c};})();
