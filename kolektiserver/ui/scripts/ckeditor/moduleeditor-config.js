
/* Remove bad indent from CkEditor for block tags */
CKEDITOR.on('instanceReady', function( ev ) {
   ev.editor.dataProcessor.writer.indentationChars = '  ';
   var allrulestags = {}
   for(var tag in CKEDITOR.dtd.$tableContent) {
      if(!allrulestags[tag])
         allrulestags[tag] = CKEDITOR.dtd.$tableContent[tag];
   }
   for(var tag in CKEDITOR.dtd.$listItem) {
      if(!allrulestags[tag])
         allrulestags[tag] = CKEDITOR.dtd.$listItem[tag];
   }
   for(var tag in CKEDITOR.dtd.$block) {
      if(!allrulestags[tag])
         allrulestags[tag] = CKEDITOR.dtd.$block[tag];
   }

   for(var tag in allrulestags) {
       ev.editor.dataProcessor.writer.setRules(tag, {
          indent : true,
          breakBeforeOpen : true,
          breakAfterOpen : false,
          breakBeforeClose : false,
          breakAfterClose : true
       });
   }
});


CKEDITOR.editorConfig = function( config )
{
    config.contentsCss = [CKEDITOR.basePath+'contents.css'];
    config.language = kolekti.locale;

    config.toolbar = 'UPToolbar';

    config.toolbar_UPToolbar =
    [
        ['Preview', 'Source'],
        ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Scayt'],
        ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
        ['Image','Flash','Table','HorizontalRule','SpecialChar'],
        '/',
        ['Format','Conditions'],
        ['Bold','Italic','Strike'],
        ['NumberedList','BulletedList','-','Outdent','Indent'],
        ['Link','Unlink','Anchor'],
        ['Maximize','-','About']
    ];

    config.filebrowserBrowseUrl = '/projects/'+kolekti.project+'/modules';
    config.filebrowserUploadUrl = '/projects/'+kolekti.project+'/modules';
    config.filebrowserImageBrowseUrl = '/projects/'+kolekti.project+'/medias';
    config.filebrowserImageUploadUrl = '/projects/'+kolekti.project+'/medias';
    config.filebrowserFlashBrowseUrl = '/projects/'+kolekti.project+'/medias';
    config.filebrowserFlashUploadUrl = '/projects/'+kolekti.project+'/medias';
    config.filebrowserImageWindowWidth = '60%';
    config.filebrowserImageWindowHeight = '60%';

    config.resize_minWidth = 450;
    config.height = '100%';
    config.width = 'auto';
    config.resize_enabled=false;
    config.fullPage = true;
    config.entities = false;
    config.toolbarCanCollapse = false;

    config.extraPlugins = 'codemirror,onchange';
//    config.extraPlugins = 'kolekti';
};


