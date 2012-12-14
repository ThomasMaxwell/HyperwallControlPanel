'''
Created on Mar 14, 2012

@author: tpmaxwel
'''

import os, sys
hwUserRoot = '/hw/home'
hwSystemPlaylist = '/var/tmp/hw/playlist.txt'

def dump_playlist( username, playlistFilePath ):
    try:
        playlistFile = open( playlistFilePath )
    except Exception, err:
        print>>sys.stderr, " Error opening PlayList File %s: %s" % ( playlistFilePath, str(err) ) 
        return      
    try:
        name = '-'.join( [ username, os.path.splitext( os.path.basename( playlistFilePath ) )[0] ] )
        print '@' + name
        for line in playlistFile:
            line = line.strip()
            if line and (line[0] <> '#'):
                args = line.split()
                showPath = args[1]
                showId = os.path.splitext( os.path.basename(showPath) )[0]
                print '$' + showId 
    except Exception, err:
        print>>sys.stderr, " Error reading PlayList File %s: %s" % ( playlistFilePath, str(err) )     
    finally:
        playlistFile.close()   

        
if __name__ == '__main__':
    dump_playlist( 'system', hwSystemPlaylist )
    users = os.listdir( hwUserRoot )
    for username in users:
        try:
            userDir = os.path.join( hwUserRoot, username )
            userFiles = os.listdir( userDir )
            for userFile in userFiles:
                userFile = userFile.lower()
                if userFile.endswith('.txt') and ( userFile.find('playlist') >= 0 ):
                    playlistFilePath = os.path.join( userDir, userFile )
                    dump_playlist( username, playlistFilePath )
        except Exception, err: 
            print>>sys.stderr, " Error reading user PlayList dir %s: %s" % ( userDir, str(err) )  
            pass
