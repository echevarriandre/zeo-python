import argparse
import os.path
import configparser

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
    configFolderPath = os.path.join(os.getenv('APPDATA'), CONFIG_FOLDER_NAME)
    configFilePath = os.path.join(os.getenv('APPDATA'), CONFIG_FOLDER_NAME, CONFIG_FILE_NAME)
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

        os.mkdir(configFolderPath)
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
    atLeastOneFileFound = False
    for e in listOfFiles:
        fullpath = os.path.join(download, e)
        if (os.path.isfile(fullpath)) and isAnimeVideo(e):
            atLeastOneFileFound = True
            name = getAnimeName(e)
            createDir(save, name)
            print('Found anime:', e)
            os.replace(fullpath, os.path.join(save, name, e))
        # else if folder starts with [HorribleSubs] it means it is a full season for example
    
    if not atLeastOneFileFound:
        print('No anime found')

def setupArguments():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-d', '--download', help='Required for the first run. Folder location for completed torrents')
    parser.add_argument('-s', '--save', help='Required for the first run. Folder location to save the files')
    return parser.parse_args()

# Verify if the file found is from HorribleSubs and if it 
def isAnimeVideo(fileName):
    if HORRIBLE_SUBS == fileName[:len(HORRIBLE_SUBS)]:
        return True
    else: 
        return False

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