import argparse
import os.path
import platform
import configparser
from pathlib import Path

# ------------ Constants ------------ #
# Settings
CONFIG_FOLDER_NAME = 'Zeo'
CONFIG_FILE_NAME = 'zeo.ini' # change to appdata later on

# Config constants
CONFIG_FOLDER = 'Folder Paths'
CONFIG_DOWNLOAD = 'download'
CONFIG_SAVE = 'save'

# Substrings to look for
HORRIBLE_SUBS = '[HorribleSubs]'
NAME_EPISODE_DELIMITER = '-'
# ----------------------------------- #

def main(args):
    config = configparser.ConfigParser()

    operativeSystem = platform.system()
    if operativeSystem == 'Linux':
        home = str(Path.home())
        configFolderPath = os.path.join(home, '.config', CONFIG_FOLDER_NAME)
        configFilePath = os.path.join(configFolderPath, CONFIG_FILE_NAME)
    elif operativeSystem == 'Windows':
        configFolderPath = os.path.join(os.getenv('APPDATA'), CONFIG_FOLDER_NAME)
        configFilePath = os.path.join(configFolderPath, CONFIG_FILE_NAME)
    else:
        print('Operative system not supported')
        return 1

    if os.path.isfile(configFilePath):
        config.read(configFilePath)
        if args.download != None:
            config[CONFIG_FOLDER][CONFIG_DOWNLOAD] = str(args.download)
        if args.save != None:
            config[CONFIG_FOLDER][CONFIG_SAVE] = str(args.save)

        with open(configFilePath, 'w') as file:
                config.write(file)
    else:
        if args.download == None or args.save == None:
            print('Use -h or --help for the correct usage when running for the first time')
            return 1

        os.makedirs(configFolderPath)
        print('Creating config folder in', configFolderPath)
        file = open(configFilePath, 'w')

        config[CONFIG_FOLDER] = {}
        config[CONFIG_FOLDER][CONFIG_DOWNLOAD] = str(args.download)
        config[CONFIG_FOLDER][CONFIG_SAVE] = str(args.save)

        config.write(file)
        file.close()
        print('Creating config file in', configFilePath)

    download = config[CONFIG_FOLDER][CONFIG_DOWNLOAD]
    save = config[CONFIG_FOLDER][CONFIG_SAVE]

    listOfFiles = os.listdir(download)
    filesFound = searchForFiles(listOfFiles, save, download)

    if not filesFound: print('No anime found')

def setupArguments():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-d', '--download', help='Required for the first run. Folder location for completed torrents')
    parser.add_argument('-s', '--save', help='Required for the first run. Folder location to save the files')
    return parser.parse_args()

def searchForFiles(listOfFiles, save, download):
    atLeastOneFileFound = False
    for e in listOfFiles:
        fullpath = os.path.join(download, e)
        if os.path.isfile(fullpath) and isFromHorribleSubs(e):
            atLeastOneFileFound = True
            name = getAnimeName(e)
            createDir(save, name)
            try:
                os.replace(fullpath, os.path.join(save, name, e))
                print('Found anime:', e)
            except PermissionError as error:
                print('The following anime: ' + e + ' is currently being used by another process. Try again later.')
        elif isFromHorribleSubs(e):
            newPath = os.path.join(download, e)
            listOfFiles = os.listdir(newPath)
            atLeastOneFileFound = searchForFiles(listOfFiles, save, newPath)
            if len(os.listdir(newPath)) == 0:
                os.rmdir(newPath)
    
    return atLeastOneFileFound

# Verify if the file found is from HorribleSubs
def isFromHorribleSubs(fileName):
    return True if HORRIBLE_SUBS == fileName[:len(HORRIBLE_SUBS)] else False

# Get only the name of the anime and remove all extra stuff
def getAnimeName(fileName):
    aux = None
    # Remove HorribleSubs tag, quality tag and file extension
    # Change to constants for [1080] and search for the extension separator .
    aux = fileName[len('[HorribleSubs]') + 1:-12]
    index = aux.rfind(NAME_EPISODE_DELIMITER)
    return aux[:index-1]

# Create directory for a new anime
def createDir(save, name):
    fullPath = os.path.join(save, name)
    if not os.path.exists(fullPath):
        os.mkdir(fullPath)
        print('Created a new directory:', fullPath)

if __name__ == "__main__":
    args = setupArguments()
    main(args)