'''
Created on Jun 21, 2011

@author: tpmaxwel
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
from HWShowGraphicsView import *
from TouchscreenClient import *
showButtonsDraggable = True

#class DraggableTable(QTableWidget):
#
#    drop_event_signal = SIGNAL('drop_event')
#    
#    def __init__(self, rows,cols, parent=None):
#        super(DraggableTable, self).__init__( rows, cols, parent )
#        self.currentLocation = None 
#        self.setAcceptDrops(True)
#        self.setSortingEnabled( False )
#        self.setDragDropMode ( QAbstractItemView.DragDrop )
#        self.setDefaultDropAction( Qt.MoveAction )
#        self.setDragDropOverwriteMode ( True )
#        self.setDropIndicatorShown (True )
#        self.setDragEnabled ( True )
#        self.dragThreshold = 20
#        
#    def mousePressEvent ( self, event ):
#        self.currentLocation = event.globalPos() 
##        print ' mousePressEvent: loc = ', str(self.currentLocation)
#
#    def mouseReleaseEvent ( self, event ):
#        self.currentLocation = None 
##        print ' mouseReleaseEvent '
#        
#    def mouseMoveEvent ( self, event ):
#        if self.currentLocation:
#            location = event.globalPos()
#            dragDistance = location - self.currentLocation
#            if abs( dragDistance.x() ) > self.dragThreshold:
#                dx = -1 if dragDistance.x() < 0 else 1
#                hBar = self.horizontalScrollBar()
#                hBar.setValue( hBar.value() + dx ) 
#                self.currentLocation.setX ( location.x() )
#            if abs( dragDistance.y() ) > self.dragThreshold: 
#                dy = -1 if dragDistance.y() < 0 else 1          
#                vBar = self.verticalScrollBar() 
#                vBar.setValue( vBar.value() + dy ) 
#                self.currentLocation.setY ( location.y() )      
#
#    def getGridPosition( self, x, y ):
#        vBar = self.verticalScrollBar() 
#        hBar = self.horizontalScrollBar()
#        row = y / GridSpacing[0] + vBar.value()
#        col = x / GridSpacing[1] + hBar.value()
#        if col >= gridCols: col = gridCols - 1
#        if row >= gridRows: row = gridRows - 1
#        return ( row, col )
#    
#    def dragEnterEvent( self, event ):
#        if event.mimeData().hasFormat("text/plain"): 
#            event.acceptProposedAction()
#
#    def dragMoveEvent ( self, event ):
#        if event.mimeData().hasFormat("text/plain"): 
#            event.acceptProposedAction()
#
#    def dropEvent( self, event ): 
#        pos = event.pos()       
#        text = event.mimeData().text()
#        gridPos = self.getGridPosition(  pos.x(), pos.y() )
#        targetItem = self.item ( gridPos[0],  gridPos[1] )
#        if not targetItem:
#            self.emit( self.drop_event_signal, [ text, gridPos[0],  gridPos[1] ] )
#            event.acceptProposedAction()

 
#class DraggableScrollArea(QScrollArea):
#    
#    drop_event_signal = SIGNAL('drop_event')
#
#    def __init__(self, parent=None):
#        super(DraggableScrollArea, self).__init__(parent)
#        self.currentLocation = None 
#        self.setBackgroundRole(QPalette.Light)
#        self.setWidgetResizable(True) 
#        self.setAcceptDrops(True)
#            
#    def mousePressEvent ( self, event ):
#        if isTouchEvent( event ):
#            print "DraggableScrollArea Touch DOWN Event " 
#            event.accept()
#        super(DraggableScrollArea, self).mousePressEvent(event)
#        self.currentLocation = event.globalPos() 
##        print ' mousePressEvent: loc = ', str(self.currentLocation)
#
#    def mouseReleaseEvent ( self, event ):
#        if isTouchEvent( event ):
#            print "DraggableScrollArea Touch UP Event " 
#            event.accept()
#            return
#        super(DraggableScrollArea, self).mouseReleaseEvent(event)
#        self.currentLocation = None 
##        print ' mouseReleaseEvent '
#        
#    def mouseMoveEvent ( self, event ):
#        if isTouchEvent( event ):
#            print "DraggableScrollArea Touch MOVE Event " 
#            event.accept()
#            return
#        if self.currentLocation:
#            location = event.globalPos()
#            dragDistance = location - self.currentLocation
#            self.currentLocation = location
#            hBar = self.horizontalScrollBar() 
#            hBar.setValue( hBar.value() - dragDistance.x() )            
#            vBar = self.verticalScrollBar() 
#            vBar.setValue( vBar.value() - dragDistance.y() )            
##            print ' mouseMoveEvent: dragDistance = ', str( ( dragDistance.x(), dragDistance.y() ) )
#    def dragEnterEvent( self, event ):
#        if event.mimeData().hasFormat("text/plain"): 
#            event.acceptProposedAction()
#            
#    def dropEvent( self, event ): 
#        pos = event.pos()       
#        text = event.mimeData().text()
#        self.emit( self.drop_event_signal, [ text, pos.x(), pos.y() ] )
#        event.acceptProposedAction()
 

class TextAreaWidget( QWidget ):

    def __init__(self, parent=None ):
        super(TextAreaWidget, self).__init__(parent)

    def event ( self, event ):
        if isTouchEvent( event ):
            print "TextAreaWidget Touch Event, pos = %s " % strPos( event.pos() )
            event.accept()
            return True
        return super( TextAreaWidget, self ).event( event )

#def touchEnabledTextEditEvent ( self, event ):
#    if isTouchEvent( event ):
#        print "DraggableTextEdit Touch Event, pos = %s " % strPos( event.localPos )
#        event.accept()
#        return True
#    return QTextEdit.event( self, event )

class DraggableTextEdit(QTextEdit):

    def __init__(self, parent=None):
        super(DraggableTextEdit, self).__init__(parent)
        self.setAttribute(Qt.WA_AcceptTouchEvents)   
#        self.viewport().event = touchEnabledTextEditEvent  
        self.scrollArea = parent
    
    def mousePressEvent ( self, event ):
        if isTouchEvent( event ):
            print "DraggableTextEdit Touch Event, pos = %s " % str( event.pos() )
            event.accept()
        else:
            print " DraggableTextEdit mousePressEvent at %s " % strPos( event.pos() )
            shiftDown = (event.modifiers()&Qt.ShiftModifier)
            if shiftDown:
                postTouchEvent( self.window(), event.globalPos() )           
            if self.scrollArea and self.isReadOnly(): self.scrollArea.mousePressEvent ( event )
            else: super( DraggableTextEdit, self ).mousePressEvent( event )

    def mouseReleaseEvent ( self, event ):
        if self.scrollArea and self.isReadOnly(): self.scrollArea.mouseReleaseEvent ( event )
        else: super( DraggableTextEdit, self ).mouseReleaseEvent( event )
        
    def mouseMoveEvent ( self, event ):
        if self.scrollArea and self.isReadOnly(): self.scrollArea.mouseMoveEvent ( event )
        else: super( DraggableTextEdit, self ).mouseMoveEvent( event )

class MainForm( QMainWindow ):
 
    def __init__(self, showManager, parent=None):
        super(MainForm, self).__init__(parent)
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.showManager = showManager
        self.useHtml = False
        self.currentShowId = None
        self.displayedPageName = None
        self.currentPageName = None
        self.newPageName = None
        self.listDropAreaWidget = None
        self.buttonAreaWidget = None
        self.buttonAreaTable = None
        self.editing_scene = None
        self.setupGui()
        
    def resizeEvent (self, resizeEvent ):
        print " MainForm resizeEvent "
        
    def event ( self, event ):
        if event.type() == ControlEventType:
            if ( event.controlEventType == 'P' ):
                print " --> Wireless Control Button Press, ID = ", str( event.buttonId )
                if ( event.buttonId[0] == 1 ):
                    if ( event.buttonId[1] == 3 ):
                        currentItem = self.showManager.selectNextShow( self.currentPageName, self.currentShowId )
                        self.currentShowId = currentItem.id
                        self.ensureVisible( currentItem )
                        self.showManager.runShow( self.currentShowId )
                    elif ( event.buttonId[1] == 0 ):
                        self.showManager.runShow( self.currentShowId )
                    else:
                        currentItem = self.showManager.selectNextShow( self.currentPageName, self.currentShowId, event.buttonId[1]-4 )
                        self.currentShowId = currentItem.id
                        self.ensureVisible( currentItem )
            if ( event.controlEventType.lower() == 'j' ):
                joystick_sensitivity = 0.005
#                print " **Form--> JS Toggle, Pos = ( %.2f %.2f )" % ( event.jx, event.jy ) 
                dx = event.jx  * joystick_sensitivity
                dy = event.jy  * joystick_sensitivity
                self.scroll( dx, dy )
                 
        if isTouchEvent( event ):
            print "MainForm Touch Event, class = %s " % str( event.__class__ )
            event.accept()
            return True
#        if event.type() <> 76: 
#            print " --------> MainForm event: type = %s, class = %s " % ( str( event.type() ), str( event.__class__ ) )
        return super(MainForm, self).event( event )
        
    def closeEvent ( self, event ):
        self.showManager.save()
        QApplication.exit(0)
        
#    def event ( self, event ):
#        print " Event: ", str(event)
#        return super(MainForm, self).event(event)
        
    def getControlButton(self,  label, action, parent, icon_name = None, **args ):
        button = QToolButton( parent ) 
        checkable = args.get( 'checkable', False )
        icon_size = args.get( 'size', 50 )
        if icon_name:
            button.setIcon( loadIcon( icon_name ) )
            button.setIconSize( QSize( icon_size, icon_size ) )
        if label: 
            button.setText( label )
        button.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )
        text_border_size = 20 if label else 0
        button_size = icon_size + text_border_size
        button.setMinimumHeight ( button_size )
        button.setMinimumWidth ( button_size )
        button.setMaximumHeight ( button_size )
        button.setMaximumWidth ( button_size )
        button.setCheckable ( checkable )
        self.connect( button, SIGNAL('clicked(bool)'),  action)
        return button

    def getPushButton(self,  label, action, parent, height, icon_name = None, checkable = False ):
        button = None
        if icon_name:
            button = QPushButton( loadIcon( icon_name ), label, parent ) 
            button.setIconSize( QSize( height, height ) )
        else: 
            button = QPushButton( label, parent )
            button.setMinimumHeight ( height )
            button.setMinimumWidth ( height )
        button.setCheckable ( checkable )
        self.connect( button, SIGNAL('clicked(bool)'),  action)
        return button
    
    def listConstructionWindowVisible( self, isVisible ):
        if isVisible:   
            self.listConstructionAreaWidget.setMaximumWidth( 600 )
            self.listConstructionAreaWidget.setMinimumWidth( 600 )
        else:           
            self.listConstructionAreaWidget.setMaximumWidth( 0 )
            self.listConstructionAreaWidget.setMinimumWidth( 0 )
            
    def ensureVisible( self, item ):
        if self.listEditorOpen():   self.listConstructionScrollArea.ensureVisible( item )
        else:                       self.buttonAreaTable.ensureVisible( item )

    def scroll( self, dx, dy ):
        if self.listEditorOpen():   self.listConstructionScrollArea.scroll(  dx, dy  )
        else:                       self.buttonAreaTable.scroll(  dx, dy  )
                          
    def setupGui(self):
        centralWidget = QWidget( self )
        layout = QVBoxLayout()
        self.setCentralWidget ( centralWidget )
        centralWidget.setLayout( layout )

        # Show Selection
        showSelectionAreaLayout = QHBoxLayout()
        layout.addLayout( showSelectionAreaLayout, 1 ) 
          
        self.setWindowTitle("Hyperwall Interface")
        
        # List Construction
        self.listConstructionAreaWidget = QFrame(self)  
        list_construction_area_layout = QHBoxLayout()
        self.listConstructionAreaWidget.setLayout( list_construction_area_layout )
        
        list_construction_show_grid_layout = QVBoxLayout()
        self.listConstructionAreaWidget.setFrameStyle( QFrame.StyledPanel | QFrame.Raised )
        self.listConstructionAreaWidget.setLineWidth(2)
        
        self.listConstructionAreaWidget.setMaximumWidth( 250 )
        showSelectionAreaLayout.addWidget( self.listConstructionAreaWidget )

        list_construction_title_area_layout = QHBoxLayout()
        list_construction_area_title = QLabel("Drop Shows into List:")
        list_construction_area_title.setFont( QFont("Times", 16, QFont.Bold) )
        list_construction_title_area_layout.addWidget( list_construction_area_title ) 
        self.listNameEditor = QLineEdit("")
        self.listNameEditor.setReadOnly(False) 
        self.listNameEditor.setFont( QFont("Times", 16, QFont.Bold) )
        list_construction_title_area_layout.addWidget( self.listNameEditor )          
        
        list_construction_show_grid_layout.addLayout( list_construction_title_area_layout )        
        self.listConstructionScrollArea = ShowGridWidget( 'ListConstruction', self.showManager, self, MultitouchRole.CONSUMER, ncols=[2,1] )
#        print " listConstructionScrollArea: %x " % id( self.listConstructionScrollArea )

#        self.connect( self.listConstructionScrollArea, self.listConstructionScrollArea.drop_event_signal, self.addShowToList )
        list_construction_show_grid_layout.addWidget( self.listConstructionScrollArea )    
                   
        list_construction_buttonbox_layout = QVBoxLayout() 
        cancel_button = self.getControlButton(  "Cancel", self.closeListEditor, self.listConstructionAreaWidget, 'cancel' )  
        list_construction_buttonbox_layout.addWidget( cancel_button )             
        save_button = self.getControlButton(  "Save List", self.saveList, self.listConstructionAreaWidget, 'save' )  
        list_construction_buttonbox_layout.addWidget( save_button )             
        delete_button = self.getControlButton(  "Remove Show", self.removeShow, self.listConstructionAreaWidget, 'trash' )  
        list_construction_buttonbox_layout.addWidget( delete_button )             

        list_construction_area_layout.addLayout( list_construction_buttonbox_layout ) 
        list_construction_area_layout.addLayout( list_construction_show_grid_layout )

        self.buttonAreaTable = ShowGridWidget( 'ShowSelection', self.showManager, self, MultitouchRole.PRODUCER, ncols=[6,2] )
        self.buttonAreaTable.initShowLists()  
#        self.connect( self.buttonAreaTable.scene, SIGNAL('showDocs(QString)'), self.showDocumentation )
        showSelectionAreaLayout.addWidget( self.buttonAreaTable )        

        listAreaWidget = QFrame(self)  
        list_area_layout = QHBoxLayout() 
        listAreaWidget.setFrameStyle( QFrame.StyledPanel | QFrame.Raised )
        listAreaWidget.setLineWidth(2)
        listAreaWidget.setMaximumSize( 400, 300 )
#        listAreaWidget.setMinimumSize( 300, 300 )
        
        list_area_list_layout = QVBoxLayout() 
        list_area_title_layout = QHBoxLayout() 
        list_area_list_layout.addLayout( list_area_title_layout )
          
        listAreaTitle = QLabel("Show Lists")
        listAreaTitle.setFont( QFont("Times", 18, QFont.Bold) )
        list_area_title_layout.addWidget( listAreaTitle )

        up_button = self.getControlButton(  None, self.listUp, listAreaWidget, 'up', size = 45 )  
        list_area_title_layout.addWidget( up_button )
        down_button = self.getControlButton(  None, self.listDown, listAreaWidget, 'down', size = 45 )
        list_area_title_layout.addWidget( down_button )  
        
        self.listWidget = StationaryListWidget(self) 
        self.listWidget.setSelectionMode( QAbstractItemView.SingleSelection )
        self.connect( self.listWidget, SIGNAL( "itemSelectionChanged()" ), self.selectPage )
        usrPageNames = self.showManager.getPageNames()
        sysPageNames = self.showManager.importShowLists( self.buttonAreaTable )
        print " ** --> Importing pages: %s " % str( sysPageNames )
        self.listWidget.populate( usrPageNames + sysPageNames )
        self.listWidget.setFont( QFont("Times", 20 ) ) # , QFont.Bold) )
        self.listWidget.setGridSize( QSize ( 280, 40 ) )
        list_area_list_layout.addWidget( self.listWidget )
        
        list_area_buttons_layout = QVBoxLayout() 
        create_button = self.getControlButton(  "Create List", self.createNewList, listAreaWidget, 'tab_new_bg' )
        list_area_buttons_layout.addWidget( create_button )
        delete_button = self.getControlButton(  "Edit List", self.editList, listAreaWidget, 'edit' )
        list_area_buttons_layout.addWidget( delete_button )
        delete_button = self.getControlButton(  "Delete List", self.deleteList, listAreaWidget, 'trash' )  
        list_area_buttons_layout.addWidget( delete_button )             

        list_area_layout.addLayout( list_area_buttons_layout )
        list_area_layout.addLayout( list_area_list_layout )
        listAreaWidget.setLayout( list_area_layout ) 
     
        controlAreaWidget = QFrame(self)  
        control_area_layout = QVBoxLayout() 
        controlAreaWidget.setFrameStyle( QFrame.StyledPanel | QFrame.Raised )
        controlAreaWidget.setLineWidth(2)
 
        controlAreaWidget.setLayout( control_area_layout ) 
#        controlAreaWidget.setMinimumSize ( 150, 250 )        
        import_button =  self.getControlButton( "Import Show", self.importShow, controlAreaWidget, 'import' )
        control_area_layout.addWidget( import_button )  
        self.show_editable = self.getControlButton(  "Edit Show", self.editShow, controlAreaWidget, 'edit_clear', checkable=True )  
        control_area_layout.addWidget( self.show_editable )              
        trash_button = self.getControlButton(  "Trash", self.trash, controlAreaWidget, 'trash_green_full' )
        control_area_layout.addWidget( trash_button )

        descriptionAreaWidget = QFrame(self)
        description_area_layout = QVBoxLayout() 
        descriptionAreaWidget.setLayout( description_area_layout ) 
               
        description_title_area_layout = QHBoxLayout() 
        self.showTitleLabel = QLineEdit("")
        self.showTitleLabel.setReadOnly(True) 
        self.showTitleLabel.setFont( QFont("Times", 16, QFont.Bold) )
        description_title_area_layout.addWidget( self.showTitleLabel )         
#        self.show_editable = self.getControlButton(  "Edit Show", self.editShow, descriptionAreaWidget, 'edit_clear', checkable=True )  
#        description_title_area_layout.addWidget( self.show_editable )        
        description_area_layout.addLayout( description_title_area_layout )

        self.descriptionBox = DraggableTextEdit()
        self.descriptionBox.setReadOnly(True) 
        self.descriptionBox.setAcceptRichText( self.useHtml ) 
        self.descriptionBox.setAttribute(Qt.WA_AcceptTouchEvents)
        self.descriptionBox.setMinimumSize ( 500, 800 )
        descriptionAreaWidget.setMaximumHeight( 300 )
        descriptionAreaWidget.setMinimumHeight( 200 )
        description_area_layout.addWidget( self.descriptionBox )
        self.connect( self.showManager, SIGNAL('closeEditing()'), self.closeEditing  )

        showManagementAreaLayout = QHBoxLayout()
        layout.addLayout( showManagementAreaLayout, 1 )  
               
        showManagementAreaLayout.addWidget( listAreaWidget )  
        showManagementAreaLayout.addWidget( descriptionAreaWidget ) 
        showManagementAreaLayout.addWidget( controlAreaWidget )        
        self.listConstructionWindowVisible( False )
        self.selectPage( 'global' )
        self.listWidget.selectItem('global')
        
    def listUp( self ):
        self.listWidget.pageUp()
        
    def listDown( self ):
        self.listWidget.pageDown()
        
    def closeEditing( self ):
        if self.show_editable.isChecked():
            self.show_editable.click()
        else: self.editShow( False )
        
    def trash( self ):
        pass

    def keyPressEvent ( self, event ):
        if event.key()  == Qt.Key_T:
            screenPos = QPoint(200,200)
            postTouchEvent( self, screenPos )
        if (event.key()  == Qt.Key_Q) and ( event.modifiers() & Qt.Key_Alt ):
            self.close()
            sys.exit()
        
    def selectPage( self, pageName = None ):
        scene = None
        if not pageName: 
            currentItem = self.listWidget.currentItem()
            if currentItem: pageName = str( currentItem.text() )
        if pageName:
            print "Setting current scene: ", pageName
            self.displayedPageName = pageName
            scene = self.showManager.updatePage( pageName )
            if scene:
                self.closeEditing() 
                scene.enableDragDropMode( False )
                self.buttonAreaTable.setCurrentScene( scene )
                self.connect( scene, SIGNAL('showDocs(QString)'), self.showDocumentation )
                try:
                    selectedItems = scene.selectedItems()
                    self.showDocumentation( selectedItems[0].id )
                except Exception, err:
                    print " Error selecting show item."
        return scene
        
    def setDescriptionEditable( self, editable ):
        self.showManager.editingRecord( self.currentShowId, editable )
        if editable:
            self.descriptionBox.setReadOnly( False ) 
            self.showTitleLabel.setReadOnly( False ) 
        else:
            self.descriptionBox.setReadOnly( True ) 
            self.showTitleLabel.setReadOnly( True ) 
       
    def show(self): 
        super(MainForm, self).show()
        self.buttonAreaTable.updateView()  
        
    def listEditorOpen(self):
        return ( self.listConstructionAreaWidget.maximumWidth() > 0 )
        
    def closeListEditor(self):
        self.listConstructionWindowVisible( False )
        self.buttonAreaTable.scene.enableDragDropMode( False )
        if self.editing_scene:
#            self.editing_scene.setAcceptDrops(False)
            self.editing_scene = None
        self.listWidget.setDisabled( False )

    def openListEditor(self):
        self.listConstructionWindowVisible( True )
        self.buttonAreaTable.scene.enableDragDropMode( True )
        self.listWidget.setDisabled( True )
        
    def deleteList(self): 
        removedPageName = self.listWidget.deleteSelectedItem( exempt=[ 'global' ] )  
        if removedPageName: self.showManager.removePage( removedPageName )
        self.closeListEditor()
        self.listWidget.selectItem( 'global' )
      
    def removeShow( self ):
        self.showManager.removeSelectedShowFromList( self.currentPageName )
#        self.listConstructionScrollArea.setCurrentPage( self.currentPageName )
        self.listConstructionScrollArea.refreshList()

    def saveList(self): 
        editedPageName = str( self.listNameEditor.text() )
        savedPageName = editedPageName if editedPageName else ( self.newPageName if self.newPageName else self.currentPageName )
        if self.newPageName:   
            self.listWidget.addItem( savedPageName )  
            if editedPageName <>  self.newPageName:  self.showManager.renamePage( self.newPageName, savedPageName )       
        else:                   
            self.listWidget.renameItem( self.currentPageName, savedPageName ) 
            if editedPageName <>  self.currentPageName:  self.showManager.renamePage( self.currentPageName, savedPageName )
        self.listWidget.selectItem( savedPageName )
        self.closeListEditor()
        self.currentPageName = savedPageName       
        self.showManager.savePages()
        self.selectPage( self.currentPageName )
        self.newPageName = None           

    def createNewList(self):
        self.closeEditing() 
        self.buttonAreaTable.setCurrentPage('global')
        self.listWidget.selectItem('global')
        self.openListEditor()
        self.newPageName = self.listWidget.getUniqueItemName("NewList")      
        self.listNameEditor.setText( self.newPageName )
        self.listNameEditor.setFocus()
        self.listNameEditor.setCursorPosition ( len(self.newPageName) )
        self.editing_scene = self.listConstructionScrollArea.addPage( self.newPageName  )
#        self.editing_scene.setAcceptDrops(True) 
        self.connect( self.editing_scene, SIGNAL('showDocs(QString)'), self.showDocumentation )

    def editList(self):
        self.closeEditing() 
        self.currentPageName = self.listWidget.getSelectedItem() 
        if self.currentPageName and self.currentPageName <> 'global':
            self.listNameEditor.setText( self.currentPageName )
            self.listNameEditor.setFocus()
            self.listNameEditor.setCursorPosition ( len(self.currentPageName) )
    #        self.listWidget.editItem( self.listWidget.currentItem() )
            self.editing_scene = self.listConstructionScrollArea.setCurrentPage( self.currentPageName )
#            self.editing_scene.setAcceptDrops(True) 
            self.selectPage( 'global' )
            self.openListEditor()
        
    def editShow( self, editable ): 
        self.setDescriptionEditable( editable ) 
        if not editable:
            showRec = self.showManager.getShowRecord( self.currentShowId )
            if showRec:
                showRec.setTitle( self.showTitleLabel.text() )
                showRec.setDescription( self.descriptionBox.toPlainText() )

    def importShow(self): 
        showRec = self.showManager.importShow()
        if showRec:
            pageName = self.displayedPageName if self.displayedPageName else 'global'
            scene = self.showManager.getPage( pageName )
            if scene: scene.updateShowItem( showRec )
                       
    def importShow1(self): 
        showName, showPath = self.showManager.forceGetCurrentSnapshot()
        showRec = self.showManager.getShowRecord( showName, path=showPath, create=True )        
        if showRec:
            scene = self.selectPage( 'global' )
            item = scene.createShowItem( showRec.id, showRec.loadPixmap(), showRec.isActive() )
            self.showDocumentation( showRec.id )
            item.update()
        
    def showDocumentation(self, showId ):
        showRec = self.showManager.getShowRecord( str(showId) )
        if not showRec:
            print "ShowDocumentation: Can't find show: " % showId
        else:
            description = showRec.getDescription()
            if self.useHtml: self.descriptionBox.setHtml( QString(description) )
            else:            self.descriptionBox.setText( QString(description) )
            title = showRec.title if showRec.title else ''
            self.showTitleLabel.setText( title )
            self.currentShowId = showRec.id
#            print " $$$ Button %s clicked: title = '%s'" % ( showRec.id, showRec.title )
        
if __name__ == '__main__':
    enableMultitouch = False
    enableWirelessController = True
    fullScreen = False
    
    from TouchscreenClient import *  
    from QtWirelessControllerInterface import *  
    from HWShowManager import showManager
    app = QApplication(sys.argv)
    showManager.updateShows()
    form = MainForm( showManager )
    rect = QApplication.desktop().availableGeometry()
    form.resize(int(rect.width()), int(rect.height()))
    if fullScreen: form.showFullScreen()
    else: form.show()
    tc = TouchscreenManager( form, app ) if enableMultitouch else None
    controllerInterface = QtControllerInterface( form ) if enableWirelessController else None
    if controllerInterface: controllerInterface.start()
    app.exec_()
    if tc: tc.shutdown()
    if controllerInterface: controllerInterface.stop()
    
