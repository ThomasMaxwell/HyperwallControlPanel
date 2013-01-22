'''
Created on Jun 28, 2011

@author: tpmaxwel
'''

import os, math, time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from HWShowManager import showManager, LargeIconSize, SmallIconSize
from TouchscreenClient import *
hw_root_dir = os.path.dirname(__file__)
hw_config_data_path = os.path.join( hw_root_dir, 'data' )
hw_icon_data_path = os.path.join( hw_config_data_path, 'icons' )
def pt2str( pt ): return "( %.2f, %.2f )" % ( pt.x(), pt.y() ) 
def rect2str( rect ): return "{ %s %s }" % ( pt2str( rect.bottomLeft() ), pt2str( rect.topRight() ) ) 

GRID_MODE = 0
LIST_MODE = 1
SEARCH_HORIZONTAL = 0
SEARCH_VERTICAL = 1

TSIZE = 5
CORNER_SIZE = 0.25
RollEventType =  QEvent.User + 5
   
class RollEvent( QEvent ):
 
    def __init__( self, dval ):
        QEvent.__init__ ( self, RollEventType )
        self.dv = dval

class MultitouchRole:
    PRODUCER = 0
    CONSUMER = 1

def loadIcon( name ):
    iconFile =  os.path.join( hw_icon_data_path, name + ".png" )
    icon = QIcon ( iconFile )
    return icon
        
def getQPoint( pointf ):
    return QPoint( int( pointf.x() ), int( pointf.y() ) )

def bound( value, vrange ):
    if value < vrange[0]: return vrange[0]
    if value > vrange[1]: return vrange[1]
    return value

class GraphicsViewport( QWidget ):

    def __init__(self, parent=None):
        super(GraphicsViewport, self).__init__(parent)
    
#    def mousePressEvent ( self, event ):
#        if isTouchEvent( event ):
#            print "GraphicsViewport Mouse Touch Event, pos = %s, class = %s " % ( strPos( event.pos() ), str( event.__class__ ) ) 
#            event.accept()
#            return
#        super( GraphicsViewport, self ).mousePressEvent( event )

#class DraggableListWidget(QListWidget):
#    
#    list_selection_signal = SIGNAL('list_selection')
#
#    def __init__( self, parent=None, scroll_factor=1.0, mrole = None ):
#        super(DraggableListWidget, self).__init__(parent)
#        self.setAttribute(Qt.WA_AcceptTouchEvents)
#        self.currentLocation = None 
#        self.currentTouchId = None
#        self.scrollFactor = scroll_factor
#        self.setAcceptDrops(True)
#        self.role = mrole
#        self.scrollSensitivity = 0.5
#        self.showList = None
#        self.sliderRange = [ 0, 100 ]  
##        self.connect( self, SIGNAL( "itemSelectionChanged()" ), self.itemSelected )
#
#    def updateListData( self, listData  ):
#        self.clear ()
#        self.showList = []
#        background = QBrush( QColor( 230, 240, 255 ) ) 
#        for iShowIndex in range( len( listData ) ):
#            ( showId, pixmap, text ) = listData[ iShowIndex ]
##            id = listData[0]
##            pixmap = listData[1]
##            text =  listData[2]
#            item = QListWidgetItem( QIcon( pixmap ), text )
#            if iShowIndex %2 == 0: item.setBackground ( background )
#            self.addItem( item )
#            self.showList.append( showId )
#        
#    def getShowId( self, iRow  ):
#        return self.showList[ iRow ]        
#            
#    def mousePressEvent ( self, event ):
#        isTE = isTouchEvent( event )
#        if isTE:
##            print "DraggableListWidget Touch Event, pos = %s " % strPos( localPos )
#            if event.gesture.cardinality > 1:
#                self.horizontalScrollBar().setRange( self.sliderRange[0], self.sliderRange[1] )
#                self.verticalScrollBar().setRange( self.sliderRange[0], self.sliderRange[1] )
#                self.currentLocation = event.globalPos()
#                self.currentTouchId = event.id
#                super( DraggableListWidget, self ).mousePressEvent ( event ) 
#            else:
#                globalPos = event.globalPos()
#                localPos = self.mapFromGlobal( globalPos )
#                mouse_event = QMouseEvent ( QEvent.MouseButtonPress, localPos, globalPos, Qt.LeftButton, Qt.LeftButton, Qt.MetaModifier )
#                super( DraggableListWidget, self ).mousePressEvent ( mouse_event ) 
#    #            self.emit( SIGNAL( 'dragItem(int)' ), self.getSelectedRow() ) 
#                self.processTouchEvent( event ) 
#                event.accept()
#        else:
#            shiftDown = (event.modifiers()&Qt.ShiftModifier)
#            if shiftDown:
#                postTouchEvent( self.window(), event.globalPos() ) 
#            else:
#                self.currentLocation = event.globalPos()
#                super( DraggableListWidget, self ).mousePressEvent ( event ) 
#                if ( event.button() == Qt.LeftButton ): 
#                    self.emit( SIGNAL( 'dragItem(int)' ), self.getSelectedRow() )               
#    #                print "DraggableListWidget Mouse Event, pos = %s " % strPos( event.pos() )
#
#    def processTouchEvent( self, event ):
#        scenePos = event.pos()
#        if self.role == MultitouchRole.CONSUMER:
#            event.gesture.targetList = self
#            event.gesture.targetPos = scenePos
#        elif self.role == MultitouchRole.PRODUCER:
##            localPos = self.mapFromGlobal( event.globalPos() )
##            item =  self.itemAt( localPos )
##            self.setCurrentItem( item )
#            iRow = self.getSelectedRow()
#            showId = self.getShowId( iRow )
#            targetScene = event.gesture.targetScene
#            if targetScene <> None:
#                targetScene.addShow(  showId, event.gesture.targetPos )
#                return
#            targetList = event.gesture.targetList
#            if targetList <> None:
#                targetList.dropItem( showId )
#                return
#
#    def dropEvent ( self, event ): # QGraphicsSceneDragDropEvent
#        if event.source() <> self:
#            showId = str( event.mimeData().text() ) 
#            self.dropItem( showId ) 
#            event.acceptProposedAction()  
#        else:
#            event.ignore() 
#
#    def dropItem ( self, showId ): # QGraphicsSceneDragDropEvent
#        self.emit( SIGNAL( 'dropItem(QString)' ), QString( showId ) ) 
# 
#    def dragEnterEvent ( self, event ): 
#        if ( event.source() <> self ) and event.mimeData().hasFormat("text/plain"): 
#            event.acceptProposedAction()
#        else:
#            event.ignore()
#
#    def dragMoveEvent ( self, event ):
#        if ( event.source() <> self ) and event.mimeData().hasFormat("text/plain"): 
#            event.acceptProposedAction()
#        else:
#            event.ignore()
#
#    def getSelectedRow( self ):
#        iRow = -1
#        try:
#            items = self.selectedItems()
#            iRow = self.row( items[0] ) 
#        except:
#            pass
#        return iRow
#
#    def mouseDoubleClickEvent ( self, event ):
#        iRow = self.getSelectedRow()
#        self.emit( SIGNAL('executeItem(int)'), iRow )   
#      
#    def selectItem(self, name ):           
#        items = self.findItems ( QString(name), Qt.MatchExactly )
#        if items: self.setCurrentItem(items[0])
#
#    def renameItem(self, current_name, new_name ):         
#        items = self.findItems ( QString(current_name), Qt.MatchExactly )
#        if items: items[0].setText( QString(new_name) )
#        
#    def mouseReleaseEvent ( self, event ):
#        self.currentLocation = None 
#        
#    def getSelectedItem(self):
#        item = self.currentItem()
#        return str( item.text() ) if item else None
#        
#    def itemSelected( self ):
#        pass
#        self.emit( self.list_selection_signal, str('item.text()') )
#        
#    def mouseMoveEvent ( self, event ):
#        if self.currentLocation and ( self.currentTouchId == event.id ):
#            location = event.globalPos()
##            dragDistance = QPoint( int( round( ( location.x() - self.currentLocation.x() ) * self.scrollSensitivity ) ), int( round( ( location.y() - self.currentLocation.y() ) * self.scrollSensitivity ) ) )
#            dragDistance = location - self.currentLocation
#            print "_________________ location, currentLocation, dragDistance __________________________"
#            for x in ( location, self.currentLocation, dragDistance ): print str( ( x.x(), x.y() )  )
#            self.currentLocation = location
#            hBar = self.horizontalScrollBar() 
#            if dragDistance.x() <> 0: 
#                dx = -1 if dragDistance.x() < 0 else 1
#                hBar.setValue(  bound( hBar.value() - dx, [ hBar.minimum(), hBar.maximum() ] ) )            
#            vBar = self.verticalScrollBar() 
#            if dragDistance.y() <> 0: vBar.setValue( bound( vBar.value() - dragDistance.y(), [ vBar.minimum(), vBar.maximum() ] ) )            
#            print " VBAR VAL = ", str( vBar.value()  )

class StationaryListWidget(QListWidget):
    
    list_selection_signal = SIGNAL('list_selection')

    def __init__( self, parent=None, mrole = None ):
        super(StationaryListWidget, self).__init__(parent)
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
#        self.setAcceptDrops(True)
        self.role = mrole
        self.showList = None
        self.listHead = 0
        self.maxItems = 5
#        self.connect( self, SIGNAL( "itemSelectionChanged()" ), self.itemSelected )

    def populate( self, items ):
        self.listHead = 0
        self.showList = []
        for item in items:
            self.showList.append( item )
        self.resetList()

    def addItem( self, item, select = True ): 
        self.showList.append( item )
        super(StationaryListWidget, self).addItem( item )
        
    def renameItem( self, old_value, new_value ):
        selIndex = self.showList.index( old_value )
        self.showList[ selIndex ] = new_value
        items = self.findItems( QString(old_value), Qt.MatchExactly )
        for item in items: item.setText( new_value )
        
    def selectItem( self, selection ):
        selIndex = self.showList.index( selection )
        listHead = ( selIndex/self.maxItems ) * self.maxItems
        if listHead <> self.listHead:
            self.listHead = listHead
            self.resetList()         
        items = self.findItems ( QString(selection), Qt.MatchExactly )
        if items: self.setCurrentItem(items[0])
                   
    def resetList( self ):
        self.clear ()
        listEnd = self.listHead + self.maxItems
        nItems = len( self.showList )
        listEnd = nItems if listEnd > nItems else listEnd
        for iItem in range( self.listHead, listEnd ):
            super(StationaryListWidget, self).addItem( self.showList[ iItem ] )
            
    def getUniqueItemName( self, baseName ):
        for itemIndex in range( 1, 10000 ):
            itemName = "%s-%d" % ( baseName, itemIndex ) 
            if itemName not in self.showList:
                return itemName
        return None

    def deleteSelectedItem( self, **args ):
        exempt = args.get( 'exempt', [] )
        selectedRow = self.currentRow () 
        item = self.item ( selectedRow ) 
        selectedItem = str( item.text() )        
        if selectedItem in exempt: return None
        self.showList.remove( selectedItem )
        self.resetList()
        return selectedItem           
                
    def pageUp( self ):
        if self.listHead > 0:
            self.listHead = self.listHead - self.maxItems
            self.resetList() 

    def pageDown( self ):
        newListHead = self.listHead + self.maxItems
        if newListHead < len( self.showList ):
            self.listHead = newListHead
            self.resetList() 

    def updateListData( self, listData  ):
        self.clear ()
        self.showList = []
        background = QBrush( QColor( 230, 240, 255 ) ) 
        for iShowIndex in range( len( listData ) ):
            ( showId, pixmap, text ) = listData[ iShowIndex ]
#            id = listData[0]
#            pixmap = listData[1]
#            text =  listData[2]
            item = QListWidgetItem( QIcon( pixmap ), text )
            if iShowIndex %2 == 0: item.setBackground ( background )
            super(StationaryListWidget, self).addItem( item )
            self.showList.append( showId )
        
    def getShowId( self, iRow  ):
        return self.showList[ iRow ]        
            
    def mousePressEvent ( self, event ):
        isTE = isTouchEvent( event )
        if isTE:
#            print "StationaryListWidget Touch Event, pos = %s " % strPos( localPos )
            globalPos = event.globalPos()
            localPos = self.mapFromGlobal( globalPos )
            mouse_event = QMouseEvent ( QEvent.MouseButtonPress, localPos, globalPos, Qt.LeftButton, Qt.LeftButton, Qt.MetaModifier )
            super( StationaryListWidget, self ).mousePressEvent ( mouse_event ) 
#            self.emit( SIGNAL( 'dragItem(int)' ), self.getSelectedRow() ) 
            self.processTouchEvent( event ) 
            event.accept()
        else:
            shiftDown = (event.modifiers()&Qt.ShiftModifier)
            if shiftDown:
                postTouchEvent( self.window(), event.globalPos() ) 
            else:
                super( StationaryListWidget, self ).mousePressEvent ( event ) 
                if ( event.button() == Qt.LeftButton ): 
                    self.emit( SIGNAL( 'dragItem(int)' ), self.getSelectedRow() )               
    #                print "DraggableListWidget Mouse Event, pos = %s " % strPos( event.pos() )

#    def processTouchEvent( self, event ):
#        scenePos = event.pos()
#        if self.role == MultitouchRole.CONSUMER:
#            event.gesture.targetList = self
#            event.gesture.targetPos = scenePos
#        elif self.role == MultitouchRole.PRODUCER:
##            localPos = self.mapFromGlobal( event.globalPos() )
##            item =  self.itemAt( localPos )
##            self.setCurrentItem( item )
#            iRow = self.getSelectedRow()
#            showId = self.getShowId( iRow )
#            targetScene = event.gesture.targetScene
#            if targetScene <> None:
#                targetScene.addShow(  showId, pos=event.gesture.targetPos )
#                return
#            targetList = event.gesture.targetList
#            if targetList <> None:
#                targetList.dropItem( showId )
#                return

#    def dropEvent ( self, event ): # QGraphicsSceneDragDropEvent
#        if event.source() <> self:
#            showId = str( event.mimeData().text() ) 
#            self.dropItem( showId ) 
#            event.acceptProposedAction()  
#        else:
#            event.ignore() 
#
#    def dropItem ( self, showId ): # QGraphicsSceneDragDropEvent
#        self.emit( SIGNAL( 'dropItem(QString)' ), QString( showId ) ) 
# 
#    def dragEnterEvent ( self, event ): 
#        if ( event.source() <> self ) and event.mimeData().hasFormat("text/plain"): 
#            event.acceptProposedAction()
#        else:
#            event.ignore()
#
#    def dragMoveEvent ( self, event ):
#        if ( event.source() <> self ) and event.mimeData().hasFormat("text/plain"): 
#            event.acceptProposedAction()
#        else:
#            event.ignore()

    def getSelectedRow( self ):
        iRow = 0
        try:
            items = self.selectedItems()
            iRow = self.row( items[0] ) 
        except: pass          
        return iRow

    def mouseDoubleClickEvent ( self, event ):
        iRow = self.getSelectedRow()
        self.emit( SIGNAL('executeItem(int)'), iRow )   
                      
    def getSelectedItem(self):
        item = self.currentItem()
        return str( item.text() ) if item else None
        
    def itemSelected( self ):
        pass
        self.emit( self.list_selection_signal, str('item.text()') )

class ScrollRollThread( threading.Thread ):
    
    TIME_DELAY = .01
    TIME_DELAY_DILATION = 0.00
    ROLL_INCREMENT = 5

    def __init__( self, target, speed ):
        threading.Thread.__init__( self )
        self.isActive = True 
        self.daemon = True
        self.speed = speed
        self.target = target
        self.time_delay = self.TIME_DELAY

    def stop(self):
        self.isActive = False

    def run(self):
#        dx = self.ROLL_INCREMENT if self.speed > 0 else -self.ROLL_INCREMENT
        while self.isActive:
            QApplication.postEvent( self.target, RollEvent( self.speed ) ) 
            time.sleep( self.time_delay )
            self.time_delay += self.TIME_DELAY_DILATION 
         
class GraphicsView(QGraphicsView):
    
    MIN_SCROLL_SPEED_FOR_ROLL = 5

    def __init__(self, name, layout_mode, parent=None, **args ):
        super(GraphicsView, self).__init__(parent)
        self.name = name
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.grabGesture(Qt.PanGesture)
        self.grabGesture(Qt.PinchGesture)
        self.grabGesture(Qt.SwipeGesture)
        self.setViewport( GraphicsViewport() )
        self.setAcceptDrops( True )
        self.layout_mode = layout_mode
        self.role = args.get( 'role', None )
        self.ncols = args.get( 'ncols', 2 )
        self.scroll_speed = None
        self.vpos = None
        self.scrollRollThread = None
                
    def setScene( self, scene ):
        scene.setParent(self)
        QGraphicsView.setScene( self, scene )
        scene.setLayoutMode( self.layout_mode )
        
#    def dropEvent ( self, event ): 
#        scene = self.scene()
#        if scene: scene.dropEvent( event )
#
#    def dragEnterEvent ( self, event ): 
#        scene = self.scene()
#        if scene: scene.dragEnterEvent( event )
        
    def getNColumns(self):
        return self.ncols

#    def paintEvent ( self, event ):
#        print " ----------- GraphicsView:paintEvent: %s --------------- " % rect2str( event.rect() )
#        super(GraphicsView, self).paintEvent ( event )
                
    def focusInEvent( self, focusEvent ):
        self.resetScroll()
        
    def resetScroll(self):
        return
    
#        for sBar in ( self.horizontalScrollBar(), self.verticalScrollBar() ): sBar.setValue( sBar.minimum() )
#        scroll_bar_size = 40
#        self.horizontalScrollBar().setMinimumHeight ( scroll_bar_size )
#        self.verticalScrollBar().setMinimumWidth ( scroll_bar_size )
                
    def wheelEvent(self, event):
#        print " --------> GraphicsView wheel event: delta = %s, class = %s " % ( str( event.delta() ), str( event.__class__ ) )
        factor = 1.41 ** (-event.delta() / 240.0)
        self.scale(factor, factor)
        
    def event(self, e): 
        if ( e.type() == RollEventType ): 
            sBar = self.verticalScrollBar()
            sBar.setValue( sBar.value() + e.dv )
            e.accept()
            return True
        return QGraphicsView.event( self, e ) 
        
    def mouseMoveEvent( self, event ):
        vpos = self.verticalScrollBar().value()
        if self.vpos: 
            self.scroll_speed = vpos - self.vpos
            print " ---> mouseMoveEvent, vpos = %s, speed = %s " % ( str( vpos ), str( self.scroll_speed ) )
        self.vpos = vpos
        super( GraphicsView, self ).mouseMoveEvent( event )
        
    def mouseReleaseEvent ( self, event ):
        super( GraphicsView, self ).mouseReleaseEvent( event )
        self.startScrollRoll()
        self.scroll_speed = None
        self.vpos = None
        
    def startScrollRoll( self ):
        if self.scroll_speed and ( abs( self.scroll_speed ) >= self.MIN_SCROLL_SPEED_FOR_ROLL ):
            self.scrollRollThread = ScrollRollThread( self, self.scroll_speed/self.MIN_SCROLL_SPEED_FOR_ROLL )
            self.scrollRollThread.start()

    def stopScrollRoll( self ):
        if self.scrollRollThread:
            self.scrollRollThread.stop()
            self.scrollRollThread = None

    def mousePressEvent ( self, event ):
        self.stopScrollRoll()
        if isTouchEvent( event ):
            scenePos =  self.mapToScene( event.pos() )
            sceneItem = self.itemAt ( event.pos() )
            self.processTouchEvent( event, scenePos, sceneItem ) 
            print "GraphicsView Mouse Touch Event, pos = %s, class = %s " % ( strPos( event.pos() ), str( event.__class__ ) ) 
            event.accept()
            self.vpos = self.horizontalScrollBar().value()
            return
        super( GraphicsView, self ).mousePressEvent( event )

    def processTouchEvent( self, event, scenePos, sceneItem ):
        try: sceneItem.touchEvent( scenePos, event )
        except: pass
        if self.role == MultitouchRole.CONSUMER:
            event.gesture.targetScene = self.scene()
            event.gesture.targetPos = scenePos
        elif self.role == MultitouchRole.PRODUCER:
            targetScene = event.gesture.targetScene
            if targetScene and sceneItem:
                targetScene.addShow(  sceneItem.id, pos=event.gesture.targetPos )
                return
            targetList = event.gesture.targetList
            if targetList and sceneItem:
                targetList.dropItem( sceneItem.id )

class GraphicsScene(QGraphicsScene):
    drop_event_signal = SIGNAL('drop_event')

    def __init__(self, showManager, name, parent=None, **args ):  
        super(GraphicsScene, self).__init__(parent)
        self.showManager = showManager
        self.growDirection = Qt.Vertical
        self.windowOffsetSize = 10
        self.initLayoutItemCoords = [ [ 0, 0 ], [ 0, 0 ] ]
        self.nCols = args.get( 'ncols')
        self.enableDragDrop = False
        self.showMap = {}
        self.idList = []
        self.name = name
        self.mouseDown = False
        self.gridDims = [ None, None ]
        self.newItemCount = 0
#        self.initialLayout = [ True, True ]
#        self.setLayoutMode( layout_mode )

        
    def setLayoutMode( self, layout_mode ):
        self.layout_mode = layout_mode
        self.mouseDown = False
        self.gridSpacing = ShowItem.gridSpacing( layout_mode ) 
        self.gridDims[ self.layout_mode ] = self.getGridDims()
        for item in self.items(): item.updatePosition( layout_mode )
        self.clearGridOverlap()
        pageSize = self.getPageSize()
        self.setSceneRect( 0, 0, pageSize[0], pageSize[1] )
        self.update( 0, 0, pageSize[0], pageSize[1] )
#        self.idList.sort()
#        for id in self.idList: 
#            item = self.showMap.get( id, None  )
#            if item: item.updatePosition( layout_mode )
#        self.initialLayout[ layout_mode ] = False
#        if self.initialLayout[ layout_mode ]:
#            self.idList.sort()
#            for id in self.idList: 
#                item = self.showMap.get( id, None  )
#                if item: item.updatePosition( layout_mode )
#            self.initialLayout[ layout_mode ] = False
#        else:
#            for item in self.items(): item.updatePosition( layout_mode )
        
    def getLayoutMode(self):
        return self.layout_mode
        
    def enableDragDropMode( self, enable ):
        self.enableDragDrop = enable
        print " enableDragDropMode(%s): %s" % (  self.name, str( enable ) )
        
#    def initialize( self, name ):
#        self.name = name

    def getGridDims( self ):
        ns = showManager.getNShows()
        nCols = self.parent().getNColumns()
        return [ nCols, ns/nCols + 1 ]
        
#        return [ int( math.ceil( float(self.window_size[i])/self.gridSpacing[i] ) ) for i in range(2) ]

    def clearGridOverlap(self):
        iy = 0
        while iy < self.gridDims[ self.layout_mode ][1]:
            ix = 0
            while ix < self.gridDims[ self.layout_mode ][0]:
                self.clearOvelap( [ ix, iy ] )
                ix = ix + 1
            iy = iy + 1
                             
    def deserialize( self, datastring ):
        dataComponents = datastring.split(':')
        header = dataComponents[0]
        item_list = dataComponents[1]
        header_comps = header.split(',')
        self.name = header_comps[0]
        items = item_list.split(';')
        posIndex = 0
        for item in items:
            try:
                item_comps = item.split(',')
                showId = item_comps[0]
                self.addShow( showId, indices=[ int(item_comps[i]) for i in range( 1, len(item_comps) ) ] )
                posIndex = posIndex + 1   
            except Exception, err:
                print "Error parsing item: %s " % item

    def updatePage(self):
        pageSize = self.getPageSize()
        self.setSceneRect( 0, 0, pageSize[0], pageSize[1] )
        self.update()
                
    def serialize( self ):
        header = ','.join( [ self.name, str(self.gridDims[ self.layout_mode ][0]), str(self.gridDims[ self.layout_mode ][1]) ] )
        item_list = ';'.join( [ ','.join( item.getPositionIndexList( [ item.id ] ) ) for item in self.items() ] )
        return ':'.join( [ header, item_list ] )    # f.write(
        
    def setGrowthDirection( self, growDirection ):
        self.growDirection = growDirection 
                
    def updatePageSize( self, newGridCoords ):
        changed = False
        for iDim in range( 0, 2 ):
            if newGridCoords[iDim] >= self.gridDims[ self.layout_mode ][iDim]: 
                self.gridDims[self.layout_mode][iDim] = newGridCoords[iDim]+1
                changed = True
        if changed:
            pageSize = self.getPageSize()
            self.setSceneRect( 0, 0, pageSize[0], pageSize[1] )
        
    def getPageSize(self):
            return ( self.gridSpacing[0]*self.gridDims[ self.layout_mode ][0], self.gridSpacing[1]*self.gridDims[ self.layout_mode ][1] )
        
    def boundGridCoords(self, gc ):
        for iC in range(0,2):
            if gc[iC] < 0: gc[iC] = 0
            if gc[iC] >= self.gridDims[ self.layout_mode ][iC]: gc[iC] = self.gridDims[ self.layout_mode ][iC]-1
        return gc
    
    def getGridPos( self, gridCoords, offset = 0.0 ):
        posOffset = self.windowOffsetSize + offset
        return QPointF( posOffset + gridCoords[0]*self.gridSpacing[0], posOffset + gridCoords[1]*self.gridSpacing[1] )

    def getGridPositionIndex( self, gridCoords ):
        return gridCoords[0] + gridCoords[1] * self.gridDims[ self.layout_mode ][0]

    def getGridCoords( self, index ):
        return [ index % self.gridDims[ self.layout_mode ][0], index / self.gridDims[ self.layout_mode ][0] ]
    
    def getPositionIndex( self, pos, excludeCorners = False ):
        gx, gy = pos.x()/self.gridSpacing[0], pos.y()/self.gridSpacing[1]
        if excludeCorners:
            rx, ry = round( gx ), round( gy )
            isCorner = ( abs( gx-rx) < CORNER_SIZE ) and ( abs( gy-ry) < CORNER_SIZE )
            if isCorner: 
                print " <<<<< isCorner >>>>>>>"
                return None
        gridCoords = self.boundGridCoords(  [ int(gx), int(gy) ]  )
        return self.getGridPositionIndex( gridCoords )
        
    def getPositionFromIndex( self, index ):
        gridCoords = self.getGridCoords( index )
        gridPos = QPointF( self.windowOffsetSize+gridCoords[0]*self.gridSpacing[0], self.windowOffsetSize+gridCoords[1]*self.gridSpacing[1] )
        return gridPos
    
    def selectNextShow( self, showId, adjacencyIndex ):
        print " -- selectNextShow: id = ", showId
        item = self.showMap.get( showId, None )
        index_ceiling = self.gridDims[ self.layout_mode ][0] * self.gridDims[ self.layout_mode ][1]
        pos_index = item.getPositionIndex( self.layout_mode ) if item else -1
        gridCoords = None
        searchDir = SEARCH_HORIZONTAL
        while True:
            if adjacencyIndex < 0:
                pos_index = ( pos_index + 1 ) % index_ceiling
                gridCoords = self.getGridCoords( pos_index )
            else: 
                if not gridCoords: gridCoords = self.getGridCoords( pos_index )
                if   adjacencyIndex == 0: 
                    gridCoords[1] = ( gridCoords[1] - 1 ) % self.gridDims[ self.layout_mode ][1]
                elif adjacencyIndex == 1: 
                    gridCoords[0] = ( gridCoords[0] + 1 ) % self.gridDims[ self.layout_mode ][0]
                    searchDir = SEARCH_VERTICAL
                elif adjacencyIndex == 2: 
                    gridCoords[1] = ( gridCoords[1] + 1 ) % self.gridDims[ self.layout_mode ][1]
                elif adjacencyIndex == 3: 
                    gridCoords[0] = ( gridCoords[0] - 1 ) % self.gridDims[ self.layout_mode ][0]
                    searchDir = SEARCH_VERTICAL
                else: return showId            
            currentItem = self.getClosestItem( gridCoords, searchDir )
            if currentItem:
                self.clearSelection()
                currentItem.setSelected(True)
                self.setSelectedItem( currentItem )
                return currentItem
        return None
    
    def getClosestItem( self, gridCoords, searchDir ):
        gridPos = self.getGridPos( gridCoords, 20.0 )
        rv = self.itemAt( gridPos  )
        if rv == None:
            gc = [ gridCoords[0], gridCoords[1] ]
            dbound = self.gridDims[ self.layout_mode ][ searchDir ]
            for iDel in range( 1, dbound ):
                stopIter = True
                c1 = gridCoords[ searchDir ] - iDel 
                if c1 >= 0: 
                    gc[ searchDir ] = c1
                    gridPos = self.getGridPos( gc, 20.0 )
                    rv = self.itemAt( gridPos  )
                    if rv: return rv
                    stopIter = False 
                c1 = gridCoords[ searchDir ] + iDel 
                if c1 < dbound: 
                    gc[ searchDir ] = c1
                    gridPos = self.getGridPos( gc, 20.0 )
                    rv = self.itemAt( gridPos  )
                    if rv: return rv  
                    stopIter = False 
                if stopIter: break              
        return rv
                               
#    def addItem( self, item ):
#        super(GraphicsScene, self).addItem (item )
                
    def setSelectedItem( self, item ):
        self.emit( SIGNAL('showDocs(QString)'), QString(item.id) )

    def mouseReleaseEvent ( self, event ):
        super( GraphicsScene, self ).mouseReleaseEvent( event )
        self.mouseDown = False
        self.update()

    def mousePressEvent ( self, event ):
        self.mouseDown = True
        print " Scene mousePressEvent(%s): enableDragDrop=%s" % (  self.name, str( self.enableDragDrop ) )
        shiftDown = (event.modifiers()&Qt.ShiftModifier)
        if shiftDown:
            for view in self.views(): postTouchEvent( view.window(), event.screenPos() ) 
            return
        index = self.getPositionIndex( event.scenePos(), True )
        if index == None: 
            return super( GraphicsScene, self ).mousePressEvent( event )
        gridCoords = self.getGridCoords( index )
        gridPos = self.getGridPos( gridCoords, 20.0 )
#            print " pos = %s: gridCoords, gridPos = %s, %s " % ( strPos(event.scenePos()), str(gridCoords), strPos(gridPos) )
        currentItem = self.itemAt( gridPos  )
        if currentItem:
            if currentItem in self.selectedItems():
                currentItem.runShow()              
            if ( event.button() == Qt.LeftButton ) and self.enableDragDrop:
                self.clearSelection()
                drag = QDrag( self.views()[0] )
                mimeData = QMimeData()
                drag.setMimeData( mimeData )
                mimeData.setText( currentItem.id )
                drag.setPixmap( currentItem.getScaledPixmap() )
                drag.setHotSpot( QPoint( -20, 0 )  )
                drag.exec_( Qt.CopyAction |  Qt.MoveAction,  Qt.CopyAction)
            else:
                super( GraphicsScene, self ).mousePressEvent( event )
            
                
#                drag.exec_( ) # QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.CopyAction )
                
#                if drag.exec_( Qt.CopyAction |  Qt.MoveAction,  Qt.CopyAction) ==  Qt.MoveAction:
#                    currentItem.close()
#                else:
#                    currentItem.show()

        
                
    def dragEnterEvent ( self, event ): 
        print " GraphicsScene - dragEnterEvent "
        if event.mimeData().hasFormat("text/plain"): 
            showId = str( event.mimeData().text() )  
            if self.showMap.get( showId, None ):
                event.setDropAction( Qt.MoveAction )
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent ( self, event ):
        print " GraphicsScene - dragMoveEvent "
        if event.mimeData().hasFormat("text/plain"): 
            showId = str( event.mimeData().text() )  
            if self.showMap.get( showId, None ):
                event.setDropAction( Qt.MoveAction )
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()
            
    def isLocalDragDropEvent( self, event ):
        return event.source() == self.views()[0]
    
    def getActiveView(self):
        for view in self.views():
            return view
        return None
    
    def dropEvent ( self, event ): # QGraphicsSceneDragDropEvent
        print " GraphicsScene - dropEvent "
        scenePos = event.scenePos() 
        showId = str( event.mimeData().text() ) 
        movedItem = self.moveShow( showId, scenePos )      
        if not movedItem:
            grid_index = self.getPositionIndex( scenePos )
            self.addShow(  showId, [ grid_index, self.newItemCount ] )
            self.newItemCount = self.newItemCount + 1
        if movedItem:
            event.setDropAction( Qt.MoveAction )
            event.accept()
        else:
            event.acceptProposedAction()
            
#        for view in self.views():
#            view.update()
#        self.clearFocus()
#        self.clearSelection()
##        self.event ( QMouseEvent ( QEvent.MouseButtonPress, QPoint(1,1), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier ) )
##        self.event ( QMouseEvent ( QEvent.MouseButtonRelease, QPoint(1,1), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier ) )
#        self.setFocus( Qt.MouseFocusReason )

    def addShow( self, showId, indices = None ):
        showRec = self.showManager.getShowRecord( showId )
        if showRec: 
            item = self.createShowItem( showRec.id, showRec.getPixmap(), showRec.isActive() )
            if indices <> None: 
                item.initPositionIndices( indices )
                self.clearSpaceAndAddItem( indices[ self.layout_mode ], item )
#            view = self.getActiveView()
#            if view: view.ensureVisible( item ) 

    def removeSelectedShows( self ):
        selectedShows = self.selectedItems()
        for show in selectedShows:
            self.removeShow( show.id )
        
    def removeShow( self, showId ):
        if showId in self.showMap:
            item = self.showMap[ showId ]
            self.removeItem( item )
            del self.showMap[ showId ]
            return item
        return None

    def moveShow( self, showId, pos ):
        showItem = self.showMap.get( showId, None )
        if showItem:
            index = self.getPositionIndex( pos )
            self.clearSpaceAndAddItem( index, showItem )
            showItem.setSelected(True)
        return showItem

    def renameShow( self, oldShowId, newShowId ):
        item = self.showMap.get( oldShowId, None )
        if item:
            del self.showMap[ oldShowId ]
            newItem = self.showMap.get( newShowId, None )
            self.idList.remove(oldShowId)
            if not newItem:
                self.showMap[ newShowId ] = item
                item.updateId( newShowId )
                self.idList.append( newShowId )
                
    def getNextItemPosition(self):
        position = self.getGridPos( self.initLayoutItemCoords[self.layout_mode] )
        if self.layout_mode == GRID_MODE:
            self.initLayoutItemCoords[self.layout_mode][0] = self.initLayoutItemCoords[self.layout_mode][0] + 1
            if self.initLayoutItemCoords[self.layout_mode][0] >= self.gridDims[ self.layout_mode ][0]:
                self.initLayoutItemCoords[self.layout_mode][0] = 0 
                self.initLayoutItemCoords[self.layout_mode][1] = self.initLayoutItemCoords[self.layout_mode][1] + 1 
        elif self.layout_mode == LIST_MODE:
            self.initLayoutItemCoords[self.layout_mode][1] = self.initLayoutItemCoords[self.layout_mode][1] + 1
            if self.initLayoutItemCoords[self.layout_mode][1] >= self.gridDims[ self.layout_mode ][1]:
                self.initLayoutItemCoords[self.layout_mode][1] = 0 
                self.initLayoutItemCoords[self.layout_mode][0] = self.initLayoutItemCoords[self.layout_mode][0] + 1 
        return position
                   
    def createShowItem( self, showId, pixmap, active ):
        item = self.showMap.get( showId, None )
        if item == None:
            item = ShowItem( showId, pixmap, active  )
            item.setFlags( QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable )
            self.addItem(item)
            self.showMap[ showId ] = item
            self.idList.append( showId )
        else: 
            item.updatePixmap( pixmap )
        self.clearSelection()
        item.setSelected(True)
        return item 

    def getShowItem( self, showId ):
        return self.showMap.get( showId , None )

    def updateShowItem( self, showRec ):
        item = self.showMap.get( showRec.id , None )
        if item:   item.updatePixmap( showRec.pixmap )
        else:      item = self.createShowItem( showRec.id, showRec.pixmap, showRec.isActive() )
        item.update()  
        return item         

    def clearOvelap( self, gridCoords ):
        gridPos = self.getGridPos( gridCoords )
        currentItems  = self.items( gridPos )
        N = len( currentItems )
#        print "clearOvelap-%s: N = %d" % ( str(gridCoords), N )
        if N > 1 :
            dpos = ( 1, 0 ) if ( (self.growDirection == Qt.Horizontal) and ( self.layout_mode == GRID_MODE ) ) else ( 0, 1 )
            newGridCoords = ( gridCoords[0] + dpos[0], gridCoords[1] + dpos[1] ) 
            newGridIndex = self.getGridPositionIndex( newGridCoords )
            self.updatePageSize( newGridCoords )
            firstItem = None
            for currentItem in currentItems:
                if firstItem == None:   firstItem = currentItem
                else:                   currentItem.configurePosition( self.layout_mode, newGridIndex, True )

    def clearSpaceAndAddItem( self, index, showItem ):
        gridCoords =  self.getGridCoords( index ) 
        offset = 20.0 if self.layout_mode == GRID_MODE else 2.0
        gridPos = self.getGridPos( gridCoords, offset )
#        print " --> clearSpaceAndAddItem[%s]: gridPos=%s, gridCoords=%s" % ( showItem.id, pt2str( gridPos ), str( gridCoords ) )
        currentItems  = self.items( gridPos )
        for currentItem in currentItems:
            if currentItem <> showItem:
                dpos = ( 1, 0 ) if ( (self.growDirection == Qt.Horizontal) and ( self.layout_mode == GRID_MODE ) ) else ( 0, 1 )
                newGridCoords = ( gridCoords[0] + dpos[0], gridCoords[1] + dpos[1] ) 
                newGridIndex = self.getGridPositionIndex( newGridCoords )
                self.updatePageSize( newGridCoords )
                self.clearSpaceAndAddItem( newGridIndex, currentItem ) 
        showItem.configurePosition( self.layout_mode, index, True )
#           print " Clear Pos[%s]: position=%s gridCoords=%s gridPos=%s newGridPos=%s newGridCoords=%s " % ( currentItem.id, strPos(position), str(gridCoords), strPos(gridPos), strPos(newGridPos), str(newGridCoords) )
#           print " ----->>> move %s to %s " % ( currentItem.id, strPos(newGridPos) )
        return gridPos
    
class ShowItem(QGraphicsItem):
    borderSize = 5
    itemBuffer = 4
    textBoxWidth = 300
    textBoxHeight = 32

    def __init__(self, showId, pixmap, active, matrix=QMatrix()):
        super(ShowItem, self).__init__()
        self.setFlags( QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable )
        self.setAcceptTouchEvents ( True )
        self.dragStartPosition = None
        self.id = showId
        self.active = active
        self.pixmap = pixmap
        self.setMatrix( matrix )
        self.showManager = showManager
        self.positionIndex = {}
        self.setPos( 0, 0 )
      
#    def setPos( self, position ):  
#        print " setPos[%s]: %s" % ( self.id, str(position))
#        super(ShowItem, self).setPos( position )

#    def contains( self, point ):
#        displayMode= self.getDisplayMode()
#        if displayMode == GRID_MODE: 
#            print str( [ point.x(), point.y() ] )
#        return QGraphicsItem.contains( self, point )

    def getDisplayMode(self):
        return self.scene().getLayoutMode()

    def updateId(self, showId ):
        self.id = showId
        self.update()
        
    def updatePixmap( self, pixmap ):
        self.pixmap = pixmap 
        self.update()

    def touchEvent( self, scenePos, event ):
        print " -- ShowItem Touch Event, id=%s, pos = %s, class = %s " % ( self.id, strPos( scenePos ), str( event.__class__ ) )

    def sceneEvent ( self, event  ):
        return super(ShowItem, self).sceneEvent( event )
           
#    def boundingRect1(self):
#        rect = None
#        displayMode= self.getDisplayMode()
#        if displayMode == GRID_MODE: rect = QRectF( -1, -1, LargeIconSize.width() + 2*self.borderSize+1, LargeIconSize.height() + 2*self.borderSize+self.textBoxHeight+1 )
#        if displayMode == LIST_MODE: rect = QRectF( -1, -1, SmallIconSize.width() + 2*self.borderSize+1 + 2*self.textBoxWidth+1, SmallIconSize.height() + 2*self.borderSize )
#        return rect

    def boundingRect(self):
        rect = None
        displayMode= self.getDisplayMode()
        if displayMode == GRID_MODE: rect = QRectF( TSIZE-2, TSIZE, LargeIconSize.width() + 2*self.borderSize-TSIZE, LargeIconSize.height() + 2*self.borderSize+self.textBoxHeight-TSIZE )
        if displayMode == LIST_MODE: rect = QRectF( -1, -1, SmallIconSize.width() + 2*self.borderSize+1 + 2*self.textBoxWidth+1, SmallIconSize.height() + 2*self.borderSize )
        return rect

    @classmethod
    def gridSize(cls, mode ):
        size = None
        if mode == GRID_MODE: size = ( LargeIconSize.width() + 2*cls.borderSize+1, LargeIconSize.height() + 2*cls.borderSize + cls.textBoxHeight+1 )
        if mode == LIST_MODE: size = ( SmallIconSize.width() + 2*cls.borderSize+1 + 2*cls.textBoxWidth +1, SmallIconSize.height() + 2*cls.borderSize )
        return size

    @classmethod
    def gridSpacing(cls, mode ):
        size = cls.gridSize( mode )
        return ( size[0] + cls.itemBuffer, size[1] + cls.itemBuffer )
       
    def parentWidget(self):
        return self.scene().views()[0]
    
    def initPositionIndex( self, index ):
        for displayMode in [ GRID_MODE, LIST_MODE ]:
            self.positionIndex[displayMode] = index

    def initPositionIndices( self, indices ):
        for displayMode in [ GRID_MODE, LIST_MODE ]:
            self.positionIndex[displayMode] = indices[ displayMode ]

    def getPositionIndexList( self, plist = [] ):
        for displayMode in [ GRID_MODE, LIST_MODE ]: plist.append( str( self.positionIndex.get(displayMode,0) ) )
        return plist

    def getPositionIndex( self, displayMode ):
        return self.positionIndex[displayMode]
    
    def configurePosition( self, displayMode, index, effectiveImmediately = False ):
        self.positionIndex[displayMode] = index
        if effectiveImmediately: 
            pos = self.scene().getPositionFromIndex( index )
            self.setPos( pos )
    
    def updatePosition( self, displayMode ):
        if not self.scene().mouseDown:
            index = 0
            try:    index = self.positionIndex[ displayMode ]
            except: self.positionIndex[ displayMode ] = index
            pos = self.scene().getPositionFromIndex( index )
            self.setPos( pos )
#            self.scene().clearSpaceAndAddItem( index, self )
            
#            currentItem = self.scene().itemAt( pos )
#            if currentItem <> self: self.scene().clearSpaceAndAddItem( index, self, currentItem )
#            else: self.setPos( pos )            
 
    def paint(self, painter, option, widget):
#        print " --> paint[%s]: %s " % ( self.id, str( self.scene().getItemIds() )  )
        displayMode = self.getDisplayMode()
        self.updatePosition( displayMode )
        if self.active == 0: 
            self.setOpacity( 0.5 )
            painter.fillRect( self.boundingRect(), QColor( 150, 150, 150) )
        else:
            if option.state & QStyle.State_Selected:
                painter.fillRect( self.boundingRect(), QColor( 0xff, 0xff, 0xb0, 0xd0 ) )
            else:
                painter.fillRect( self.boundingRect(), QColor( 0xff, 0xff, 0xff, 0xcc ) )
            
        if displayMode == GRID_MODE: 
            painter.drawPixmap ( self.borderSize, self.borderSize+self.textBoxHeight, LargeIconSize.width(), LargeIconSize.height(), self.pixmap )
            painter.drawText( QRectF( self.borderSize, self.borderSize, LargeIconSize.width(), self.textBoxHeight ), Qt.TextWordWrap|Qt.AlignLeft, QString( self.id ) )
        if displayMode == LIST_MODE: 
            showRec = self.showManager.getShowRecord( self.id )
            painter.drawPixmap ( self.borderSize, self.borderSize, SmallIconSize.width(), SmallIconSize.height(), self.pixmap )
            painter.drawText( QRectF( 2*self.borderSize + SmallIconSize.width(), self.borderSize, self.textBoxWidth, SmallIconSize.height() ), Qt.TextWordWrap|Qt.AlignLeft, QString( self.id ) )
            painter.drawText( QRectF( 2*self.borderSize + SmallIconSize.width() + self.textBoxWidth, self.borderSize, self.textBoxWidth, SmallIconSize.height() ), Qt.TextWordWrap|Qt.AlignLeft, QString( showRec.title ) )
        pen = QPen( Qt.SolidLine )
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            pen.setColor(Qt.blue)
        painter.setPen(pen)
        painter.drawRect( self.boundingRect() )
        
    def getScaledPixmap( self, size=None ):
        size = size if size else SmallIconSize
        return self.pixmap.scaled( size.width(), size.height() )
    
    def runShow(self):
        showRec = self.showManager.getShowRecord( self.id )
        if not showRec:
            msgBox = QMessageBox()
            msgBox.setText( " RunShow: Can't find show: %s " % self.id)
            msgBox.exec_()
            print>>sys.stderr, "RunShow: Can't find show: ", self.id
            return
        if not showRec.isActive():
            msgBox = QMessageBox()
            msgBox.setText(" This show has been moved (new location unknown). ")
            msgBox.exec_()
            return 
        self.showManager.runShow( showRec )

    def mouseDoubleClickEvent(self, event):
        self.runShow()

    def mouseReleaseEvent ( self, event ):
        self.dragStartPosition = None
        super( ShowItem, self ).mouseReleaseEvent( event )
        index = self.scene().getPositionIndex( self.pos() )  
        self.scene().clearSpaceAndAddItem( index, self )

    def contextMenuEvent ( self, event ):
        parent = self.parentWidget()
        menu = QMenu( parent )
        editAction = menu.addAction("Edit")
        removeAction = menu.addAction("Remove")  
        renameAction = menu.addAction("Rename")  
        editAction.connect( editAction, SIGNAL('triggered(bool)'),  self.edit )
        removeAction.connect( removeAction, SIGNAL('triggered(bool)'),  self.remove )
        renameAction.connect( renameAction, SIGNAL('triggered(bool)'),  self.rename )
        menu.move( event.screenPos() )                 
        menu.show()
        
    def edit( self, checked ):
        print "edit"

    def remove( self, checked ):
        scene = self.scene()
        if scene: scene.showManager.removeShow( self.id )

    def rename( self, checked ):
        scene = self.scene()
        if scene: 
            new_name, ok = QInputDialog.getText( None, "Rename Show Dialog", "New Show Name:", QLineEdit.Normal, self.id )
            if ok and new_name: scene.showManager.renameShow( self.id, new_name )
 
    def mousePressEvent ( self, event ):
        if isTouchEvent( event ):
            print "GraphicsItem Mouse Touch Event, pos = %s, class = %s " % ( strPos( event.pos() ), str( event.__class__ ) )
        scene = self.scene()
        scene.setSelectedItem( self )
        print " showDocs: scene=%s, item=%s " % ( str( id(scene) ), self.id  )
        super(ShowItem, self).mousePressEvent(event)
        
    def mouseMoveEvent ( self, event ):
        super(ShowItem, self).mouseMoveEvent(event)
        collidingShowItems = self.collidingItems()
        for item in collidingShowItems: item.stackBefore(self)
    
    def keyPressEvent(self, event):
        changed = False
        if event.key() == Qt.Key_Left:
            pass
        elif event.key() == Qt.Key_Right:
            pass
        elif event.key() == Qt.Key_Up:
            pass
        elif event.key() == Qt.Key_Down:
            pass
        if changed:
            self.update()
        else:
            super(ShowItem, self).keyPressEvent(event)
           
class ShowGridWidget(QWidget):

    def __init__( self, name, showManager, parent, role, **args ):
        super(ShowGridWidget, self).__init__(parent)
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.showManager = showManager
        self.Dirty = False
        self.scene = None
        self.role = role
        self.views = {}
        self.ncols = args.get( 'ncols', [ 6, 2 ] )
        
        layout = QHBoxLayout()
        self.tabWidget = QTabWidget( self )
        layout.addWidget( self.tabWidget )
        view = GraphicsView( name, GRID_MODE, self.tabWidget, role=self.role, ncols=self.ncols[GRID_MODE] )         
        self.iGridTab = self.tabWidget.addTab( view, 'grid' )
        self.views[ self.iGridTab ] = view
        view = GraphicsView( name, LIST_MODE, self.tabWidget, role=self.role, ncols=self.ncols[LIST_MODE] )   
        self.iListTab = self.tabWidget.addTab( view, 'list' )
        self.views[ self.iListTab ] = view
        self.tabWidget.setCurrentIndex ( self.iGridTab )
#        tabWidget.setTabEnabled ( self.iGridTab, True )
#        tabWidget.setTabEnabled ( self.iListTab, False )
        self.tabWidget.connect( self.tabWidget, SIGNAL('currentChanged(int)'), self.tabSelectionChanged )
        self.tabWidget.setTabIcon( self.iListTab, loadIcon( 'list' ) )
        self.tabWidget.setTabIcon( self.iGridTab, loadIcon( 'grid' ) )
        self.tabWidget.setIconSize( QSize( 32, 32 ) )
#        self.list.setSelectionMode( QAbstractItemView.SingleSelection )
#        self.connect( self.list, SIGNAL( "currentRowChanged(int)" ), self.selectShow )
#        self.connect( self.list, SIGNAL( 'executeItem(int)' ), self.executeShow )
#        self.connect( self.list, SIGNAL( 'dragItem(int)' ), self.dragShow ) 
#        self.connect( self.list, SIGNAL( 'dropItem(QString)' ), self.addShow )         
#        self.list.setFont( QFont("Courier", 18 ) ) # , QFont.Bold) )
#        self.list.setGridSize( QSize ( 500, 64 ) )
#        self.list.setIconSize ( QSize( 64, 64 ) )
##        self.list.setBackgroundRole( QPalette.AlternateBase  )
        self.setLayout(layout)
        
    def getView(self):
        return self.views[ self.tabWidget.currentIndex() ]
    
    def scroll ( self, dx, dy ):
        view = self.views[ self.tabWidget.currentIndex() ]
        hsb, vsb = view.horizontalScrollBar(), view.verticalScrollBar()
        dxs = dx * ( hsb.maximum () - hsb.minimum() )
        dys = dy * ( vsb.maximum () - vsb.minimum() )
        hsb.setValue ( hsb.value() + int(round(dxs)) )
        vsb.setValue ( vsb.value() + int(round(dys)) )
#        print " --- Scroll: (%.4f,%.4f) (%.2f,%.2f) (%d,%d) " % ( dx, dy, dxs, dys, hsb.value(), vsb.value() )
    
    def ensureVisible( self, item ):
        view = self.views[ self.tabWidget.currentIndex() ]
        view.ensureVisible( item )
    
    def getTabIndex(self):    
        return self.tabWidget.currentIndex()
    
    def getLayoutMode(self):  
        tabIndex =  self.getTabIndex() 
        if tabIndex == self.iGridTab: return GRID_MODE
        if tabIndex == self.iListTab: return LIST_MODE
        return -1
       
    def getShowId( self, iRow  ):
        return self.showList[ iRow ]

    def selectShow( self, iRow ):
        showId = self.showList[ iRow ]
        showRec = self.showManager.getShowRecord( showId )
        self.scene.setSelectedItem( showRec )

    def executeShow( self, iRow ):
        showId = self.showList[ iRow ]
        showRec = self.showManager.getShowRecord( showId )
        if not showRec:
            print>>sys.stderr, "RunShow: Can't find show: ", showId
            return
        if not showRec.isActive():
            msgBox = QMessageBox()
            msgBox.setText(" This show has been moved (new location unknown). ")
            msgBox.exec_()
            return 
        self.showManager.runShow( showRec )
        
    def updateView(self):
        self.tabSelectionChanged( self.getTabIndex() )
        
    def tabSelectionChanged(self, iTab ):
        print "______________________________________________________ TAB %d __________________________________________________________" % iTab
        view = self.views[ iTab ]
        view.setScene( self.scene )
        pageSize = self.scene.getPageSize()
        self.scene.setSceneRect( 0, 0, pageSize[0], pageSize[1] )
        view.setFocus()
        view.update()
                      
    def buildShowList(self):
        itemList =  self.scene.items()
        self.showList = []
        maxLen = 0
        for item in itemList:
            self.showList.append( item.id )
            if len( item.id ) > maxLen: maxLen = len( item.id )
        self.showList.sort()
        listData = []
        for iShowIndex in range( len(self.showList) ):
            showId = self.showList[ iShowIndex  ]
            showRec = self.showManager.getShowRecord( showId )
            pixmap = showRec.pixmap
            title = showRec.getTitle()
            nspaces = maxLen - len( showId ) + 5
            text = " %s:%s%s " % ( showId, ' '*nspaces, title )
            listData.append( ( showId, pixmap, text ) )
        self.list.updateListData( listData  )
            
    def dragShow ( self, iRow ):
        if iRow < 0: return
        showId = self.showList[ iRow ]
        showRec = self.showManager.getShowRecord( showId )
        drag = QDrag( self.list )
        mimeData = QMimeData()
        drag.setMimeData( mimeData )
        mimeData.setText( showRec.id )
        drag.setPixmap( showRec.pixmap )
#            drag.setHotSpot( getQPoint( event.scenePos() - currentItem.pos() )  )
        drag.exec_( Qt.CopyAction |  Qt.MoveAction,  Qt.CopyAction)

#    def event ( self, event ):
#        print " ShowGridWidget event, type = %d " % event.type()
#        if isTouchEvent( event ):
#                print "ShowGridWidget Touch Event, class = %s " % str( event.__class__ )
#                event.accept()
#                return True
##        print " --------> ShowGridWidget event: type = %s, class = %s " % ( str( event.type() ), str( event.__class__ ) )
#        return super(ShowGridWidget, self).event( event )
        
#    def setGridSpecs(self, gridDims, gridSpacing, growDirection ):
#        self.gridDims[ self.layout_mode ] =  gridDims
#        self.gridSpacing =  gridSpacing 
#        self.growDirection =  growDirection


    def getNewPage( self, page_name=None ):
        scene = GraphicsScene( self.showManager, page_name, self.views[ self.iGridTab ] )
        scene.setLayoutMode( self.getLayoutMode() )
        return scene
        
    def addPage(self, page_name, setCurrent=True ):
        scene = self.getNewPage( page_name )
        self.showManager.addPage( scene )
        if setCurrent: self.setCurrentScene( scene ) 
        return scene
         
    def setCurrentPage(self, page_name ):
        print " Set Current Page: ", page_name
        scene = self.showManager.getPage( page_name )
        self.setCurrentScene( scene )
        return scene

    def setCurrentScene( self, scene ):
        if scene:
            self.scene = scene
            view = self.views[ self.tabWidget.currentIndex() ]
            view.setScene( self.scene )
            view.resetScroll()
        else: print>>sys.stderr, "Error, unrecognized page!"
        
    def clear(self):
        if self.scene:
            items = self.scene.items()
            while items:
                item = items.pop()
                self.scene.removeItem(item)
                del item
                                    
    def initShowLists( self ):
        self.addPage( 'global' )
        showIds = self.showManager.getShowIds()
        sortedShowIds = sorted( showIds, key=str.lower )  
        posIndex = 0      
        for showId in sortedShowIds:
            item = self.addShow( showId, False )
            item.initPositionIndex( posIndex )
            posIndex = posIndex + 1     
        self.showManager.restorePages( self ) 
        
    def addShow( self, showId, rebuild=True ):                                   
        showRec = self.showManager.getShowRecord( str(showId) )
        item = self.scene.createShowItem(  showRec.id, showRec.getPixmap(), showRec.isActive() ) 
#        self.views[ self.tabWidget.currentIndex() ].ensureVisible( item ) 
        if rebuild: self.buildShowList() 
        return item  

#class TestForm(QDialog):
# 
#    def __init__(self, configParser, parent=None):
#        super(TestForm, self).__init__(parent)
#        self.showManager = HWShowManager( configParser )
#        self.setupGui()
#        
#    def setupGui(self):
#        layout = QVBoxLayout()
#        self.setLayout(layout)
#        self.showGridWidget = ShowGridWidget( 'test', self.showManager )
#        layout.addWidget( self.showGridWidget )

#if __name__ == '__main__':  
#    shrink_factor = 0.8
#    showCfg = HWShowConfigReader( "HyperwallShowList.txt" )                                              
#    app = QApplication(sys.argv)
#    form = TestForm( showCfg )
#    rect = QApplication.desktop().availableGeometry()
#    form.resize(int(rect.width()*shrink_factor), int(rect.height()*shrink_factor))
#    form.show()
#    app.exec_()