from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, sys, threading, subprocess
from WirelessControllerInterface import *    
current_dir = os.path.dirname(__file__)
hid_api_dir = os.path.join( os.path.dirname(current_dir), 'HID_API' )
hid_bridge_app = os.path.join( hid_api_dir, 'hidBridge' )
ControlEventType =  QEvent.User + 1
   
class QtControllerEvent( QEvent ):
 
    def __init__( self, controlEventData ):
         QEvent.__init__ ( self, ControlEventType )
         try:
             self.controlEventType = controlEventData[1]
             if ( self.controlEventType == 'P' ) or  ( self.controlEventType == 'R' ):
                 self.buttonId = ( int(controlEventData[2]), int(controlEventData[3]) )
#                 print " Button event : %s "  % str( self.buttonId  )
             if ( self.controlEventType.lower() == 'j' ):
                 sx = '0x'+controlEventData[2:4]
                 sy = '0x'+controlEventData[4:6]
                 self.jx = ( int( sx, 0 ) - 128 ) / 128.0;
                 self.jy = ( 128 - int( sy, 0 ) ) / 128.0;
#                 print " Joystick event : %s %s ( %d %d ) (%.2f %.2f ) "  % ( sx, sy, ix, iy, self.jx, self.jy )
         except Exception, err:
             print>>sys.stderr, " ControllerEvent Error: ", str(err)
     
class QtControllerInterface( threading.Thread ):
    
    def __init__( self, target ):
        threading.Thread.__init__ ( self )
        self.daemon = True
        self.target = target
        
    def stop(self):
        self.isActive = False
    
    def run(self):
        wc = WirelessController()
        wc.start()
        self.isActive = True
        while self.isActive:
            status, event_spec = wc.getEventData( ) 
            if event_spec[0] == 'E':
               print>>sys.stderr, "Control device generated error: ",  event_spec
            else:
#                print "Posting event: %s, status = %d" % ( event_spec, status )
                QApplication.postEvent( self.target, QtControllerEvent( event_spec ) )  
            if status < 0: break   
        wc.stop()

class EventTestForm( QMainWindow ):
 
    def __init__(self, parent=None ):
        super(QMainWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_AcceptTouchEvents)
                
    def event ( self, event ):
        if event.type() == ControlEventType:
            if ( event.controlEventType == 'P' ):
#                print " **Form--> Button Press, ID = ", str( event.buttonId )  
                pass             
            if ( event.controlEventType.lower() == 'j' ):
#                print " **Form--> JS Toggle, Pos = ( %.2f %.2f )" % ( event.jx, event.jy )  
                pass
                
        return super(QMainWindow, self).event( event )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = EventTestForm()
    form.resize(800,500)
    form.show()
    controllerInterface = QtControllerInterface( form )
    controllerInterface.start()
    app.exec_()
