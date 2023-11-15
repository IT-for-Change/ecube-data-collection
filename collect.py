import sys
import logging
import uuid
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import xml.etree.ElementTree as ET
import os.path
from pathlib import Path
import sqlite3
import shutil
import configparser
from time import time
import csv
import traceback

APP_VERSION = '2.0.2'
ECUBE_COLLECT_SCOPE_FULL = 'all'
ECUBE_COLLECT_SCOPE_AUDIO = 'audio'
ECUBE_COLLECT_DB = 'ell-collect.db'

#KITE OS based ECUBE is the default; the value is also set in the conf file
#It can take values 'kiteos' or 'docker'
class CollectConfiguration:
        ecubeSetupType = 'kiteos'
        ecubeCollectScope = ECUBE_COLLECT_SCOPE_AUDIO
        ecubeTables = ''
        ecubeLocalDB = ''
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

    ecubeCollectScope = config['ECUBE']['ecube.collectscope']
    if (ecubeCollectScope == None or ecubeCollectScope == ""):
        ecubeCollectScope = ECUBE_COLLECT_SCOPE_AUDIO

    ecubeLocalDB = config['ECUBE']['ecube.localdb']
    if (ecubeLocalDB == None or ecubeLocalDB == ""):
        ecubeLocalDB = ECUBE_COLLECT_DB

    collectConfig = CollectConfiguration()
    collectConfig.ecubeSetupType = ecubeSetupType
    collectConfig.ecubeCollectScope = ecubeCollectScope
    collectConfig.ecubeLocalDB = collectConfig.tmpDir + ECUBE_COLLECT_DB
    collectConfig.ecubeTables = config['ECUBE']['ecube.tables']
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

    if (collectConfig.ecubeCollectScope == ECUBE_COLLECT_SCOPE_FULL):
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
        collectConfig.ecubeCollectScope + ' | ' + \
        collectConfig.ecubeLocalDB + ' | ' + \
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
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, encoding='utf-8',shell=True)
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

def dumpELLDB(collectConfig):
    logging.info("Dumping data from the ELL database for FULL collect scope")
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

    logging.info("Dumped data from the database successfully")
    return execStatus
    

def exportTablesToXML(collectConfig):
    logging.info("Collecting data from XML tables")
    logging.debug('Database tables {}'.format(collectConfig.ecubeTables))
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
        collectConfig.ecubeTables + \
        ' ' + \
        '>' + ' ' + \
        collectConfig.moodleMediaTableDataFile
    
    logging.debug('Creating xml table dump...')
    execStatus = runProcess(cmd)
    if (execStatus == False):
        raise DataCollectionError("1002")
    logging.info('Completed XML table dump successfully')
    return execStatus

def setupLocalDB(collectConfig):

    db = sqlite3.connect(collectConfig.ecubeLocalDB)

    tables = collectConfig.ecubeTables.split(' ')

    doc = ET.parse(collectConfig.moodleMediaTableDataFile).getroot()  # Parse XML

    for table in tables:
        table_structure = doc.find("./database/table_structure/[@name='" + table + "']")
        table_fields = table_structure.findall('field')

        create_table_sql = 'create table if not exists ' + table     + ' ('

        for table_field in table_fields:
            table_column = table_field.attrib['Field']
            create_table_sql += table_column + ' TEXT,'
    
        create_table_sql = create_table_sql.rstrip(',')
        create_table_sql += ' );'
        logging.debug('Creating local table {} with SQL {}'.format(table, create_table_sql))
        db.execute(create_table_sql)
    return

def populateLocalDB(collectConfig):

    db = sqlite3.connect(collectConfig.ecubeLocalDB)

    tables = collectConfig.ecubeTables.split(' ')

    doc = ET.parse(collectConfig.moodleMediaTableDataFile).getroot()  # Parse XML

    for table in tables:
        
        table_structure = doc.find("./database/table_structure/[@name='" + table + "']")
        table_fields = table_structure.findall('field')
        
        table_insert_sql = 'insert into ' + table + '('
        for table_field in table_fields:
            table_column = table_field.attrib['Field']
            table_insert_sql += table_column + ','

        table_insert_sql = table_insert_sql.rstrip(',')
        table_insert_sql += ' ) values ('

        for table_field in table_fields:
            table_insert_sql += '?,'

        table_insert_sql = table_insert_sql.rstrip(',')
        table_insert_sql += ')'

        table_data = doc.find("./database/table_data/[@name='" + table + "']")

        data_rows = table_data.findall('row')
        rows_to_insert = []

        for data_row in data_rows:
            data_fields = list(data_row)
            row_to_insert = []
            for data_field in data_fields:
                if (data_field.text == None):
                    data_field.text = ''
                row_to_insert.append(data_field.text)
            rows_to_insert.append(row_to_insert)

        logging.debug("Populating table {} with data using SQL {}".format(table,table_insert_sql))
        db.executemany(table_insert_sql,rows_to_insert)
        db.commit()

    db.close()

    return
    
def extractMediaMetadataFromXML(collectConfig):
    logging.info("Extracting media metadata")
    setupLocalDB(collectConfig)
    populateLocalDB(collectConfig)
    logging.info("Media metadata extracted successfully")
    return

def collectMedia(collectConfig):
    
    logging.info("Starting media collection")
    logging.debug("Reading local db " + collectConfig.ecubeLocalDB)
    
    db = None
    csvfile = None
    try:
        logging.debug("Extracting media metadata from local DB")
        sql =  '''select mdl_user.id, mdl_user.username , mdl_assign.course as course, mdl_assign.id as assignment_id, mdl_assign_submission.attemptnumber, mdl_assign_submission.timecreated, mdl_files.contenthash, mdl_files.pathnamehash 
                from mdl_assign_submission
                inner join mdl_assign on mdl_assign.id = mdl_assign_submission.`assignment`
                inner join mdl_assignsubmission_onlinetext on mdl_assignsubmission_onlinetext.`assignment` = mdl_assign_submission.`assignment`
                inner join mdl_user on mdl_user.id = mdl_assign_submission.userid
                inner join mdl_files on mdl_files.itemid = mdl_assignsubmission_onlinetext.submission 
                where mdl_assign_submission.status ='submitted' and (mdl_files.mimetype like 'audio%' or mdl_files.mimetype like 'video%');
            '''

        db = sqlite3.connect(collectConfig.ecubeLocalDB)
        cursor = db.execute(sql)
        logging.debug("Local db read complete")
        logging.info("Finished reading media records from database. Saving metadata CSV and copying audio files")

        logging.debug("Creating csv file")
        csvfilename = collectConfig.dataDir + collectConfig.id + '.csv'
        csvfile = open(csvfilename, 'w',newline='')
        logging.debug("Opened csv file {}".format(csvfilename))
        csvfilewriter = csv.writer(csvfile,delimiter=',')
        csvlines = []
        line_count = 0
        logging.debug("Looping through local DB media records and generating csv lines")
        
        for row in cursor:
            line_count += 1
            userid = row[0]
            username = row[1]
            course = row[2]
            assignmentId = row[3]
            attemptNumber = row[4]
            timecreated = row[5]
            mediaFileContenthash = row[6]
            mediaFilePathhash = row[7]
            dir1 = mediaFileContenthash[:2]
            dir2 = mediaFileContenthash[2:4]
            mediaFile = mediaFileContenthash
            mediaFileFullPath = collectConfig.moodledata + "/filedir" + "/" + str(dir1) + "/" + str(dir2) + "/" + mediaFileContenthash
            csvline = []
            csvline.append(userid)
            csvline.append(username)
            csvline.append(course)
            csvline.append(assignmentId)
            csvline.append(attemptNumber)
            csvline.append(timecreated)
            csvline.append(mediaFile)
            csvlines.append(csvline)
            logging.debug("copying audio file {0}".format(mediaFileFullPath))
            shutil.copy2(mediaFileFullPath,collectConfig.audiodataDir)
            logging.debug("Copied")

        logging.debug("Writing {} records to CSV".format(line_count))
        csvfilewriter.writerows(csvlines)
        logging.info("Saved media metadata CSV and copied audio files successfully")
    except Exception as ex:
        logging.debug("Reading media metadata from local db failed")
        logging.debug(ex)
        raise DataCollectionError("1003")
    else:
        logging.debug("Finished reading media metadata from local db successfully")
    finally:
        db.close()
        csvfile.close()

    #TODO: Mimetype check????
    
    #logging.info("Extracting audio data")
    #logging.debug("Found {} students who have submitted audio activities".format(len(users)))
    #logging.debug("Found and collected {} media files".format(audioFileCounter))
    #except Exception as err:
     #   logging.debug("Extracting audio submission data failed")
      #  logging.debug(err)
       # raise DataCollectionError("1007")

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

def logError(e,err=None):
    if (err != None):
        logging.error(err)
    logging.error("Error in data collection. Error code " + e.code)
    logging.error("Report the error code to the technical team along with the log files in the 'log' directory")
    logging.debug(''.join(traceback.format_exc()))

if __name__ == "__main__":
    
    collectConfig = None
    completedWithErrors = False

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
            if (collectConfig.ecubeCollectScope == ECUBE_COLLECT_SCOPE_FULL):
                dumpELLDB(collectConfig)
            exportTablesToXML(collectConfig)
            extractMediaMetadataFromXML(collectConfig)
            collectMedia(collectConfig)
            saveReport(startTime, collectConfig.id, schoolCode, collectConfig.logDir)
            packageData(collectConfig)
        else:
            logging.info("Exiting without collecting data")
            exit()
    except DataCollectionError as e:
        logError(e)
        completedWithErrors = True
    except Exception as err:
        e = DataCollectionError('9999')
        print(err) # in case logging is not yet initialized
        logError(e,err)
        completedWithErrors = True
    finally:
        if (completedWithErrors == True):
            logging.info("Data collection completed with errors.")
        else:
            logging.info("Data collection completed successfully.")
            logging.info("Upload the file '" + collectConfig.tarfile + "' as instructed")
#DOC #TODO
#(ensure default kiteos)
#run LL
#open terminal, go to this directory
#chmod 777 run-collect.sh
#goto upload dir. upload only the tar gz file (not the directory or any other file or directory)
