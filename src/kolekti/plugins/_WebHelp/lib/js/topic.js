/*
document.onload=function() {
if (!parent.iframe){
    var s=window.location.href.split('/')
    var topic=s[s.length-1];
    s.pop();
    var rad=s.join('/')+'/'
    window.location.href=rad+'index.html?'+topic;
}
}
*/
function inittopic() {
    var w=this.parent;
    if (!w.iframe){
	var s=window.location.href.split('/')
	var topic=s[s.length-1];
	s.pop();
	var rad=s.join('/')+'/'
	    window.location.href=rad+'index.html?'+topic;
    }    
    document.onmousemove=move_sidepanel;
    document.onmouseup=endmove_sidepanel;
    w.a_highlight_topic();
}

function topic(ref,local) {
    if (ref=="")return;
    var w=this.parent;
    var blocal;
    if(local) blocal='true';
    else blocal='false';
    var f="w.topic('"+ref+".html',"+blocal+")";
    setTimeout(f,50);
    //w.topic(ref+'.html',local);
    document.onmousemove=move_sidepanel;
    document.onmouseup=endmove_sidepanel;
}

function endmove_sidepanel(e) {
    if(!e) var e = window.event;
    if (!w.spmove) return;
    move_sidepanel(e);
    w.spmove=false;
}

function move_sidepanel(e) {
    if(!e) var e = window.event;
    if (!w.spmove) return;
    var pos=e.clientX;
    w.iframe_move_sidepanel(pos);
}
var w=this.parent;