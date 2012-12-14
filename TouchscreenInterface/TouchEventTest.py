'''
Created on Aug 17, 2011

@author: tpmaxwel
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from TouchscreenClient import *
import sys, copy, os, cdms2, traceback, copy, sip


class MainWidget( QWidget ):

    def __init__( self, parent ):
        super(MainWidget, self).__init__( parent )
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        
    def event ( self, event ):
        if isTouchEvent( event ):
                print "MainWidget Touch Event"
                event.accept()
                return True
        elif event.type() == QEvent.MouseButtonPress:
            print " --------> MainWidget MouseButtonPress: globalPos = %s, Pos = %s " % ( str( [ event.globalX(), event.globalY() ]  ), str( [ event.x(), event.y() ] ) )
        return super(MainWidget, self).event( event )        

    def mousePressEvent ( self, event ):
        print " --------> MainWidget mousePressEvent: globalPos = %s, Pos = %s " % ( str( [ event.globalX(), event.globalY() ]  ), str( [ event.x(), event.y() ] ) )       
        return super(MainWidget, self).mousePressEvent( event )       
    
class MainForm( QMainWindow ):
 
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setupGui()
        
    def event ( self, event ):
        if event.type() == QEvent.MouseButtonPress:
            print " --------> MainForm MouseButtonPress: globalPos = %s, Pos = %s " % ( str( [ event.globalX(), event.globalY() ]  ), str( [ event.x(), event.y() ] ) )
        return super(MainForm, self).event( event ) 
    
    def mousePressEvent ( self, event ):
        print " --------> MainForm mousePressEvent: globalPos = %s, Pos = %s " % ( str( [ event.globalX(), event.globalY() ]  ), str( [ event.x(), event.y() ] ) )       
        return super(MainForm, self).mousePressEvent( event )       

    def keyPressEvent ( self, event ):
        globalPos = QPoint(500,500)
        localPos = self.mapFromGlobal( globalPos ) 
        childWidget =  self.childAt( localPos )
        if childWidget: localPos = childWidget.mapFromGlobal( localPos ) 
        else: childWidget = self  
        new_event = TouchDownEvent( 1, localPos, 2 )     
#        new_event = QMouseEvent ( QEvent.MouseButtonPress, localPos, globalPos, Qt.LeftButton, Qt.LeftButton, Qt.MetaModifier )
        QApplication.postEvent( childWidget, new_event )  
#        return super(MainForm, self).keyPressEvent( event )       
                            
    def setupGui(self):
        self.centralWidget = MainWidget( self )
        layout = QVBoxLayout()
        self.setCentralWidget ( self.centralWidget )
        self.centralWidget.setLayout( layout )

if __name__ == '__main__':                                           
    app = QApplication(sys.argv)
    form = MainForm()
    rect = QApplication.desktop().availableGeometry()
    form.resize(int(rect.width()), int(rect.height()))
    form.show()
    app.exec_()