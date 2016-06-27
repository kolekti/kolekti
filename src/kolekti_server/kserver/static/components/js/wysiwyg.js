$(document).ready(function() {

    CKEDITOR.disableAutoInline = true;
    // CKEDitor Behavior
    // The "instanceCreated" event is fired for every editor instance created.
    CKEDITOR.on( 'instanceCreated', function ( event ) {
	var editor = event.editor,
	    element = editor.element;
	
	// Customize editors for headers and tag list.
	// These editors do not need features like smileys, templates, iframes etc.
	// Customize the editor configuration on "configLoaded" event,
	// which is fired after the configuration file loading and
	// execution. This makes it possible to change the
	// configuration before the editor initialization takes place.
	editor.on( 'configLoaded', function () {
	    
	    // Remove redundant plugins to make the editor simpler.
	    editor.config.removePlugins = 'colorbutton,find,flash,font,' +
		'forms,iframe,newpage,removeformat,' +
		'smiley,specialchar,stylescombo,templates';
	    
	    // Rearrange the toolbar layout.
	    editor.config.toolbarGroups = [
		{ name: 'editing', groups: [ 'basicstyles', 'links', 'image' ] },
		{ name: 'undo' },
		{ name: 'clipboard', groups: [ 'selection', 'clipboard' ] },
		{ name :"paragraph", groups :['list','blocks']},
		{ name: 'about' }
	    ];
	    
	    editor.config.removeButtons='Strike,Anchor,Styles,Specialchar,CreateDiv,SelectAll'
	} );
	editor.on('change', function() {
	    editor.ecorse_state = true
	});
	editor.on( 'blur', function () {
	    if (editor.ecorse_state) {
		
	    }
	});
    } );
    
    // collapse : initialisation CKEditor sur déroulé
    $('.collapseWysiwyg').on('shown.bs.collapse', function () {
	var editor, edid = $(this).find('.anaeditor').attr('id')
	if (CKEDITOR.instances[edid] == undefined)
	    editor = CKEDITOR.inline(edid,{startupFocus : true})
	else {
	    editor = CKEDITOR.instances[edid]
	    editor.focus()
	}
	editor.ecorse_state = false
    })

    // initialisation CKEditor dans modal edition topic

    $('.modal-topic-details').on('shown.bs.modal', function(e) {
	var editor, edid = $(e.target).find('.anaeditor').attr('id')
	var h = $(window).height() - 300;
	if (CKEDITOR.instances[edid] == undefined)
	    
	    editor = CKEDITOR.replace(edid,{startupFocus : true, height: h })
	else {
	    editor = CKEDITOR.instances[edid]
	    editor.focus()
	}
	editor.ecorse_state = false

    });
    
    $('.modal-topic-details').on('confirm.bs.modal', function(e) {
	console.log('wysiwig save')
	var release = $('.report').data('release'),
	    topic = $(e.target).closest('.topic'),
	    edid = $(topic).find('.anaeditor').attr('id'),
	    editor = CKEDITOR.instances[edid],
	    topicid = $(topic).attr('id'),
	    data = editor.getData()
	$.ajax({
	    url:"/elocus/report/analysis",
	    method:'POST',
	    data:$.param({
		'release': release,
		'topic' : topicid,
		'data':data
	    })
	}).done(function(data) {
	    if (data.status == 'ok') {
		editor.ecorse_state = false;
	    }
	}).fail(function(data) {
	});
    });
})
