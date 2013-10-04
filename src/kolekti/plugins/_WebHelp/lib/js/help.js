
var base_help;
var current_url;
var toc_topics=[];
var config={
    panelpadding:10,
    panelhandlerwidth:4,
    heightbase:6,
    offsetframe:8,
    panelvisible:true,
    panelwidth:200,
    panelslide:['']
}
var hfh;    


// GESTION DU TOPIC

// var startpage : intialized by the transformation in index.html header
function help_init() {
    if (window.parent.iframe) return;
    spvisible=config['panelvisible'];
    spcpos=config['panelwidth'];

    if (spvisible) {
 	show_sidepanel();
    } else {
	hide_sidepanel();
    }
	
    // initialize events for resize sidepanel
    var sp=document.getElementById('sphandle');
    sp.ondblclick=fold_sidepanel;
    sp.onmousedown=startmove_sidepanel;
    document.onmousemove=move_sidepanel;
    document.onmouseup=endmove_sidepanel;

    // inits the topic table
    toc_topics=get_topic_elements();

    // inits the iframe : loads the topic
    var url=window.location.href;
    
    // calculates the base url (without file part)
    var bh=url.split('/');
    bh.pop();
    base_help=bh.join('/')+'/';

    var module;
    if (url.lastIndexOf('?')==-1) {
	// url does not contains "?" : start with the start topic 
	module=startpage;
    } else {
	// url is formed like : index.php?id1234.html : loads topic id1234.html
	module=url.slice(url.lastIndexOf('?')+1);
    }

    // remove the trailing "#"
    module=module.replace('#','');

    // if module could not be calculated go to the start page
    if (module=="")
	module=startpage;
	
    // dérouler la table des matières

    // set height of table of contents (TOC), main body zone and sidepanel handle 

	hfh=config['heightbase'];
    var browserName=navigator.appName; 
    if (browserName=="Microsoft Internet Explorer") {
	elt=document.getElementById('header');
	if (elt) {
	    h=parseInt(elt.currentStyle.height.slice(0,-2));
	    hfh+=h;
	}
	elt=document.getElementById('breabcrumbs');
	if (elt) {
	    h=parseInt(elt.currentStyle.height.slice(0,-2));
	    hfh+=h;
	}
	elt=document.getElementById('context');
	if (elt) {
	    h=parseInt(elt.currentStyle.height.slice(0,-2));
	    hfh+=h;
	}
	elt=document.getElementById('footer');
	if (elt) {
	    h=parseInt(elt.currentStyle.height.slice(0,-2));
	    hfh+=h;
	}
	elt=document.getElementById('toolbar');
	if (elt) {
	    h=parseInt(elt.currentStyle.height.slice(0,-2));
	    hfh+=h;
	}
	window.onresize=adjust_blocks_size;
	adjust_blocks_size();
    }

    // load the start topic 

    topic(module);

    // loads the fulltext frame (for search result purpose)
    document.getElementById('searchresframe').src="js/texts.html";
    search_init();
    
    
}

var jumpsearch=false;
var nav_mode_histo=false;

// displays a topic from search results
function topic_search(topic) {
    jumpsearch=true;
    display_topic(topic);
    histo_add(topic);
}

// display a topic either from a link in topic / TOC
function topic(topic,local) {
    jumpsearch=false;
    display_topic(topic,local);
    histo_add(topic);
}


// loads a topic file in the iframe
function display_topic(topic,local) {
    //get the iframe
    iframe=document.getElementById('topicframe');

    // calculate the url with local id part if necessary : topic.html#here
    url=topic;
    if(local) {
	url=url+'#'+local;
    }

    // loads the iframe content
    iframe.src=base_help+url;

    // remind the url (for bookmark)
    current_url=base_help+"index.html?"+topic;

    // update the toc
    tocupdate(topic);

    // update navigation buttons (in prev/next mode)
    nav_update_buttons(topic); 
}





// TOC MANAGEMENT FUNCTIONS

// update the TOC when chaging the topic

function tocupdate(topic) {
    
    //var listTOC=document.getElementById('listToc');
    //var topics=listTOC.getElementsByTagName('li');
    var top;
    // loops on every topic in the TOC
    for (var i =0; i<toc_topics.length; i++) {
	top=toc_topics[i];
	if ((top.getAttribute('id').replace('tocmod', '')+'.html')==topic) {
	    // this is the current displayed topic : highlight it
	    // unfold ancestor sections if necessary
	    tocdisplay(top)
	    top.className="activetopic";
	} else {
	    // may this was the previous displayed topic: remove highlight
	    if (top.className=="activetopic") {
		top.className="seentopic"
	    }
	}
    }
}


// unfolds all sections that are ancestor of item
function tocdisplay(item) {
    c=item;
    while (c && c.getAttribute('id')!='listToc') {
	if (c.nodeName=='UL') {
	    id=c.getAttribute('id').substring(4);
	    fold_show(id);
	}
	c=c.parentNode;
    }
	
}


// TODO : give english name : warning called by onclick in generated content

// unfolds a section in the table of content
function fold_show(id) {
    document.getElementById("cond"+id).style.display="none";
    document.getElementById("comp"+id).style.display="inline";
    document.getElementById("belt"+id).style.display="block";
}

// folds a section in the table of content
function fold_hide(id) {

    document.getElementById("cond"+id).style.display="inline";
    document.getElementById("comp"+id).style.display="none";
    document.getElementById("belt"+id).style.display="none";
}

// END TOC MANAGEMENT FUNCTIONS



// SIDE PANEL FUNCTIONS

// update the height of sidebar, sidebar handle, body and footer when broowser window size changes
// For IEpurpose that cannot manage that with css
function adjust_blocks_size () {
    if (document.all) {
	var iframeElement = document.getElementById('topicframe');
	var sideElement   = document.getElementById('sidepanel');
	var sphandleElement   = document.getElementById('sphandle');

	if (window.document.compatMode &&
            window.document.compatMode != 'BackCompat') 
	{
	    sideElement.style.height = document.documentElement.clientHeight - hfh+ 'px';
	    sphandleElement.style.height = document.documentElement.clientHeight - hfh+ 'px';
	    iframeElement.style.height = document.documentElement.clientHeight - hfh+ 'px';
	}
	else {
	    sideElement.style.height = document.body.clientHeight - hfh+ 'px';
	    sphandleElement.style.height = document.body.clientHeight - hfh+ 'px';
	    iframeElement.style.height = document.body.clientHeight - hfh + 'px';
	}
    }
}

// GENERIC SHOW/HIDE FUNCTIONS
// used for search options... only
var visible={
    searchoptionscontent:false
}

// TODO : englishize
function fold(id) {
    if(visible[id]){
	document.getElementById(id).style.display="none";
	visible[id]=false;
    } else {
	document.getElementById(id).style.display="block";
	visible[id]=true;
    }
}


// SIDE PANEL REDUCE/EXPAND / FOLD/UNFOLD

// state function
var spvisible=true; // is it visible ?
var spmove=false;   // is it moving  ?
var spcpos;         // what was the last width ?

function stopevent(e) {
    if (e.stopPropagation) {
	e.stopPropagation();
	e.preventDefault();
    } else {
	e.cancelBubble = true;
	e.returnValue = false;	    
    }
}

// mouse down : starts moving sidepanel
function startmove_sidepanel(e) {
    if(!e) var e = window.event;
    stopevent(e);
    if (!spvisible) return;
    spmove=true;
    // if it was folded, unfold : 
    // !! not a good idea, could make it resize to a large dimension while mouse still at the border of the window
    // if (!spvisible)
    //    fold_sidepanel(e);
}

// mouse up : stops moving sidepanel
function endmove_sidepanel(e) {
    if (!spmove) return;
    if(!e) var e = window.event;
    stopevent(e);
    move_sidepanel(e);
    spmove=false;
}

// mouse move : updates position of panel 
function move_sidepanel(e) {
    if (!spmove) return;
    if(!e) var e = window.event;
    stopevent(e);
    spvisible=true;
    var ppos=e.clientX;
    if (ppos < 10) return;
    spcpos=ppos;
    document.getElementById("sidepanel").style.width=ppos-config['panelpadding'];
    document.getElementById("main").style.left=ppos+config['panelpadding'];
    setpanelslidingelements(ppos-config['panelpadding']);
}

// called when mouse moved from within the iframe (topic.js)
function iframe_move_sidepanel(offset) {
   if (!spmove) return;
    //var sp=document.getElementById("sidepanel").clientWidth+5;
    var ppos=spcpos+offset+config['offsetframe'];
    spcpos=ppos;
    document.getElementById("sidepanel").style.width=ppos-config['panelpadding'];
    document.getElementById("main").style.left=ppos+config['panelpadding'];
    setpanelslidingelements(ppos-config['panelpadding']);
}

// dblclick on handle : folds/unfolds the sidepanel
function fold_sidepanel(e) {
    if(!e) var e = window.event;
    stopevent(e);
    if (spvisible) {
	hide_sidepanel();
    } else {
	show_sidepanel();
    }
}

// folds the side panel
function hide_sidepanel() {
    document.getElementById("sidepanel").style.width=0;
    document.getElementById("main").style.left=0;
    setpanelslidingelements(0);
    spvisible=false;
    document.getElementById("fold_sidepanel").style.display='none';
    document.getElementById("unfold_sidepanel").style.display='inline';
    cmdulight();
}

// unfolds the side panel
function show_sidepanel() {
    document.getElementById("sidepanel").style.width=spcpos-config['panelpadding'];
    document.getElementById("main").style.left=spcpos+config['panelpadding'];
    setpanelslidingelements(spcpos+config['panelpadding']);
    spvisible=true;
    document.getElementById("fold_sidepanel").style.display='inline';
    document.getElementById("unfold_sidepanel").style.display='none';
    cmdulight();
 }


function setpanelslidingelements(offset) {
    var idx,id;
    for (idx in config['panelslide']) {
	id=config['panelslide'][idx];
	document.getElementById(id).style.left=offset+config['panelslideoffset'][idx];
    }
	
}

// END SIDEPANEL FUNCTIONS



// DIVERS

// display the toc in the sidepanel
function showtabtoc() {
    document.getElementById("toctab").className="activetab";
    document.getElementById("searchtab").className="passivetab";
    var alphaindextab = document.getElementById("alphaindextab");
    if(alphaindextab)
        alphaindextab.className="passivetab";
    showtoc();
    cmdulight();
}

function showtoc() {
    document.getElementById("toc").style.display="block";
    document.getElementById("search").style.display="none";
    var alphaindextab = document.getElementById("alphaindextab");
    if(alphaindextab)
        alphaindextab.style.display="none";
    show_sidepanel();
}

// display the toc in the sidepanel
function showtabalphaindex() {
    document.getElementById("toctab").className="passivetab";
    document.getElementById("searchtab").className="passivetab";
    document.getElementById("alphaindextab").className="activetab";
    showalphaindex();
    cmdulight();
}

function showalphaindex() {
    document.getElementById("toc").style.display="none";
    document.getElementById("search").style.display="none";
    document.getElementById("alphaindex").style.display="block";
    show_sidepanel();
}

// display the search results
function showtabsearch() {
    document.getElementById("toctab").className="passivetab";
    document.getElementById("searchtab").className="activetab";
    var alphaindextab = document.getElementById("alphaindextab");
    if(alphaindextab)
        alphaindextab.className="passivetab";
    showsearch();
    cmdulight();
}

function showsearch() {
    document.getElementById("search").style.display="block";
    document.getElementById("toc").style.display="none";
    var alphaindex = document.getElementById("alphaindex");
    if(alphaindex)
        alphaindex.style.display="none";
    document.getElementById("search_field_side").focus();
    show_sidepanel();
}

// search function 
// a_* functions are in search.js
function search() {
    // get the search field content
    words=document.getElementById("search_field").value;
    if (words=='') {
	words=document.getElementById("search_field_side").value;
    }
    if (words!='') {
	// remove previous highlight, if any
	a_unlight_topic();
	// do search
	pages=a_search(words);
	// show results
	showsearch();
    }
    return false;
}

// jumps to the start topic
function defaulttopic() {
    topic(startpage);
}

// removes highlght (search results
function cmdulight() {
    document.getElementById('tool_uhlight').style.display='none';
    document.getElementById('tool_uhlight2').style.display='none';
    a_unlight_topic();
}

// prints the current topic
function printtopic() {
    a_unlight_topic() 
    var w=get_topic_window();
    w.print();
}

// bookmarks the current topic
function bktopic() {
    var w=get_topic_window();
    var title="";
    var url="";
    if (window.sidebar) { // Mozilla Firefox Bookmark
	window.sidebar.addPanel(title, current_url,"");
    } else if (window.external) {
	window.external.AddFavorite( current_url, title);
    } else if(window.opera && window.print) { 
	// Opera Hotlist
	return true; 
    }
	
}


function get_topic_window() {
    return document.getElementById('topicframe').contentWindow;
}


//************************
// Navigation with history 
//************************

// Historic of seen topics
var histo=[];
var histosize=0;
var histocurrent=0;

// Displays a topic (form breadcrumbs)
function h_topic(t) {
    histocurrent=t;
    display_topic(histo[t]);
    histo_update_buttons();
}

// Displays the following topic in history
function h_next_topic() {
    if (histocurrent < histosize) {
	display_topic(histo[++histocurrent]);
    }
    histo_update_buttons();
}

// Displays the previous topic in history
function h_prev_topic() {
    if (histocurrent > 1) {
	display_topic(histo[--histocurrent]);
    }
    histo_update_buttons();
}

// Displays the first topic in history
function h_first_topic() {
    display_topic(histo[0]);
    histo_update_buttons();
}

// Displays the last topic in history
function h_last_topic() {
    display_topic(histo[histosize]);
    histo_update_buttons();
}

// adds the current topic to history
function histo_add(topic) {
    if (histo[histocurrent]==topic)
	return;
    histo[++histocurrent]=topic;
    histosize=histocurrent;
    histo_update_buttons();
}

// update the historic buttons
function histo_update_buttons() {
   if (histocurrent==histosize) {
      document.getElementById('tool_nav_h_n').style.display="none";
      document.getElementById('tool_nav_h_n_dis').style.display="inline";
      document.getElementById('tool_nav_h_l').style.display="none";
      document.getElementById('tool_nav_h_l_dis').style.display="inline";
   } else {
      document.getElementById('tool_nav_h_n').style.display="inline";
      document.getElementById('tool_nav_h_n_dis').style.display="none";
      document.getElementById('tool_nav_h_l').style.display="inline";
      document.getElementById('tool_nav_h_l_dis').style.display="none";
   }
   if (histocurrent==1) {
      document.getElementById('tool_nav_h_p').style.display="none";
      document.getElementById('tool_nav_h_p_dis').style.display="inline";
      document.getElementById('tool_nav_h_f').style.display="none";
      document.getElementById('tool_nav_h_f_dis').style.display="inline";
   } else {
      document.getElementById('tool_nav_h_p').style.display="inline";
      document.getElementById('tool_nav_h_p_dis').style.display="none";
      document.getElementById('tool_nav_h_f').style.display="inline";
      document.getElementById('tool_nav_h_f_dis').style.display="none";
   }
   breadcrumbs();
}

// displays the breadcrumbs : liste of preceding/following topics in history
function breadcrumbs() {
    var start,end,c,sp,sep,sept;
    var bc;
    bc=document.getElementById('breadcrumbs');
    while (bc.firstChild)
	bc.removeChild(bc.firstChild);
    if (histocurrent==histosize) {
	start=histocurrent-3;
	end=histocurrent;
    } else {
	start=histocurrent-2;
	end=histocurrent+1;
    }
    if (start < 0) 
	start=0;
    for (c=start;c<=end;c++) {
	sp=document.createElement("span");	
	sept=document.createTextNode(topic_title(histo[c]));
	sp.appendChild(sept);
	bc.appendChild(sp);
	if (c!=end) {
	    sep=document.createElement("span");
	    sept=document.createTextNode(" >> ");
	    sep.appendChild(sept);
	    bc.appendChild(sep);
	}
	if (c==histocurrent) {
	    sp.setAttribute('class','ctopic topic');
	} else {
	    sp.setAttribute('class','topic');
	}
	sp.setAttribute('onclick','h_topic('+c+')');
    }
}

function topic_title(t) {
    var top;
    for (var i =0; i<toc_topics.length; i++) {
	top=toc_topics[i];
	if ((top.getAttribute('id').replace('tocmod', '')+'.html')==t) {
	    return top.firstChild.nodeValue;
	}
    }
    return '';
}


//**************************
// Navigation with structure
//**************************

// updates buttons of prev/next navigation

function nav_update_buttons(topic) {
    var top;
    context(topic);
    for (var i =0; i<toc_topics.length; i++) {
	top=toc_topics[i];
	if ((top.getAttribute('id').replace('tocmod', '')+'.html')==topic) {
            if(i==0) {
               document.getElementById('tool_nav_p').style.display="none";
               document.getElementById('tool_nav_p_dis').style.display="inline";
               document.getElementById('tool_nav_f').style.display="none";
               document.getElementById('tool_nav_f_dis').style.display="inline";
            } else {
               document.getElementById('tool_nav_p').style.display="inline";
               document.getElementById('tool_nav_p_dis').style.display="none";
               document.getElementById('tool_nav_f').style.display="inline";
               document.getElementById('tool_nav_f_dis').style.display="none";
            }
            if (i==toc_topics.length-1) {
               document.getElementById('tool_nav_n').style.display="none";
               document.getElementById('tool_nav_n_dis').style.display="inline";
               document.getElementById('tool_nav_l').style.display="none";
               document.getElementById('tool_nav_l_dis').style.display="inline";
            } else {
               document.getElementById('tool_nav_n').style.display="inline";
               document.getElementById('tool_nav_n_dis').style.display="none";
               document.getElementById('tool_nav_l').style.display="inline";
               document.getElementById('tool_nav_l_dis').style.display="none";
            }
            return;
        }
    }
}


// builds the list of topics ordered according to the TOC
function get_topic_elements() {
    var res=[];
    var listTOC=document.getElementById('listToc');
    var topics=listTOC.getElementsByTagName('li');
    var top;
    for (var i =0; i<topics.length; i++) {
	top=topics.item(i);
	//if (top.hasAttribute('id')) {
	if (top.getAttribute('id')) {
	    res.push(top);
	}
    }
    return res;
}

// searchs in the table of content the previous or next topic
function getnextprev(topic,next) {    
    var top;
    for (var i =0; i<toc_topics.length; i++) {
	top=toc_topics[i];
	if ((top.getAttribute('id').replace('tocmod', '')+'.html')==topic) {
	    if (next && i==toc_topics.length-1) return null;
	    if (!next && i==0) return null;
	    if (next) return (toc_topics[i+1].getAttribute('id').replace('tocmod', '')+'.html');
	    if (!next) return (toc_topics[i-1].getAttribute('id').replace('tocmod', '')+'.html');
	}
    }
}

// jumps to the next topic
function next_topic() {
    var ntop=getnextprev(histo[histocurrent],true);
    if (ntop) topic(ntop);
}

// displays the previous topic
function prev_topic() {
    var ntop=getnextprev(histo[histocurrent],false);
    if (ntop) topic(ntop);
}

// displays the first topic
function first_topic() {
   var ntop=toc_topics[0].getAttribute('id').replace('tocmod', '')+'.html';
   if (ntop) topic(ntop);
}

// displays the last topic
function last_topic() {
   var ntop=toc_topics[toc_topics.length - 1].getAttribute('id').replace('tocmod', '')+'.html';
   if (ntop) topic(ntop);
}

function context(topic) {
    var start,end,c,sp,sep,sept;
    var bc,top;
    bc=document.getElementById('context');
    while (bc.firstChild)
	bc.removeChild(bc.firstChild);

    for (var i =0; i<toc_topics.length; i++) {
	top=toc_topics[i];
	if ((top.getAttribute('id').replace('tocmod', '')+'.html')==topic) {
	    c=top;
	}
    }
    while (c && c.getAttribute('id')!='listToc') {
	if (c.nodeName=='LI') {
	    var anc=c.getElementsByTagName('A').item(0);
	    sp=document.createElement("span");
	    if (anc.firstChild)
	    {
		sept=document.createTextNode(anc.firstChild.nodeValue);
	    } else {
		sept=document.createTextNode("");
	    }
	    sp.appendChild(sept);
	    bc.insertBefore(sp,bc.firstChild);
	    
	    if (c.getAttribute('id') && c.getAttribute('id').replace('tocmod', '')+'.html'==topic) {
		sp.setAttribute('class','ctopic topic');
	    } else {
		sp.setAttribute('onclick',anc.getAttribute('onclick'));
		sp.setAttribute('class','topic');
		sep=document.createElement("span");
		sept=document.createTextNode(" > ");
		sp.appendChild(sept);
	    }
	}
	c=c.parentNode;
    }

}



// index menu
var lastindexmenu=null;
function indexmenutopic(t) {
    topic(t);
    indexmenuhide();
}

function indexmenu(m) {
    var cmenu=lastindexmenu;
    if (lastindexmenu) {	
	indexmenuhide();
    }
    if(cmenu==null || cmenu.getAttribute('id') != 'im'+m)
    {
	lastindexmenu=document.getElementById('im'+m);
	lastindexmenu.style.display="block";
    }
    
}

function indexmenuhide() {
    if (lastindexmenu)
	lastindexmenu.style.display="none";
    lastindexmenu=null;
}
    