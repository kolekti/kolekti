var first_in_topic;

function highlight(elt) {
    first_in_topic=true;
    parcours(elt,highlight_text);
}

function uhighlight(elt) {
   var splist=elt.getElementsByTagName('SPAN');
   var i,span;
   for (i=0; i< splist.length;i++) {
     span=splist[i];
     if (span.getAttribute('class')=='hl' || span.className=="hl") {
	 
       txt=span.firstChild;
       span.parentNode.replaceChild(txt,span);
     }
   }
}

function parcours (elt,func) {
    var c=elt.firstChild;
    var next;
    while (c) {
	next=c.nextSibling;
	if (c.nodeType==3) {
	    func(c);
	}
	if (c.nodeType==1) {
	    parcours(c,func);
	}
	c=next;
    }	
}

function highlight_text(elt) {
    var textl=chchr2(elt.nodeValue.toLowerCase());
    var texto=elt.nodeValue;
    var re= new RegExp('');
    var delend='';
    var segs;
    var len;
    var indices=[];
    var re= new RegExp();
    if (options.mot_entier) {
	delend='\\b';
    }
    for (wsi in lastsearchedwords) {
	re.compile('\\b'+lastsearchedwords[wsi]+delend);
	segs=textl.split(re);
	len=0;
	for (s=0; s<segs.length-1; s++) {
	    len+=segs[s].length
	    indices[indices.length]=[len,lastsearchedwords[wsi].length];
	    len+=lastsearchedwords[wsi].length;
	}
    }
    if (indices.length==0)
	return;

    indices.sort(sortIndices);
    var cc=0;
    var ext='';
    for (i in indices) {
	ext+=texto.substring(cc,indices[i][0]);
	if (first_in_topic) {
	    ext+="<a class='firstsearchresult' id='firstsearchresult' name='firstsearchresult'>";
	}
	ext+="<span class='hl'>";
	ext+=texto.substr(indices[i][0],indices[i][1]);
	ext+="</span>";
	if (first_in_topic) {
	    first_in_topic=false;
	    ext+="</a>";
	}
	cc=indices[i][0]+indices[i][1];
    }
    ext+=texto.substr(cc);
    
    span=elt.ownerDocument.createElement('SPAN');
    span.innerHTML=ext;
    elt.parentNode.replaceChild(span,elt);
}

var hllimit=50;

function extraits(elt) {
    var t=elt.firstChild;
    var textl='';
    var texto='';
    while(t) {
	textl+=chchr2(t.nodeValue.toLowerCase());
	texto+=t.nodeValue;
	t=t.nextSibling;
    }
    var delend='';
    var segs;
    var len;
    var indices=[];
    var re= new RegExp();
    if (options.mot_entier) {
	delend='\\b';
    }
    for (wsi in lastsearchedwords) {
	re.compile('\\b'+lastsearchedwords[wsi]+delend);
	segs=textl.split(re);
	len=0;
	for (s=0; s<segs.length-1; s++) {
	    len+=segs[s].length
	    indices[indices.length]=[len,lastsearchedwords[wsi].length];
	    len+=lastsearchedwords[wsi].length;
	}
    }
    indices.sort(sortIndices);
    var curst=0;
    var curend=0;
    var restab=[];
    var ext;
    for (i=0; i<indices.length; i++) {
	if (indices[i][0]-hllimit <0) {
	    ext=texto.substr(0,indices[i][0]);
	} else {
	    ext=texto.substr(indices[i][0]-hllimit,hllimit);
	}
	ext+="<span class='hl'>";
	ext+=texto.substr(indices[i][0],indices[i][1]);
	ext+="</span>";
	while (i<(indices.length-1) && indices[i+1][0]-indices[i][0]<hllimit) {
	    ext+=texto.substring(indices[i][0]+indices[i][1], indices[i+1][0]);
	    ext+="<span class='hl'>";
	    ext+=texto.substr(indices[i+1][0],indices[i+1][1]);
	    ext+="</span>";
	    i++;
	}
	if (indices[i][0]+indices[i][1]+hllimit > texto.length)
	    ext+=texto.substr(indices[i][0]+indices[i][1],texto.length-(indices[i][0]+indices[i][1]+1));
	else
	    ext+=texto.substr(indices[i][0]+indices[i][1],hllimit);
	ext=ext.replace(/^[^\s]*\s+/,'');
	ext=ext.replace(/\s+[^\s]*$/,'');
	restab[restab.length]=ext;
    }
    return restab;
}

function sortIndices(a,b)
{
  return a[0] - b[0];
}
