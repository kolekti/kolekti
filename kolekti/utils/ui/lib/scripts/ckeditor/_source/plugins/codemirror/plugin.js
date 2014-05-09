    /**
    * @fileOverview The "codemirror" plugin. It's indented to enhance the
    *  "sourcearea" editing mode, which displays the xhtml source code with
    *  syntax highlight and line numbers.
    * @see http://marijn.haverbeke.nl/codemirror/ for CodeMirror editor which this
    *  plugin is using.
    */

    CKEDITOR.plugins.add( 'codemirror', {
       requires : [ 'sourcearea' ],
       /**
        * This's a command-less plugin, auto loaded as soon as switch to 'source' mode
        * and 'textarea' plugin is activeated.
        * @param {Object} editor
        */

       init : function( editor ) {

          function notifyChange() {
            editor.fire('change');
            editor.textarea.setValue( editor.kcm.getCode() );
          }

          var thisPath = this.path;
          CKEDITOR.scriptLoader.load( thisPath + '/js/codemirror.js', function( success ){
             if ( success )
             editor.on( 'mode', function() {
                   if ( editor.mode == 'source' ) {
                      var sourceAreaElement = editor.textarea,
                         holderElement = sourceAreaElement.getParent();
                      var holderHeight = holderElement.$.clientHeight + 'px';
                      /* http://codemirror.net/manual.html */
                      var codemirrorInit =
                      CodeMirror.fromTextArea(
                         sourceAreaElement.$, {
                            parserfile: ['parsexml.js'],
                            stylesheet: [thisPath + 'css/xmlcolors.css'],
                            // Adapt to holder height.
                            height: holderHeight,
                            path: thisPath + 'js/',
                            passDelay: 300,
                            passTime: 35,
                            continuousScanning: 1000, /* Numbers lower than this suck megabytes of memory very quickly out of firefox */
                            lineNumbers: false,
                            textWrapping: false,
                            enterMode: 'flat',
                            onChange: notifyChange
                         }
                      );
                      editor.kcm=codemirrorInit;
                          // Commit source data back into 'source' mode.
                          editor.on( 'beforeCommandExec', function( ev ){
                             // Listen to this event once.
                             ev.removeListener();
                             sourceAreaElement.setValue( codemirrorInit.getCode() );
                             editor.fire( 'dataReady' );
                             /*editor._.modes[ editor.mode ].loadData(
                                codemirror.getCode() );*/
                          } );

                          CKEDITOR.plugins.mirrorSnapshotCmd = {
                             exec : function( editor ) {
                                if ( editor.mode == 'source' ) {
                                   sourceAreaElement.setValue( codemirrorInit.getCode() );
                                   editor.fire( 'dataReady' );
                                }
                             }
                          };
                          editor.addCommand( 'mirrorSnapshot', CKEDITOR.plugins.mirrorSnapshotCmd );
                          /* editor.execCommand('mirrorSnapshot'); */
                   }

             } );
          } );

       }

    });
