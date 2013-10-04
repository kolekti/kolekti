var charsin ='àâäéèêëïîôöùûç';
var charsout='aaaeeeeiioouuc';
var charexcl='!#%&\',-/:;=>@_`{}~';
var charescxcl='()*+.?[\\]$^|';
var nbsnippets=1;

var IE=false;
if(navigator.userAgent.indexOf("MSIE") != -1)
    IE=true;

var do_highlight=true;
var lastsearchedwords=[];

var options={
    mot_entier:true,
    multi_ou:true
}

function search_init() {
  if (options.multi_ou) {
     document.getElementById('optTM').checked=false;
     document.getElementById('opt1M').checked=true;
  } else {
     document.getElementById('optTM').checked=true;
     document.getElementById('opt1M').checked=false;
  }
  if (options.mot_entier) {
     document.getElementById('optMC').checked=true;
     document.getElementById('optMD').checked=false;
  } else {
     document.getElementById('optMC').checked=false;
     document.getElementById('optMD').checked=true;
  }
}


function a_opt() {
    var restart=false;
    if (options.multi_ou && document.getElementById('optTM').checked) {
	options.multi_ou=false;
	restart=true;
    }
    if (!options.multi_ou && document.getElementById('opt1M').checked) {
	options.multi_ou=true;
	restart=true;
    }
    if (!options.mot_entier && document.getElementById('optMC').checked) {
	options.mot_entier=true;
	restart=true;
    }
    if (options.mot_entier && document.getElementById('optMD').checked) {
	options.mot_entier=false;
	restart=true;
    }
    if (restart) {
	words=document.getElementById("search_field").value;
	if (words=="")
	    words=document.getElementById("search_field_side").value;
	if (words!="") {
	    pages=a_search(words);
	    showsearch();
	}
    }
}

function chchr(str) {
    var re=new RegExp('');
    var chr=str;
    var cin;
    var cout;
    var i;
    for (i=0; i<charsin.length; i++) {
	cin=charsin.substr(i,1);
	cout=charsout.substr(i,1);
	re.compile(cin,"g");
	chr=chr.replace(re,cout);
    }
    for (i=0; i<charexcl.length; i++) {
	cin=charexcl.substr(i,1);
	re.compile(cin,"g");
	chr=chr.replace(re,'');
    }
    for (i=0; i<charescxcl.length; i++) {
	cin=charescxcl.substr(i,1);
	re.compile("\\"+cin,"g");
	chr=chr.replace(re,'');
   }
    return chr;
}

function chchr2(str) {
    var re=new RegExp('');
    var chr=str;
    var cin;
    var cout;
    var i;
    for (i=0; i<charsin.length; i++) {
	cin=charsin.substr(i,1);
	cout=charsout.substr(i,1);
	re.compile(cin,"g");
	chr=chr.replace(re,cout);
    }
    for (i=0; i<charexcl.length; i++) {
	cin=charexcl.substr(i,1);
	re.compile(cin,"g");
	chr=chr.replace(re,' ');
    }
    for (i=0; i<charescxcl.length; i++) {
	cin=charescxcl.substr(i,1);
	re.compile("\\"+cin,"g");
	chr=chr.replace(re,' ');
   }
    return chr;
}

function lemmatise(words){
    var res=[]
    var lc=words.toLowerCase()
    lc=lc.replace(/ +/g," ");
    lc=lc.replace(/^ /,"");
    lc=lc.replace(/ $/,"");

    var nb;
    lc=chchr2(lc);
    if (lc.substr(0,1)=='"') {
	nb=lc.substr(2).search('"');
	if (nb==-1) return [];
        res.push(lc.substr(0,nb+3));
        lc=lc.substr(nb+4);
    }
    var nb=lc.search(' ');
    while (nb!=-1) {
	if(lc.substr(0,1)=='"'){
	    nb=lc.substr(1).search('"');
	    if (nb==-1) return [];
	    nb+=2;
	}
        res.push(lc.substr(0,nb));
        lc=lc.substr(nb+1);
        nb=lc.search(' ');
    }
    res.push(lc);
    return res
        
}

function a_search(words) {

    var restot={};
    var rescount={};
    var restab={};
    var wordtab=lemmatise(words);
    var i, res;
    lastsearchedwords=[];
    for (i in wordtab) {
	if (wordtab[i]=="") continue;
	if (wordtab[i].substr(0,1)=='"') {
	    var w=wordtab[i].substr(1,wordtab[i].length-2);
	    restab=a_search_fulltext(w);
	    lastsearchedwords.push(w);
	} else {
	    restab=a_searchword(wordtab[i]);
	    lastsearchedwords.push(wordtab[i]);
	}
	for (res in restab) {
	    if (restot[res]) {
		restot[res]+=restab[res];
		rescount[res]+=1;
	    }  else {
		restot[res]=restab[res];
		rescount[res]=1;
	    }
	}
    }
    var rescore={};
    for (res in restot) {
  	rescore[res]=Math.floor((restot[res]/wordcount[res])*1000);
    }
    var ressort=sort_score(rescore);

    var htmlbuf='';
    for (r in ressort) {
        res=ressort[r];
	if (options['multi_ou'] || rescount[res]==wordtab.length) {
            score=rescore[res];
	    htmlbuf=htmlbuf+'<a onclick="topic_search(\''+res+'.html\')" title="'+modcodes[res+".html"]+'" href="#">';
            htmlbuf=htmlbuf+'<div class="resitem" id="restop'+res+'">';
            htmlbuf=htmlbuf+'<p class="reslink">';
            htmlbuf=htmlbuf+modcodes[res+".html"];
	    htmlbuf=htmlbuf+'</p>';
            htmlbuf=htmlbuf+'<p class="resscore">'+label_score+score+"</p>";
            //htmlbuf=htmlbuf+show_search_words(res,false);
            htmlbuf=htmlbuf+'</div>';
            htmlbuf=htmlbuf+'</a>';
	}
    }
    if (htmlbuf=='') {
	document.getElementById('nores').style.display='block';
	document.getElementById('searchres').style.display='none';
	document.getElementById('searchres').innerHTML='';
    } else {
	document.getElementById('nores').style.display='none';
	document.getElementById('searchres').style.display='block';       
	document.getElementById('searchres').innerHTML=htmlbuf;
    }
    delayed_highlight();
}

function delayed_highlight() {
  var resdiv=document.getElementById('searchres');
  var restopics=resdiv.getElementsByTagName('DIV');
  var i;
  var topicelt;
  do_highlight=true;
  a_highlight_topic();
  for (i=0; i<restopics.length; i++) {
     topicelt=restopics[i];
     topicid=topicelt.getAttribute('id').substr(6);
     setTimeout("highlight_search_results('"+topicid+"')", 0);
     //topicelt.innerHTML+=show_search_words(topicid,false);
  }
}

function highlight_search_results(topicid) {    
  var topicelt=document.getElementById('restop'+topicid);
  topicelt.innerHTML+=show_search_words(topicid,false);
}

function show_search_words(topic,full) {
    var sif=document.getElementById('searchresframe').contentWindow.document;
    var topicdiv=sif.getElementById(topic+'.html');
    if (!topicdiv) return;
    var strings=extraits(topicdiv);
    var res="";
    for (s in strings) {
	if (full || s <= (nbsnippets - 1)) {	
	    res=res+'<p class="strres">... '+strings[s]+'...</p>';
	}
    }
    
    if (!full && s > (nbsnippets - 1)) {
	res=res+"<p class='more' onmouseover='show_all_words(\""+topic+"\")' onmouseout='hide_all_words()'>"+label_moreres+"</p>";
    }
    return res;
}

function show_all_words(topic) {
    document.getElementById('allwordsdiv').innerHTML=show_search_words(topic,true);
    document.getElementById('allwordsdiv').style.display="block";
}
function hide_all_words(topic,words) {
    document.getElementById('allwordsdiv').style.display="none";
}

function search_get_text(doc,topic) {
    var topicdiv=doc.getElementById(topic+'.html');
    text=topicdiv.innerText || topicdiv.textContent;
    return chchr2(text);
}


function sort_score(obj) {
  sor=[];
  for(i in obj) {
    v=obj[i];
    for(j=0;j<sor.length && v<obj[sor[j]];j++);
    end=sor.slice(j,sor.length);
    begin=sor.slice(0,j);
    begin.push(i);
    sor=begin.concat(end)    
  }
  return sor;
}


function a_search_fulltext(word){ 
    var res={};
    var re=new RegExp(word);
    var sif=document.getElementById('searchresframe').contentWindow.document;
    var topics=sif.getElementsByTagName('DIV');
    var segs=[]
    for (i=0;i<topics.length;i++) {
	text=topics[i].innerText || topics[i].textContent;
	text=chchr2(text.toLowerCase());
	segs=text.split(re);
	if (segs.length > 1) {
	    res[topics[i].getAttribute('id').replace(".html","")]=segs.length-1;
	}
    }
    return res;
}


function a_searchword(word) {
    var cind=1;
    var clett=0;
    var stop=false;
    var wordlen=word.length;
    var nextcand=0;
    var letterfound;
    var curlet;
    var result={};
    while (clett < wordlen && !stop) {
	curlet=word.substr(clett,1);
	nextcand=cind;
	letterfound=false;
	while(nextcand!=0 && !letterfound){
	    if (curlet==nodes[nextcand]) {
		letterfound=true;
	    } else {
		nextcand=nexts[nextcand];
	    }
	}
	
	if (letterfound) {
	    clett++;
	    cind=child[nextcand];
	} else {
	    cind=0;
	}
	stop=(cind==0);
    }

    if (clett==wordlen) {
	a_concatres(result,terms[nextcand]);
	if (!options['mot_entier']) {
	    s=a_expandsearch(nextcand);
	    a_concatres(result,s);
	}
    }

    return result;
}

function a_concatres(resobj,tabres) {
    for (res in tabres) {
	
	if (resobj[res]) {
	    resobj[res]+=tabres[res];
	} else {
	    resobj[res]=tabres[res];
	}
    }
}


function a_expandsearch(cind) {
    var res=[];
    var cnode=child[cind];
    while (cnode) {
	a_concatres(res,terms[cnode])

	//res.concat(a_expandsearch(cnode));
	a_concatres(res,a_expandsearch(cnode));
	cnode=nexts[cnode];
    }
    return res;
}


function a_highlight_topic() {
    if (do_highlight && lastsearchedwords.length != 0){
	document.getElementById('tool_uhlight').style.display='inline';
	document.getElementById('tool_uhlight2').style.display='inline';
	var topicw=get_topic_window();
	var topicbody=topicw.document.body;
	highlight(topicbody);
	if (jumpsearch) {
	    topicw.location.href+="#firstsearchresult"; 
	}	    
    }
}

function a_unlight_topic() {
    var topicelt=document.getElementById('topicframe').contentWindow.document;
    var topicbody=topicelt.body;
    if (topicbody)
	uhighlight(topicbody);
      
}

