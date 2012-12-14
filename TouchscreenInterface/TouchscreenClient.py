#!/usr/bin/python -u
"""
Touchscreen interface
"""
from touch import *
import time, threading, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
TOUCH_UP_EVENT = 1
TOUCH_DOWN_EVENT = 2
TOUCH_MOVE_EVENT = 3
OFFSETX = 0
OFFSETY = 0

#TOUCH_UP_EVENT_TYPE   = QEvent.registerEventType ( QEvent.User + 1 )
#TOUCH_DOWN_EVENT_TYPE = QEvent.registerEventType ( QEvent.User + 2 )
#TOUCH_MOVE_EVENT_TYPE = QEvent.registerEventType ( QEvent.User + 3 )

class Observer(object):
    def __init__(self, subject):
        self.dispatcher = subject
        subject.push_handlers(self)

class touch_up(Observer):
    def TOUCH_UP(self,blobID, xpos, ypos):
        self.dispatcher.passTouchEventToQt( TOUCH_UP_EVENT, blobID, pos = [ xpos, ypos ] )

class touch_down(Observer):
    def TOUCH_DOWN(self,blobID):
        self.dispatcher.passTouchEventToQt( TOUCH_DOWN_EVENT, blobID )

class touch_move(Observer):
    def TOUCH_MOVE(self,blobID):
        self.dispatcher.passTouchEventToQt( TOUCH_MOVE_EVENT, blobID )

def getTouchQEventType( type ):
    if type == TOUCH_UP_EVENT: return QEvent.MouseButtonRelease
    if type == TOUCH_DOWN_EVENT: return QEvent.MouseButtonPress
    if type == TOUCH_MOVE_EVENT: return QEvent.MouseMove
    return -1

def getTouchQEventString( type ):
    if type == TOUCH_UP_EVENT: return 'TOUCH_UP_EVENT'
    if type == TOUCH_DOWN_EVENT: return 'TOUCH_DOWN_EVENT'
    if type == TOUCH_MOVE_EVENT: return 'TOUCH_MOVE_EVENT'
    return ''

#
#def getTouchEventType( type ):
#    if type == TOUCH_UP_EVENT:   return QEvent.Type(TOUCH_UP_EVENT_TYPE)
#    if type == TOUCH_DOWN_EVENT: return QEvent.Type(TOUCH_DOWN_EVENT_TYPE)
#    if type == TOUCH_MOVE_EVENT: return QEvent.Type(TOUCH_MOVE_EVENT_TYPE)
#    return -1

def strPos( pos ):
    return " [ %s, %s ] " % ( str(pos.x()), str(pos.y()) )
                              
#def isTouchEvent( event ):
#    type = int( event.type() )
#    return ( type == TOUCH_UP_EVENT_TYPE ) or ( type == TOUCH_DOWN_EVENT_TYPE ) or ( type == TOUCH_MOVE_EVENT_TYPE ) 

def isTouchEvent( event ):
    className = event.__class__.__name__
    if className == "TouchEvent": return True
    try:    return event.modifiers() & Qt.MetaModifier
    except: return False

def getChildWidget( topWidget, screenPos ):
    parent = topWidget 
    while True:
        windowPos = parent.mapFromGlobal( screenPos ) 
        child = parent.childAt( windowPos )
        if child: parent = child
        else: return parent, windowPos

def postTouchEvent ( topWidget, screenPos ):
    childWidget, localPos =  getChildWidget( topWidget, screenPos )
    touch_event = TouchEvent( TOUCH_DOWN_EVENT, 1, localPos, screenPos, 2 ) 
    print "Posting touch down event to app at %s " % str( localPos )
    QApplication.postEvent( childWidget, touch_event )
    
#class TouchEvent( QEvent ):
#
#    def __init__( self, type, id, screenPos, cardinality, **args ):
#        QInputEvent.__init__( self, type  )
#        self.screenPos = screenPos
#        self.localPos = None
#        self.id = id
#        self.cardinality = cardinality
#        self.touch_mgr = args.get( 'mgr', None )

class Gesture( QObject ):
    def __init__( self, cardinality, **args ):
        self.cardinality = cardinality
        self.touch_mgr = args.get( 'mgr', None )
        self.targetScene = None
        self.targetList = None
        self.targetPos = None
        
class TouchEvent( QMouseEvent ):

    def __init__( self, ttype, tid, localPos, screenPos, gesture, **args ):
        QMouseEvent.__init__( self, getTouchQEventType( ttype ), localPos, screenPos, Qt.RightButton, Qt.RightButton, Qt.MetaModifier )
        self.id = tid
        self.gesture = gesture
    
class TouchscreenManager( touchpy ):
    
    def __init__( self, mainWindow, app, host='127.0.0.1', port = 3333  ):
        touchpy.__init__( self, host, port  )
        self.app = app
        self.screenRect = self.app.desktop().availableGeometry()
        self.mainWindow = mainWindow
        self.qTouchPointMap = {}
        self.client = TouchscreenClient( self )
        self.client.start()
           
    def getNTouchPoints(self):
        return len( self.blobs )
    
    def shutdown(self):
        self.client.shutdown()
        
    def passTouchEventToQt( self, type, blobID, **args ):
        if  (type == TOUCH_DOWN_EVENT) or (type == TOUCH_UP_EVENT) or (type == TOUCH_MOVE_EVENT) :
            n_points = len( self.alive )
            if (n_points > 1):
                gesture = Gesture( n_points, mgr=self )
                for blobID in self.alive:
                    touch_point = self.blobs[blobID]
                    pos = args.get('pos', [ touch_point.xpos, touch_point.ypos ] )        
                    normPos = QPointF( pos[0], pos[1] )
                    screenPos = QPointF( self.screenRect.width() * normPos.x() - OFFSETX, self.screenRect.height() * normPos.y() - OFFSETY ).toPoint() 
                    
                    childWidget, localPos =  getChildWidget( self.mainWindow, screenPos )
                    touch_event = TouchEvent( type, blobID, localPos, screenPos, gesture ) 
#                    print 'Touch event %s [%d:%d] detected: screenPos = %s, localPos = %s ' % ( getTouchQEventString(type), blobID, n_points, strPos( screenPos ), strPos( localPos ) )                    
                    QApplication.postEvent( childWidget, touch_event ) 
                             
#
#        touchPoint = QTouchEvent.TouchPoint( blobID )
#
#        touchPoint.setNormalizedPos(normPos)
#        touchPoint.setRect(QRectF())
#
#        touchPoint.setPressure(1.0);
#        touchPoint.setScreenRect(self.screenRect)
#        touchPoint.setScreenPos(screenPos)

#    if (theScene) {
#        touchPoint.setSceneRect(theScene->sceneRect());
#        if (theView) {
#            const QPoint pos((int)screenPos.x() - theView->geometry().x(),
#                             (int)screenPos.y() - theView->geometry().y());
#            touchPoint.setPos(pos);
#            touchPoint.setScenePos(theView->mapToScene(pos));
#        } else {
#            foreach (QGraphicsView *view, theScene->views()) {
#                if (view->isActiveWindow()) {
#                    const QPoint pos((int)screenPos.x() - view->geometry().x(),
#                                     (int)screenPos.y() - view->geometry().y());
#                    touchPoint.setPos(pos);
#                    touchPoint.setScenePos(view->mapToScene(pos));
#                }
#            }
#        }
#    } else {
#        pos = QPoint ( int(screenPos.x()) - self.mainWindow.geometry().x(), int(screenPos.y()) - self.mainWindow.geometry().y() )
#        touchPoint.setPos(pos)
#        touchPoint.setSceneRect( QRectF() )
#        touchPoint.setScenePos(pos)
##    }
#        touchPointStates = 0
#        eventType = self.getEventType( type, blobID )
#        
#        if eventType == QEvent.TouchBegin: 
#            touchPointStates = Qt.TouchPointPressed
#
#            touchPoint.setState(Qt.TouchPointPressed)
#            touchPoint.setStartNormalizedPos(normPos)
#            touchPoint.setStartPos(touchPoint.pos())
#            touchPoint.setStartScreenPos(screenPos)
#            touchPoint.setStartScenePos(touchPoint.scenePos())
#
#            touchPoint.setLastNormalizedPos(normPos)
#            touchPoint.setLastPos(touchPoint.pos())
#            touchPoint.setLastScreenPos(screenPos)
#            touchPoint.setLastScenePos(touchPoint.scenePos())
#            
#
#            qTouchPointMap[blobID] = touchPoint
#            
#        elif eventType == QEvent.TouchUpdate:
##            if tcur.getMotionSpeed() > 0:
#            touchPointStates = Qt.TouchPointMoved
#            touchPoint.setState(Qt.TouchPointMoved)
##            else:
##                touchPointStates = Qt.TouchPointStationary
##                touchPoint.setState(Q.TouchPointStationary)
#            touchPoint.setStartNormalizedPos(qTouchPointMap[blobID].startNormalizedPos())
#            touchPoint.setStartPos(qTouchPointMap[blobID].startPos())
#            touchPoint.setStartScreenPos(qTouchPointMap[blobID].startScreenPos())
#            touchPoint.setStartScenePos(qTouchPointMap[blobID].startScenePos())
#
#            touchPoint.setLastNormalizedPos(qTouchPointMap[blobID].normalizedPos())
#            touchPoint.setLastPos(qTouchPointMap[blobID].pos())
#            touchPoint.setLastScreenPos(qTouchPointMap[blobID].screenPos())
#            touchPoint.setLastScenePos(qTouchPointMap[blobID].scenePos())
#
#            qTouchPointMap[blobID] = touchPoint
#            
#        elif eventType == QEvent.TouchEnd: 
#            touchPointStates = Qt.TouchPointReleased
#            touchPoint.setState(Qt.TouchPointReleased)
#
#            touchPoint.setStartNormalizedPos(qTouchPointMap[blobID].startNormalizedPos())
#            touchPoint.setStartPos(qTouchPointMap[blobID].startPos())
#            touchPoint.setStartScreenPos(qTouchPointMap[blobID].startScreenPos())
#            touchPoint.setStartScenePos(qTouchPointMap[blobID].startScenePos())
#
#            touchPoint.setLastNormalizedPos(qTouchPointMap[blobID].normalizedPos())
#            touchPoint.setLastPos(qTouchPointMap[blobID].pos())
#            touchPoint.setLastScreenPos(qTouchPointMap[blobID].screenPos())
#            touchPoint.setLastScenePos(qTouchPointMap[blobID].scenePos())
#
#            qTouchPointMap[blobID] = touchPoint
#
#        touchEvent = QTouchEvent(eventType, QTouchEvent.TouchScreen, Qt.NoModifier, touchPointStates, qTouchPointMap.values() )
#        self.app.postEvent( self.mainWindow.centralWidget(), touchEvent )
#        if (eventType == QEvent.TouchEnd): del qTouchPointMap[blobID]
#
#        return true


#/**********************************************************
#* Old Code doesn't work with QGraphicsView
#* it doesn't send events to the viewport
#* and which make the pinchzoom example doesn't work
#***********************************************************/
#/* if (theScene)
#qApp->postEvent(theScene, touchEvent)
#else if (theView)
#qApp->postEvent(theView->scene(), touchEvent)
#else
#qApp->postEvent(theMainWindow->centralWidget(), touchEvent)*/
#
#/************************************************
#* New code fixing the issue with QGraphicsViw
#*************************************************/
#
#if (theView && theView->viewport())
#        qApp->postEvent(theView->viewport(), touchEvent)
#    else if (theScene)
#        qApp->postEvent(theScene, touchEvent)
#    else
#        qApp->postEvent(theMainWindow->centralWidget(), touchEvent)
#
#
#    if (eventType == QEvent::TouchEnd)
#        qTouchPointMap->remove(tcur->getSessionID())
#
#    return true
#}
#
#        
#        
        
#        touch_point_list = QList ()
#        blobIds = self.blobs.keys()
#        blobIds.sort()
#        for blobID in blobIds:
#            blob = self.blobs[blobID]
#            
#        if type == TOUCH_UP_EVENT:
#            if len( self.blobs ) == 1:
#                
#                event = QTouchEvent( QEvent.TouchBegin, QTouchEvent.TouchScreen, Qt.NoModifier, Qt.TouchPointPressed, touch_point_list)
#                
    
    
class TouchscreenClient( threading.Thread ):
    
    def __init__( self, touchMgr ):
        threading.Thread.__init__( self )
        self.touchMgr = touchMgr
        self.isActive = True
        self.daemon = True
              
    def shutdown(self):
        self.isActive = False
    
    def run(self):
                
        tu = touch_up(self.touchMgr)
        td = touch_down(self.touchMgr)
        tm = touch_move(self.touchMgr)
        
        try:
            while self.isActive:
                self.touchMgr.update()
                time.sleep(0.1)
        
        except (KeyboardInterrupt, SystemExit):
            return
        
if __name__ == '__main__':  
    app = QApplication(sys.argv)
    tc = TouchscreenClient()
    tc.start()
    app.exec_()    
        
        
#QTuio::QTuio(QObject *parent)
#{
#    theMainWindow = qobject_cast<QMainWindow *>(parent)
#    theView = qobject_cast<QGraphicsView *>(parent);
#    if (theView)
#        theScene = theView->scene();
#    else
#        theScene = qobject_cast<QGraphicsScene *>(parent);
#}
#
#QTuio::~QTuio()
#{
#    if (running) {
#        tuioClient->disconnect();
#        delete tuioClient;
#        delete qTouchPointMap;
#        running = false;
#        wait();
#    }
#}
#
#
#void QTuio::run()
#{
#    running = true;
#    screenRect = QApplication::desktop()->rect();
#// tuioClient = new TUIO::TuioClient::TuioClient(3333);
#    tuioClient = new TUIO::TuioClient(3333);
#    tuioClient->addTuioListener(this);
#    tuioClient->connect();
#    qTouchPointMap = new QMap<int, QTouchEvent::TouchPoint>();
#}
#
#
#void QTuio::addTuioObject(TUIO::TuioObject *tobj) {}
#
#void QTuio::updateTuioObject(TUIO::TuioObject *tobj) {}
#
#void QTuio::removeTuioObject(TUIO::TuioObject *tobj) {}
#
#
#bool QTuio::tuioToQt(TUIO::TuioCursor *tcur, QEvent::Type eventType)
#{
#    const QPointF normPos(tcur->getX(), tcur->getY());
#    const QPointF screenPos(screenRect.width() * normPos.x() - OFFSETX, screenRect.height() * normPos.y() - OFFSETY);
#
#    QTouchEvent::TouchPoint touchPoint(tcur->getSessionID());
#
#    touchPoint.setNormalizedPos(normPos);
#    touchPoint.setRect(QRectF());
#
#    touchPoint.setPressure(1.0);
#    touchPoint.setScreenRect(screenRect);
#    touchPoint.setScreenPos(screenPos);
#
#    if (theScene) {
#        touchPoint.setSceneRect(theScene->sceneRect());
#        if (theView) {
#            const QPoint pos((int)screenPos.x() - theView->geometry().x(),
#                             (int)screenPos.y() - theView->geometry().y());
#            touchPoint.setPos(pos);
#            touchPoint.setScenePos(theView->mapToScene(pos));
#        } else {
#            foreach (QGraphicsView *view, theScene->views()) {
#                if (view->isActiveWindow()) {
#                    const QPoint pos((int)screenPos.x() - view->geometry().x(),
#                                     (int)screenPos.y() - view->geometry().y());
#                    touchPoint.setPos(pos);
#                    touchPoint.setScenePos(view->mapToScene(pos));
#                }
#            }
#        }
#    } else {
#        const QPoint pos((int)screenPos.x() - theMainWindow->geometry().x(),
#                         (int)screenPos.y() - theMainWindow->geometry().y());
#        touchPoint.setPos(pos);
#        touchPoint.setSceneRect(QRectF());
#        touchPoint.setScenePos(pos);
#    }
#
#    Qt::TouchPointStates touchPointStates;
#
#    switch (eventType) {
#    case QEvent::TouchBegin: {
#touchPointStates = Qt::TouchPointPressed;
#
#            touchPoint.setState(Qt::TouchPointPressed);
#            touchPoint.setStartNormalizedPos(normPos);
#            touchPoint.setStartPos(touchPoint.pos());
#            touchPoint.setStartScreenPos(screenPos);
#            touchPoint.setStartScenePos(touchPoint.scenePos());
#
#            touchPoint.setLastNormalizedPos(normPos);
#            touchPoint.setLastPos(touchPoint.pos());
#            touchPoint.setLastScreenPos(screenPos);
#            touchPoint.setLastScenePos(touchPoint.scenePos());
#
#            qTouchPointMap->insert(tcur->getSessionID(), touchPoint);
#            break;
#        }
#    case QEvent::TouchUpdate: {
#            if (tcur->getMotionSpeed() > 0)
#{
#                touchPointStates = Qt::TouchPointMoved;
#
#                touchPoint.setState(Qt::TouchPointMoved);
#}
#            else
#{
#                touchPointStates = Qt::TouchPointStationary;
#
#                touchPoint.setState(Qt::TouchPointStationary);
#}
#
#            touchPoint.setStartNormalizedPos(qTouchPointMap->value(tcur->getSessionID()).startNormalizedPos());
#            touchPoint.setStartPos(qTouchPointMap->value(tcur->getSessionID()).startPos());
#            touchPoint.setStartScreenPos(qTouchPointMap->value(tcur->getSessionID()).startScreenPos());
#            touchPoint.setStartScenePos(qTouchPointMap->value(tcur->getSessionID()).startScenePos());
#
#            touchPoint.setLastNormalizedPos(qTouchPointMap->value(tcur->getSessionID()).normalizedPos());
#            touchPoint.setLastPos(qTouchPointMap->value(tcur->getSessionID()).pos());
#            touchPoint.setLastScreenPos(qTouchPointMap->value(tcur->getSessionID()).screenPos());
#            touchPoint.setLastScenePos(qTouchPointMap->value(tcur->getSessionID()).scenePos());
#
#            qTouchPointMap->insert(tcur->getSessionID(), touchPoint);
#            break;
#        }
#    case QEvent::TouchEnd: {
#            touchPointStates = Qt::TouchPointReleased;
#
#            touchPoint.setState(Qt::TouchPointReleased);
#
#            touchPoint.setStartNormalizedPos(qTouchPointMap->value(tcur->getSessionID()).startNormalizedPos());
#            touchPoint.setStartPos(qTouchPointMap->value(tcur->getSessionID()).startPos());
#            touchPoint.setStartScreenPos(qTouchPointMap->value(tcur->getSessionID()).startScreenPos());
#            touchPoint.setStartScenePos(qTouchPointMap->value(tcur->getSessionID()).startScenePos());
#
#            touchPoint.setLastNormalizedPos(qTouchPointMap->value(tcur->getSessionID()).normalizedPos());
#            touchPoint.setLastPos(qTouchPointMap->value(tcur->getSessionID()).pos());
#            touchPoint.setLastScreenPos(qTouchPointMap->value(tcur->getSessionID()).screenPos());
#            touchPoint.setLastScenePos(qTouchPointMap->value(tcur->getSessionID()).scenePos());
#
#            qTouchPointMap->insert(tcur->getSessionID(), touchPoint);
#            break;
#        }
#    default: {}
#    }
#
#    QEvent *touchEvent = new QTouchEvent(eventType, QTouchEvent::TouchScreen, Qt::NoModifier, touchPointStates, qTouchPointMap->values());
#
#/**********************************************************
#* Old Code doesn't work with QGraphicsView
#* it doesn't send events to the viewport
#* and which make the pinchzoom example doesn't work
#***********************************************************/
#/* if (theScene)
#qApp->postEvent(theScene, touchEvent);
#else if (theView)
#qApp->postEvent(theView->scene(), touchEvent);
#else
#qApp->postEvent(theMainWindow->centralWidget(), touchEvent);*/
#
#/************************************************
#* New code fixing the issue with QGraphicsViw
#*************************************************/
#
#if (theView && theView->viewport())
#        qApp->postEvent(theView->viewport(), touchEvent);
#    else if (theScene)
#        qApp->postEvent(theScene, touchEvent);
#    else
#        qApp->postEvent(theMainWindow->centralWidget(), touchEvent);
#
#
#    if (eventType == QEvent::TouchEnd)
#        qTouchPointMap->remove(tcur->getSessionID());
#
#    return true;
#}
#
#
#void QTuio::addTuioCursor(TUIO::TuioCursor *tcur)
#{
#QTuio::tuioToQt(tcur, QEvent::TouchBegin);
#}
#
#void QTuio::updateTuioCursor(TUIO::TuioCursor *tcur)
#{
#QTuio::tuioToQt(tcur, QEvent::TouchUpdate);
#}
#
#void QTuio::removeTuioCursor(TUIO::TuioCursor *tcur)
#{
#QTuio::tuioToQt(tcur, QEvent::TouchEnd);
#}
#
#
#void QTuio::refresh(TUIO::TuioTime frameTime) {}


