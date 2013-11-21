'''
Created on Jun 21, 2011

@author: tpmaxwel
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, copy, os, cdms2, traceback, copy, sip, subprocess, StringIO, time, threading
from collections import OrderedDict
hw_root_dir = os.path.dirname(__file__)
hw_config_data_path = os.path.join( hw_root_dir, 'data' )
hw_show_data_path = os.path.join( hw_config_data_path, 'shows' )
hw_exe_path = os.path.join( hw_root_dir, 'exe' )
AllShowsFile = 'vislin01.nccs.nasa.gov:/hw/data/download/allshows.txt'
LargeIconSize  = QSize(300,100)
SmallIconSize  = QSize(120,40)

def callbackWrapper( func, wrapped_arg ):
    def callMe( *args ):
        return func( wrapped_arg, *args )
    return callMe

class ParseState:
    none = 0
    path = 1
    title = 2
    description = 3
    
class ImportMissingShowsThread( threading.Thread ):

    def __init__( self, showMgr, startup_time=15.0 ):
        threading.Thread.__init__( self )
        self.isActive = True 
        self.daemon = True
        self.showMgr = showMgr
        self.startup_time = startup_time
        self.dlg = QDialog()
        self.dlg.setWindowTitle('Import Missing Shows')
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setMargin(6)
        label = QLabel(" Generating missing show snapshots.\n Could tie up hyperwall for a long time.\n Click 'stop' to terminate process. ")
        closeButton = QPushButton('Stop', self.dlg)
        layout.addWidget(label)
        layout.addWidget(closeButton)
        self.dlg.connect(closeButton, SIGNAL('clicked(bool)'), self.stop)
        self.dlg.setLayout(layout)
        self.dlg.show()
        
    def stop(self):
        self.isActive = False
        self.dlg.close()

    def run(self):
        idList = list( self.showMgr.showRecs.keys() )
        print " -- Running ImportMissingShowsThread, ids: ", str( idList )
        while self.isActive and ( len( idList ) > 0 ):
            showId = idList.pop()
            showRec = self.showMgr.getShowRecord( showId )
            print " -- Testing show ", showId
            if showRec and showRec.isActive() and not showRec.validPixmap:
                print " -- --> Missing Pixmap- importing!"
                self.showMgr.runShow( showRec )
                time.sleep( self.startup_time )
                self.showMgr.importShow()

class ShowRecord(QObject):
    def __init__( self, show_id ):
        super( ShowRecord, self ).__init__()
        self.id = str(show_id)
        self.path = None
        self.title = ""
        self.pixmap = None
        self.description = []
        self.active = True
        self.validPixmap = False
        
    def hasDocs(self):
        return ( len( self.description ) > 0 ) or ( self.title <> self.id )

    def importDocs( self, item ):
        doImport = True
        if self.hasDocs():
            msgBox = QMessageBox()
            msgBox.setText("There is a show by this name with documentation.");
            msgBox.setInformativeText("Do you want overwrite?");
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            doImport = msgBox.exec_()
        if doImport: 
            self.description = item.description
            self.title = item.title

    def getPixmap(self):
        if self.pixmap == None: self.loadPixmap()
        return self.pixmap
    
    def setActivation( self, val ):
        self.active = val
        
    def isActive(self):
        return self.active
    
    def matchesPath( self, path ):
        return ( path == self.path )

    def loadPixmap(self):
        data_file_path = os.path.join( hw_show_data_path, self.id + ".jpg" )
        if os.path.isfile( data_file_path ):
            self.validPixmap = True
        else:
            data_file_path = os.path.join( hw_show_data_path, "__accessing__.jpg" )
        self.pixmap = QPixmap (  data_file_path )
        return self.pixmap
                       
#    def getIcon(self):
#        self.getPixmap()
#        return QIcon( self.pixmap.scaled( IconSize, Qt.KeepAspectRatio, Qt.SmoothTransformation ) ) 
    
    def getTitle(self):
        return self.title if self.title else self.id
    
    def setTitle( self, title ):
        if title: self.title = str( title )

    def setId( self, new_id ):
        self.id = str( new_id )

    def getPath(self):
        return self.path if self.path else self.id
    
    def setPath( self, path ):
        self.path = str( path )
        self.active = True

    def getDescription(self):
        text = "\n".join( self.description )
        return text
    
    def setDescription( self, text ):
        self.description = str( text ).split( "\n" )
       
class HWShowManager(QObject):
    newShowPrefix = "#!@"
    pathPrefix = "#!>"
    pagesFile = 'pages.txt'
    
    def __init__( self, hwConfigFile, **args ):
        super( HWShowManager, self ).__init__()
        self.runningShow = None
        self.editingShow = None
        self.showRecs = {}
        self.pages = {}
        self.hwConfigFilePath  = os.path.join( hw_config_data_path, hwConfigFile )
        self.parseConfig()
        self.editingShow = None
        self.hwControlNode = 'vislin01.nccs.nasa.gov'
        self.processList = []
        self.importedShows = []
        
#    def removeShow( self, showId ):
#        showItem = None
#        for pageId in self.pages:
#            item = self.pages[ pageId ].removeShow( showId )
#            if pageId == "global": showItem = item
#        if showItem: del showItem

    def removeSelectedShowFromList( self, pageName ):
        scene = self.pages.get( pageName, None )
        if scene: scene.removeSelectedShows()

    def selectNextShow( self, pageName, showId, adjacencyIndex=-1 ):
        print " selectNextShow: ", str( pageName )
        if pageName == None: pageName = 'global'
        scene = self.pages.get( pageName, None )
        return scene.selectNextShow( showId, adjacencyIndex ) if showId else None

    def renameShow( self, oldShowId, newShowId ):
        item = self.showRecs[ oldShowId ]
        newItem = self.showRecs.get( newShowId, None )
        if newItem:
            newItem.importDocs( item )
        else:
            self.showRecs[ newShowId ] = item
            item.setId( newShowId )
        del self.showRecs[ oldShowId ]        
        for page in self.pages.values():
            page.renameShow( oldShowId, newShowId )
        self.save()
    
    def removeShow( self, showId ):
        item = self.showRecs[ showId ]
        if item.hasDocs():   
            item.setActivation( False )
            print "Can't find show %s: deactivating!" % showId 
        else:
            print "Can't find show %s: removing!" % showId             
            for pageId in self.pages:
                self.pages[ pageId ].removeShow( showId )
            del self.showRecs[ showId ]
            del item
            
    def importMissingShows( self ):
        importThread = ImportMissingShowsThread( self )       
        importThread.start()
           
    def runShow( self, showRec ):        
        cmd = [ "ssh", self.hwControlNode, '/usr/bin/hwshow "%s"' % ( showRec.getPath() ) ]
        print " --- Executing: ", ' '.join(cmd)
        try:
            p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
            self.processList.append( p ) 
            self.runningShow = showRec.id  
            return True              
        except Exception, err:
            print>>sys.stderr, " Exception in RunShow: %s " % str( err )
            return False
            
    def cleanShowList( self ):
        for show in self.showRecs.values():
            path = show.getPath()
            if self.showPathExists( path ):
                print "Show exists: ", show.id
            else:
                self.removeShow( show.id )
        self.saveConfig()

    def importShow(self): 
        print "Import current show" 
        showName, showPath = self.forceGetCurrentSnapshot()
        showRec = self.getShowRecord( showName ) 
        showRec.loadPixmap()  
        self.importedShows.append( showName )  
        return showRec    
        
    def forceGetCurrentSnapshot1( self ):
        try:
            from ScreenCapture.HyperwallScreenCapture import ParameterFile, HyperwallScreenCapture
            imageDir = os.path.expanduser(  '~/Pictures/ScreenCapture'  )
            imageFilePath = "/tmp/I.jpg"
            dims = ( 5, 3 )
            nodeList = [ "visrend%02d.nccs.nasa.gov" % iNode for iNode in range( 1, dims[0]*dims[1]+1 ) ]
            params = { 'NodeList' : ','.join( nodeList ), 'Shrink': 10, 'ImageDir' : imageDir, 'HyperwallDimensions' : "%d,%d" % ( dims[0], dims[1] ) }
            paramFile = ParameterFile( params=params )
            screenCapture = HyperwallScreenCapture( paramFile )
            screenCapture.captureScreens( "I" )           
            data_file_path = os.path.join( hw_show_data_path, '%s.jpg' % self.runningShow )
            cmd = [ "mv", "-f", imageFilePath, data_file_path ]
            print " --- Executing: ", ' '.join(cmd)
            p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
            p.wait() 
            return self.runningShow
        except Exception, err:
            print>>sys.stderr, " Exception in forceGetCurrentSnapshot: %s " % str( err )
            return None
                            
    def forceGetCurrentSnapshot( self ):
        try:
            snapshot_script = os.path.join( hw_exe_path, 'ForcedScreenCapture.sh' )
            imageFilePath = "/tmp/I.jpg"
            cmd = [ snapshot_script, imageFilePath  ]
            print " --- Executing: ", ' '.join(cmd)
            p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=sys.stderr ) 
            p.wait() 
            show_id, show_path = self.extractShowSpecs( p.stdout )
            data_file_path = os.path.join( hw_show_data_path, '%s.jpg' % show_id )
            cmd = [ "mv", "-f", imageFilePath, data_file_path ]
            print " --- Executing: ", ' '.join(cmd)
            p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
            p.wait() 
            return show_id, show_path
        except Exception, err:
            print>>sys.stderr, " Exception in forceGetCurrentSnapshot: %s " % str( err )
            return None, None
    
    def showPathExists( self, show_path ):
        test_path_script = os.path.join( hw_exe_path, 'TestShowPath.sh' )
        p = subprocess.Popen( [ test_path_script, show_path ], stdout=subprocess.PIPE, stderr=sys.stderr ) 
        p.wait() 
        for line in p.stdout.readlines():
            line = line.strip()
            if line and (line == show_path):
                return True
        return False
     
    def getNewSnapshot( self, required_show_id = None ):
        try:
            showname_script = os.path.join( hw_exe_path, 'GetCurrentShowName.sh' )
            cmd = [ showname_script,  ]
            print " --- Executing: ", ' '.join(cmd)
            p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=sys.stderr ) 
            p.wait() 
            show_id, show_path = self.extractShowSpecs( p.stdout )
            if ( required_show_id == None ) or ( required_show_id == show_id ):
                showRec = self.getShowRecord( show_id )
    #            if showRec and showRec.matchesPath( show_path ): 
    #                return None, None
                snapshot_script = os.path.join( hw_exe_path, 'ForcedScreenCapture.sh' )
                imageFilePath = "/tmp/I.jpg"
                cmd = [ snapshot_script, imageFilePath  ]
                print " --- Executing: ", ' '.join(cmd)
                p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=sys.stderr ) 
                p.wait() 
                data_file_path = os.path.join( hw_show_data_path, '%s.jpg' % show_id )
                cmd = [ "mv", "-f", imageFilePath, data_file_path ]
                print " --- Executing: ", ' '.join(cmd)
                p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
                p.wait() 
            return show_id, show_path
        except Exception, err:
            print>>sys.stderr, " Exception in getCurrentSnapshot: %s " % str( err )
            return None, None
        
    def extractShowSpecs( self, snapshot_stdout ):
        for line in snapshot_stdout.readlines():
            line = line.strip()
            if line.startswith('/hw/'):
                fileName = os.path.basename(line)
                return os.path.splitext(fileName)[0], line
        return None
        
#    def getSnapshot( self, imageFilePath ):
#        cmd = [ "ssh", self.hwControlNode, 'python HyperwallScreenCapture.py "%s" ' % ( imageFilePath ) ]
#        print " --- Executing: ", ' '.join(cmd)
#        try:
#            p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
#            self.processList.append( p ) 
#        except Exception, err:
#            print>>sys.stderr, " Exception in Snapshot: %s " % str( err )
#            
#        data_file_path = os.path.join( hw_show_data_path, self.id + ".jpg" )
#        cmd = [ "mv", imageFilePath, data_file_path ]
#        print " --- Executing: ", ' '.join(cmd)
#        try:
#            p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
#        except Exception, err:
#            print>>sys.stderr, " Exception in move image: %s " % str( err )
        
    def editingRecord( self, showId, isEditing ):
        if isEditing: self.editingShow = showId
        else: self.editingShow = None
        
    def save(self):
        self.savePages()  
        self.saveConfig()     
        
    def addPage(self, scene ):        
        self.pages[ scene.name ] = scene

    def getPage(self, name ):
        return self.pages.get( name, None )

    def updatePage(self, name ):
        scene = self.pages.get( name, None )
        if scene:
            for showId in self.importedShows:
                showRec = self.getShowRecord( showId ) 
                scene.updateShowItem( showRec )
        return scene

    def renamePage( self, old_name, new_name ):
        page = self.removePage( old_name )
        if page:
            page.name = new_name 
            self.addPage( page )
                    
    def removePage(self, name ):
        return  self.pages.pop( str(name), None )
    
    def getPageNames(self):
        return self.pages.keys()
    
    def savePages(self):
        hwPageFilePath  = os.path.join( hw_config_data_path, self.pagesFile )
        self.createBackups( hwPageFilePath, 3 )
        f = open( hwPageFilePath, 'w' )
        for page in self.pages.values():
            if page.name <> 'global':
                f.write( page.serialize() )
                f.write( '\n' )
                
    def createBackups( self, filePath, nVersions ):
        if nVersions > 9: nVersions = 9
        for iVersion in range( nVersions-1, -1, -1 ):
            targetFile = filePath if ( iVersion==0 ) else ".".join( [ filePath, str(iVersion) ] )
            if os.path.exists( targetFile ):
                dstFile =  ".".join( [ filePath, str(iVersion+1) ] )   
#                print " Creating Backup %s -> %s "  % ( targetFile, dstFile  )
                os.rename( targetFile, dstFile )

    def restorePages( self, gridWidget ):
        hwPageFilePath  = os.path.join( hw_config_data_path, self.pagesFile )
        f = open( hwPageFilePath, 'r' )
        while True:
            line = f.readline()
            if not line: break
            if len(line) > 1:
                scene = gridWidget.getNewPage() 
                scene.deserialize( line )          
                self.pages[ scene.name ] = scene
                scene.updatePage()

    def extractShowLists( self, showlist_stdout, gridWidget ):
        current_page = None
        page_names = []
        for line in showlist_stdout.readlines():
            line = line.strip()
            if line.startswith('@'):
                if current_page: current_page.updatePage()
                page_name = line[1:]
                current_page = gridWidget.getNewPage( page_name ) 
                page_names.append( page_name )
                self.pages[ page_name ] = current_page
            elif current_page and line.startswith('$'):
                current_page.addShow( line[1:] )
        if current_page: current_page.updatePage()  
        return page_names    

    def importShowLists( self, gridWidget ):
        try:
            showlist_script = '~/dev/exe/DumpPlayLists.sh'
            cmd = [ 'ssh', 'vislin01.nccs.nasa.gov', showlist_script  ]
            print " --- Executing: ", ' '.join(cmd)
            p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=sys.stderr ) 
            for iW in range( 10 ):
                if p.poll() <> None: break
                time.sleep( 0.2 )
            return self.extractShowLists( p.stdout, gridWidget )
        except Exception, err:
            print>>sys.stderr, " Exception in importShowLists: %s " % str( err )
            return []
                
    def parseConfig( self ):
        cfgFile = open( self.hwConfigFilePath, 'rU' )
        state = ParseState.none
        current_show_rec = None
        while True:
            cfgLine = cfgFile.readline()
            if not cfgLine: break
            baseCnfgLine = cfgLine.strip()
            if baseCnfgLine:
                if baseCnfgLine.startswith( self.newShowPrefix ):
                    state = ParseState.path
                    show_id_fields  = baseCnfgLine[3:].split(';')
                    show_id = show_id_fields[0]
                    current_show_rec = ShowRecord( show_id )
                    if len( show_id_fields ) > 1:
                        current_show_rec.setActivation( int( show_id_fields[1] ) )
                    self.showRecs[ show_id ] = current_show_rec 
                elif state == ParseState.path:
                    if baseCnfgLine.startswith( self.pathPrefix ):
                        current_show_rec.path = baseCnfgLine[3:]
                        state = ParseState.title
                    else:
                        if baseCnfgLine: current_show_rec.title = baseCnfgLine
                        state = ParseState.description
                elif state == ParseState.title:
                    if baseCnfgLine: current_show_rec.title = baseCnfgLine
                    state = ParseState.description
                elif state == ParseState.description:
                    current_show_rec.description.append( cfgLine )

    def saveConfig( self ):
        saveFile = self.hwConfigFilePath
        self.createBackups( saveFile, 3 )
        cfgFile = open( saveFile, 'w' )
        for show in self.showRecs.values():
            cfgFile.write( '\n' )
            cfgFile.write( self.newShowPrefix )
            cfgFile.write( show.id )
            cfgFile.write( ';' )
            if show.isActive():  cfgFile.write( '1' )
            else:                cfgFile.write( '0' )
            cfgFile.write( '\n' )
            if show.path <> None:
                cfgFile.write( self.pathPrefix )
                cfgFile.write( show.path )
                cfgFile.write( '\n' )
            cfgFile.write( show.getTitle() )
            cfgFile.write( '\n' )
            cfgFile.write( show.getDescription() )
        cfgFile.close()
            
    def getShowIds(self): 
        return self.showRecs.keys()  
    
    def getNShows(self): 
        return len(self.showRecs) 
    
    def clearHyperwall(self):
        cmd = [ "ssh", 'vislin01.nccs.nasa.gov', 'bash -c "source ~/.bash_profile; export DISPLAY=:0.0; /usr/bin/hwall off; /usr/bin/hwdemo off; ~/dev/exe/hwcleanup" ' ]
        p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
    
    def updateShows(self): 
        try:
            self.clearHyperwall()
            localAllShowsFile = '/tmp/AllShowsFile.txt'
            cmd = [ "scp", AllShowsFile, localAllShowsFile ]
            p = subprocess.Popen( cmd, stdout=sys.stdout, stderr=sys.stderr ) 
            p.wait()
            f = open( localAllShowsFile )
            for line in f:
                show_path = line.strip()
                showId = os.path.splitext( os.path.basename( show_path ) )[0]
                showRec = self.getShowRecord( showId, create=True, path=show_path )
                showRec.loadPixmap()
                print "Update %s (%s): %s " % ( showId, str( showRec.validPixmap ), show_path )
            f.close()
            self.saveConfig()
        except Exception, err:
            print>>sys.stderr, " Error in updateShows: %s " % str(err)
                
    def getShowRecord( self, showId, **args ):
        create = args.get( 'create', False )
        showPath = args.get( 'path', None )
        if self.editingShow and (self.editingShow <> showId):
            self.editingShow = None
            self.emit( SIGNAL('closeEditing()') )
        show_rec = self.showRecs.get( showId, None ) 
        if show_rec == None and create:
            show_rec = ShowRecord( showId )
            self.showRecs[ showId ] = show_rec
        if showPath and show_rec: 
            show_rec.setPath( showPath ) 
        return show_rec
   
showManager = HWShowManager( "HyperwallShowList.txt" )                                              

class ShowManagerUpdater( threading.Thread ):
    
    def __init__( self, showManager ):
        threading.Thread.__init__( self )
        self.isActive = True
        self.showManager = showManager
        self.daemon = True
              
    def shutdown(self):
        self.isActive = False

    def run(self):                      
        try:
            showIds = self.showManager.getShowIds()
            for showName in showIds:
                showRec = self.showManager.getShowRecord( showName )
                if not showRec.validPixmap:
                    if self.showManager.runShow( showRec ): 
                        print " **** Importing ", showName
                        time.sleep(20.0)       
                        self.showManager.importShow()                          
        except (KeyboardInterrupt, SystemExit):
            return
        
#    def run(self):                      
#        try:
#            self.showManager.cleanShowList()
#            while self.isActive:
#                showName, showPath = self.showManager.getNewSnapshot()
#                if showName:
#                    print "  *** Importing Show: ", showName, showPath
#                    showRec = self.showManager.getShowRecord( showName, path=showPath, create=True )        
#                    if showRec: self.showManager.saveConfig()
#                else: print "---"
#                for i in range(3):
#                    time.sleep(10.0) 
#                    print "."       
#        except (KeyboardInterrupt, SystemExit):
#            return
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    showManager.updateShows()
    smu = ShowManagerUpdater( showManager )
    smu.start()
    app.exec_()
           




