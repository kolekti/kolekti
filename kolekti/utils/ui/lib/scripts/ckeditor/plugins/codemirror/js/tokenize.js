﻿function tokenizer(b,c){function d(f){return f!='\n'&&/^[\s\u00a0]*$/.test(f);};var e={state:c,take:function(f){if(typeof f=='string')f={style:f,type:f};f.content=(f.content||'')+b.get();if(!/\n$/.test(f.content))b.nextWhile(d);f.value=f.content+b.get();return f;},next:function(){if(!b.more())throw StopIteration;var f;if(b.equals('\n')){b.next();return this.take('whitespace');}if(b.applies(d))f='whitespace';else while(!f)f=this.state(b,function(g){e.state=g;});return this.take(f);}};return e;};