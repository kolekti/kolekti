﻿(function(){var a={canUndo:false,exec:function(c){var d=c.document.createElement('hr'),e=new CKEDITOR.dom.range(c.document);c.insertElement(d);e.moveToPosition(d,CKEDITOR.POSITION_AFTER_END);var f=d.getNext();if(!f||f.type==CKEDITOR.NODE_ELEMENT&&!f.isEditable())e.fixBlock(true,c.config.enterMode==CKEDITOR.ENTER_DIV?'div':'p');e.select();}},b='horizontalrule';CKEDITOR.plugins.add(b,{init:function(c){c.addCommand(b,a);c.ui.addButton('HorizontalRule',{label:c.lang.horizontalrule,command:b});}});})();