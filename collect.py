import sys
import logging
import uuid
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import xml.etree.ElementTree as ET
import os.path
from pathlib import Path
import shutil
import configparser
from time import time

APP_VERSION = '1.0.0'

#KITE OS based ECUBE is the default; the value is also set in the conf file
#It can take values 'kiteos' or 'docker'
class CollectConfiguration:
        ecubeSetupType = 'kiteos'
        mysqldumpbin = ''
        mysqldb = ''
        mysqluser = ''
        mysqlpassword = ''
        mysqlhost = ''
        mysqlport = ''
        moodledata = ''
        logDir = 'log/'
        dataDir = 'data/'
        dbDir = dataDir + 'db/'
        tmpDir = 'tmp/'
        audiodataDir = dataDir + 'audio/'
        id = str(uuid.uuid4())
        logFilename = logDir + id + '.log'
        sqldumpFilename = dbDir + id + '.sql'
        moodleMediaTableDataFile = tmpDir + id + '-tables.xml'
        allowedMediaTypes = ('audio/ogg', 'video/webm')
        uploadDir = 'upload/'
        tarfile = id + '.tar.gz'

class Report:
    startTime = ''
    endTime = ''
    schoolCode = ''
    id = ''
 
class DataCollectionError(Exception):
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return repr(self.code)

def loadConfig(): 
    config = configparser.ConfigParser()
    config.sections()
    config.read('collect.conf')
    ecubeSetupType = config['ECUBE']['ecube.setuptype']
    if (ecubeSetupType == None or ecubeSetupType == ""):
        ecubeSetupType = 'kiteos'
    
    if ecubeSetupType == 'kiteos':
        configSection = 'KITEOS'
    elif ecubeSetupType == 'docker':
        configSection = 'DOCKER'
    else:
        configSection = 'KITEOS'

    collectConfig = CollectConfiguration()
    collectConfig.ecubeSetupType = ecubeSetupType
    collectConfig.mysqldumpbin = config[configSection]['mysqldump.bin']
    collectConfig.mysqldb = config[configSection]['mysql.db']
    collectConfig.mysqluser = config[configSection]['mysql.user']
    collectConfig.mysqlpassword = config[configSection]['mysql.password']
    collectConfig.mysqlhost = config[configSection]['mysql.host']
    collectConfig.mysqlport = config[configSection]['mysql.port']
    collectConfig.moodledata = config[configSection]['moodle.data']

    return collectConfig
    
    
def confirmContinue(collectConfig):
    if (os.path.exists(collectConfig.dataDir)):
        logging.debug("I may have run on this computer previously. Confirming re-run with user before clearing old data..")
        confirm = input("Re-running this tool will clear any old data previously collected. Continue? (enter 'y' to continue): ")
        if (confirm.lower() == 'y'):
            logging.info('OK. Continuing...')
            return True
        else:
            logging.info('OK. Exiting...')
            return False
    return True

def clearAndCreateDirs(collectConfig):
    logging.info("Clearing data files and directories from previous run if any")
    tmpDir = collectConfig.tmpDir
    dataDir = collectConfig.dataDir
    dbDir = collectConfig.dbDir
    audiodataDir = collectConfig.audiodataDir
    logDir = collectConfig.logDir
    uploadDir = collectConfig.uploadDir

    if (os.path.exists(tmpDir)): 
        shutil.rmtree(tmpDir)
    
    Path(tmpDir).mkdir()

    if (os.path.exists(dataDir)): 
        shutil.rmtree(dataDir)

    Path(dbDir).mkdir(parents=True)
    Path(audiodataDir).mkdir(parents=True)

    if (os.path.exists(uploadDir)): 
        shutil.rmtree(uploadDir)

    Path(uploadDir).mkdir()
    
    if (os.path.exists(logDir)):
        #shutil.rmtree(logDir)
        logging.debug("[Skipping log directory]")
    else:
        Path(logDir).mkdir()

    logging.info("Data files, directories cleaned and reset successfully")

def initLogging(collectConfig):
    
    logDir = collectConfig.logDir
    if (os.path.exists(logDir) == False):
        Path(logDir).mkdir()
    
    logging.basicConfig( filename = collectConfig.logFilename,filemode = 'w',level = logging.DEBUG,format = '%(asctime)s - %(levelname)s: %(message)s',\
                     datefmt = '%d/%m/%Y %I:%M:%S %p' )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO) #log info and error to console. debug goes only to file
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s',\
                     datefmt = '%d/%m/%Y %I:%M:%S %p' ))
    logging.getLogger().addHandler(stream_handler)

    logging.info('Logging initialized. Starting data collection with id {}'.format(collectConfig.id))
    logging.debug('Configuration ' + collectConfig.ecubeSetupType + ' | ' + \
        collectConfig.mysqldumpbin + ' | ' + \
        collectConfig.mysqldb + ' | ' + \
        collectConfig.mysqlhost + ' | ' + \
        collectConfig.mysqlport + ' | ' + \
        collectConfig.mysqluser + ' | ' + \
        collectConfig.mysqlpassword + ' | ' + \
        collectConfig.moodledata
        )
#
# No-op by default. Add custom validation as per your need
def isValidSchoolCode(code):
    #example
    #if code.startswith('A'):
        #return True
    #else:
        #return False
    return True

def getSchoolCode():
    schoolCode = ''
    while True:
        print('\n')
        schoolCode = input("Enter the school code: ")
        if (schoolCode.strip() != ''):
            if (isValidSchoolCode(schoolCode)):
                logging.info("School code provided: " + schoolCode + "\n")
                break
            else:
                logging.info("Invalid school code. Check your input and try again")
                logging.debug("Invalid school code: " + schoolCode)
                continue
        else:
            logging.info("School code is a mandatory input for data collection. Try again")
            continue

    return schoolCode

def runProcess(cmd):
    
    try:
        logging.debug('Executing command "' + cmd + '"')
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, text='utf-8',shell=True)
        out, err = p.communicate()
    except (OSError, CalledProcessError):
        logging.debug('Error executing command')
        logging.debug(err.replace('\n',''))
        return False
    else:
        if (err != None):
            logging.debug(err.replace('\n',''))
            if any("warning" not in l.lower() for l in err.splitlines()):#ignore the mysql insecure password warning
                return False
            else: 
                return True
        else: 
            logging.debug('Command executed successfully')
            return True

def dumpDB(collectConfig):
    logging.info("Collecting data from the database")
    cmd = ''
    cmd = \
        collectConfig.mysqldumpbin + ' ' + \
        '-h' + ' ' + \
        collectConfig.mysqlhost + ' ' + \
        '-P' + ' ' + \
        collectConfig.mysqlport + ' '
    
    if collectConfig.ecubeSetupType == 'docker':
        cmd += '--protocol tcp '

    cmd +=  \
        '-u' + ' ' + \
        collectConfig.mysqluser + ' ' + \
        '-p' + '' + \
        collectConfig.mysqlpassword + ' ' + \
        '' + \
        collectConfig.mysqldb + ' ' + \
        '>' + ' ' + \
        collectConfig.sqldumpFilename
    
    logging.debug('Creating database dump...')
    execStatus = runProcess(cmd)
    if (execStatus == False):
        raise DataCollectionError("1001")

    logging.info("Collected data from the database successfully")
    return execStatus
    

def dumpXMLTables(collectConfig):
    logging.info("Collected data from XML tables")
    cmd = ''
    cmd = \
        collectConfig.mysqldumpbin + ' ' + \
        '-h' + ' ' + \
        collectConfig.mysqlhost + ' ' + \
        '-P' + ' ' + \
        collectConfig.mysqlport + ' '
    
    if collectConfig.ecubeSetupType == 'docker':
        cmd += '--protocol tcp '

    cmd +=  \
        '-u' + ' ' + \
        collectConfig.mysqluser + ' ' + \
        '-p' + '' + \
        collectConfig.mysqlpassword + ' ' + \
        ' ' + \
        '--xml' + ' ' + \
        collectConfig.mysqldb + ' ' + \
        'mdl_files mdl_assign_submission mdl_user ' + \
        '>' + ' ' + \
        collectConfig.moodleMediaTableDataFile
    
    logging.debug('Creating xml table dump...')
    execStatus = runProcess(cmd)
    if (execStatus == False):
        raise DataCollectionError("1002")
    logging.info('Completed XML table dump successfully')
    return execStatus
    
def collectMedia(collectConfig):
    
    logging.info("Starting media collection")
    logging.debug("Reading file " + collectConfig.moodleMediaTableDataFile)
    root = None
    try:
        logging.debug("Parsing XML file")
        tree = ET.parse(collectConfig.moodleMediaTableDataFile)
        root = tree.getroot()
    except Exception as ex:
        logging.debug("XML parsing failed")
        logging.debug(ex)
        raise DataCollectionError("1003")
    else:
        logging.debug("XML parsed successfully")
    #xpath = "./database/table_data/row/field/[@name='mimetype']"
    filedir = collectConfig.moodledata + "/filedir"
    logging.info("Loaded media metadata successfully")
    # The logic below is simply equivalent to the SQL: 
    # ---
    # select * from mdl_files where mimetype in ('audio/ogg','video/webm') 
    # and userid in (select distinct userid from mdl_assign_submission where status='submitted');
    # ---
    # We cannot run an SQL due to the constraint we cannot connect to the ELL MySQL because it requires a python-mysql connector that is not part of the standard python package installed 
    # on the ELL workstation. To workaround, we are dumping the required database tables as xml files and parsing the xml 
    # to extract the information that would otherwise have been obtained by running the above SQL

    logging.info("Extracting audio data")

    try:
        users = []
        assignmentSubmissionsXpath = "./database/table_data/[@name='mdl_assign_submission']/row"
        for assignmentSubmissionRecord in root.findall(assignmentSubmissionsXpath):
            submissionStatus = assignmentSubmissionRecord.find("field/[@name='status']")
            userid = assignmentSubmissionRecord.find("field/[@name='userid']")
            if (submissionStatus.text == 'submitted'):
                users.append(userid.text)

        logging.debug("Found {} students who have submitted audio activities".format(len(users)))

        mediaRecordXpath = "./database/table_data/[@name='mdl_files']/row"
        mediaRecords = root.findall(mediaRecordXpath)
        audioFileCounter = 0
        for mediaRecord in mediaRecords:
            userid = mediaRecord.find("field/[@name='userid']").text
            filearea = mediaRecord.find("field/[@name='filearea']").text
            if (userid in users):
                mimetype = mediaRecord.find("field/[@name='mimetype']")
                if ((mimetype.text in collectConfig.allowedMediaTypes) and (filearea == 'submissions_onlinetext')) :
                    audioFileCounter = audioFileCounter+1
                    contenthash = mediaRecord.find("field/[@name='contenthash']").text
                    component = mediaRecord.find("field/[@name='component']").text
                    id = mediaRecord.find("field/[@name='id']").text
                    dir1 = contenthash[:2]
                    dir2 = contenthash[2:4]
                    mediaFile = filedir + "/" + str(dir1) + "/" + str(dir2) + "/" + contenthash
                    #print(userid + "," + mediaFile)
                    shutil.copy2(mediaFile,collectConfig.audiodataDir)
        logging.debug("Found and collected {} media files".format(audioFileCounter))
    except Exception as err:
        logging.debug("Extracting audio submission data failed")
        logging.debug(err)
        raise DataCollectionError("1007")
    
    logging.info("Extracted audio data successfully")

def packageData(collectConfig):

    logging.info('Creating tarball and compressing')
    
    cmd = 'tar czf' + ' ' + collectConfig.uploadDir + collectConfig.tarfile + ' data log'
    execStatus = runProcess(cmd)
    if (execStatus == False):
        raise DataCollectionError("1004")

    logging.info('Created compressed tarball')
    
    logging.info('Cleaning up...')
    cmd = 'rm -rf ' + collectConfig.tmpDir + ' ' + collectConfig.dataDir
    execStatus = runProcess(cmd)
    if (execStatus == False):
        raise DataCollectionError("1005")

    logging.info('Cleaned up successfully')

def saveReport(startTime, id, schoolCode, logDir):
    logging.info("Creating run report")
    try:
        config = configparser.ConfigParser()
        config['ECUBE'] = {'startTime': startTime,
                         'id': id,
                         'schoolCode': schoolCode}
        with open(logDir + id + '.txt', 'w') as configfile:
            config.write(configfile)
    except:
        raise DataCollectionError("1006")
    logging.info("Run report created successfully")

if __name__ == "__main__":
    
    try:
        print("\nLaunching version " + APP_VERSION + " of the KITE ECUBE Data Collection Tool")
        startTime = int(time() * 1000)
        print('Loading configuration..')
        collectConfig = loadConfig()
        print('Configuration loaded. Initializing logging system..')
        initLogging(collectConfig)
        schoolCode = getSchoolCode()
        if (confirmContinue(collectConfig) == True):
            clearAndCreateDirs(collectConfig)
            dumpDB(collectConfig)
            dumpXMLTables(collectConfig)
            collectMedia(collectConfig)
            saveReport(startTime, collectConfig.id, schoolCode, collectConfig.logDir)
            packageData(collectConfig)
            logging.info("Data collection complete.")
            logging.info("Upload the file '" + collectConfig.tarfile + "' as instructed")
        else:
            logging.info("Exiting without collecting data")
    except DataCollectionError as e:
        logging.error("Error in data collection. Error code " + e.code)
        logging.info("Report the error code to the technical team along with the log files in the 'log' directory")
    except Exception as err:
        logging.error(err)
        logging.error("Error in data collection. Error code 9999")
        logging.info("Report the error code to the technical team along with the log files in the 'log' directory")
    exit()

""" def isUseridMediaFileCreator(root,userid):
    userRecordXpath = "./database/table_data/[@name='mdl_user']/row"
    for userRecord in root.findall(userRecordXpath):
        id = userRecord.find("field/[@name='id']").text
        if (id == userid):
            return True
        else:
            return False """
