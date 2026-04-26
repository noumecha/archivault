// modules/documents/index.js
import { DocumentController } from './documents.controller.js';
import { ThemeController } from '../themes/themes.controllers.js';
import { CelluleController } from '../cellules/cellules.controllers.js';
import { TypeDocumentController } from '../typedocuments/typedocuments.controllers.js';
import { SousTypeDocumentController } from '../soustypedocuments/soustypedocuments.controllers.js';

$(function () {
  // init the controller for document
  DocumentController.init();
  // for more
  ThemeController.init();
  CelluleController.init();
  TypeDocumentController.init();
  SousTypeDocumentController.init();
});
