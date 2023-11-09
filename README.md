# KITE ECUBE ELL Data Collection Tool

### About

This is the KITE ECUBE English Language Lab (ELL) data collection tool. Read more about KITE [here](https://kite.kerala.gov.in) and the ECUBE ELL [here](https://ecube.kite.kerala.gov.in). If you are unfamiliar with the ELL software technology and its packaging, read [this wiki page](https://github.com/IT-for-Change/ecube-data-collection/wiki) first.

## Who is this tool intended for

This tool is intended for use by organizations that run the KITE ECUBE ELL software and interested in analyzing student engagement and performance data. 

Some technical proficiency is required to 
* ensure the necessary prerequisites for executing the tool are met, and
* actually execute the tool. The person running the tool should be able to follow the contents of this README and act accordingly.

## KITE OS vs. Docker vs. Ubuntu deployments of the ELL

The ELL can be deployed on a computer in different ways - computers can run the ELL on KITE OS, or as a docker container on any OS, or on plain Ubuntu OS. See [here](https://kite.kerala.gov.in/llabdownload.html) for details of supported OS versions. The data collection tool should work on all these flavours, but since the largest deployment of the tool so far is on [KITE OS](https://kite.kerala.gov.in/KITE/index.php/welcome/downloads), the tool is designed to assume a KITE OS deployment by default, and the tool's default configuration values correspond to KITE OS. 

If you are using a docker-based deployment, instructions on prerequisite steps and changes to the tool's configuration are documented in [this](https://github.com/IT-for-Change/ecube-data-collection/blob/main/README.md#prerequisites-docker) section.

The tool *should* work correctly on plain Ubuntu OS deployments of the ELL if it is configured correctly. The tool has not been tested on a plain Ubuntu deployment.

## What data is collected by the tool?

The data collected by the tool depends on the scope you define for it in the configuration. The tool supports two scopes - `audio` and `all`. The default setting for the tool is `audio`, specified as `ecube.collectscope = audio` in the configuration.

When the scope is set as `all`, the tool collects
* The entire ELL database, in the form of a mysqldump sql file
* Audio files (webm/ogg) from audio activity submissions

When the scope is set as `audio`, the tool collects
* Audio files (webm/ogg) from audio activity submissions
* Metadata for each audio activity submission
    * the userid of the student who submitted the audio,
    * the unique id for the audio activity in the ELL,
    * the id of the course to which the activity belongs,
    * the audio file name

All of the collected data is packaged into a single tar.gz file.

## Prerequisites (KITE OS)

### 1. Software / Hardware checks

If you are running the ELL on KITE OS, all software prerequisites should already be met. But please make the following checks to confirm this.

1. The presence of Python 3.8 (or higher version) on the system. Do this by opening a terminal window and executing the command:

```
python3
```

You should see output similar to:

```
Python 3.8.10 (default, Sep 28 2021, 16:10:42) 
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

2. Confirm the ELL is installed under /opt/lampp. Run the command on a new terminal window.

```
ls /opt/lampp
```

You should see output similar to:

```
apache2  cgi-bin       e_cube          error   icons    info   lib64     logs                   manual      mysql  phpmyadmin      README.md     sbin   THIRDPARTY     var
bin      ctlscript.sh  ecube-files     etc     img      lampp  libexec   man                    modules     pear   proftpd         README-wsrep  share  uninstall      xampp
build    docs          e-cube_version  htdocs  include  lib    licenses  manager-linux-x64.run  moodledata  php    properties.ini  RELEASENOTES  temp   uninstall.dat
```

3. Ensure there is sufficient hard-disk space on the computer. The actual space required depends on the usage of the ELL on that computer. To be on the safer side, ensure there is at least 500 MB of space on the computer.

### 2. Configuration

1. The ELL uses a MySQL database. The tool connects to this database to download data. The configuration parameters to connect to the database are specified in the **collect.conf** file. The values reflect the ELL installation defaults on KITE OS. **No action is required if you are running the tool on the default KITE OS setup of the ELL**.
2. The tool assumes the ELL has been installed under the **/opt/lampp/** directory. If you are running ELL on KITE OS, this is the default installation location. **No action is required if you are running the tool on the default KITE OS setup of the ELL**.


### 3. Mandatory information required by the tool

#### School code
When you run the tool, it will prompt you to enter a **school code**. This code uniquely identifies your school and associates the collected data with the school. This information is mandatory for the tool to execute. Contact your IT administrator to obtain this information before executing the tool.

## Prerequisites (DOCKER)

### 1. Software / Hardware checks

If you are running the ELL as a docker container, the computer in which the container is running should meet the following prerequisites.

1. Python 3.8 (or higher version). Check this by opening a terminal window and executing the command:

```
python3
```

You should see output similar to:

```
Python 3.8.10 (default, Sep 28 2021, 16:10:42) 
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

2. MySQL client tools with the `mysqldump` tool should be installed. This should be a version compatible with Maria DB 10.

3. Note dowm the location of the `mysqldump` executable

4. Ensure there is sufficient hard-disk space on the computer. The actual space required depends on the usage of the ELL on that computer. To be on the safer side, ensure there is at least 500 MB of space on the computer.

### 2. Configuration

The ELL docker image contains a MySQL database installation. The tool connects to this database to download data. The configuration parameters to connect to the database are specified in the **collect.conf** file. Since the default values reflect the ELL installation on KITE OS, you need to change the following values in **collect.conf** to successfully execute the tool.

1. change the `ecube.setuptype` from `kiteos` to `docker`. Like this:

```
[ECUBE]
ecube.setuptype = docker
```

2. Provide the full path to the mysqldump executable under the [DOCKER] section.

For example,
```
mysqldump.bin = /usr/bin/mysqldump
```
3. Update the following database values to match the values in your docker image's compose file. 

For example,
```
mysql.db = moodle
mysql.user = root
mysql.password = rootpassword
mysql.host = localhost
mysql.port = 42333
moodle.data = /home/me/ecube_docker/ecube_moodle/moodledata
```

### 3. Mandatory information required by the tool

#### School code
When you run the tool, it will prompt you to enter a **school code**. This code uniquely identifies your school and associates the collected data with the school. This information is mandatory for the tool to execute. Contact your IT administrator to obtain this information before executing the tool.


## Are you ready to execute the tool?

1. Confirm all prerequisites are met
2. Confirm you have the school code on hand
3. Confirm you have the credentials to login to the computer on which the ELL is installed and have the permissions to start the ELL software there. 
4. Confirm you know where to upload the final data package (tar.gz) file that will be generated by the tool. If the ELL computer does not have access to the internet, you may need an USB stick on hand to copy the data package to another computer and upload it.

## Steps to install and execute the tool

> Assuming all prerequisite checks have passed and you have the school code on hand, you should not need more than 30 minutes in total to install and execute the tool. The tool itself will need less than a minute to execute.

1. Login to the computer on which the ECUBE ELL software is installed. The login user should have rights to start the software
2. Start the ELL as per the normal procedure documented by the ELL software and login as any user. This is to confirm the ELL database has started and is running. Proceed to the next step only if you are able to login successfully into the ELL
3. Download the latest release version of the tool to the computer on which the ELL is installed. The latest release of the tool is available [here](https://github.com/IT-for-Change/ecube-data-collection/releases) as a tar.gz file.
5. Move the downloaded file to your home directory. 
6. Extract the tar.gz file to any folder under the home directory
7. Open a terminal window and navigate to this directory. Once you are inside this directory, run the `ls` command, you should see the following output:

```
$ls
collect.conf  collect.py  LICENSE  README.md  run-collect.sh
```

8. Grant execute permission for the **run-collect.sh** script with the following command:

```
$chmod 777 run-collect.sh
```

9. Execute the tool by running the script

```
$./run-collect.sh
```

10. If the tool completes execution successfully, you should see the following as the last two lines of the execution log on the terminal window (the date time and the filename will vary, of course):

```
27/03/2023 08:08:07 AM - INFO: Data collection complete.
27/03/2023 08:08:07 AM - INFO: Upload the file 'dfdc1e57-f828-4789-8506-974e06ec6664.tar.gz' as instructed
```
## Uploading the data file

Before you upload the collected data,

1. Confirm the tool has not encountered any errors by checking for any messages that is marked "ERROR: " in the console. If you closed the terminal window already, repeat the execution (nothing will go wrong when you re-execute!)
2. If the tool has executed successfully, one of the last log entries on the terminal window will be ```INFO: Data collection completed successfully.```
3. Then, Open the file explorer and navigate to the tool location under your home directory. The data package file (.tar.gz) will be available under the **upload** directory. Upload only the tar.gz file inside this directory. See the directory structure below. Upload **ONLY** the tar.gz file as indicated, nothing else.
4. Upload the file to a location as instructed by your designated IT team contact.

```
├── collect.conf
├── collect.py
├── LICENSE
├── log
│   ├── b1507daa-05f1-4944-b432-029f7b14b435.log
│   └── b1507daa-05f1-4944-b432-029f7b14b435.txt
├── README.md
├── run-collect.sh
└── upload
    └── b1507daa-05f1-4944-b432-029f7b14b435.tar.gz    ----------> **UPLOAD ONLY THIS ONE TAR.GZ FILE**
```

## Troubleshooting

If the tool does not complete successfully, it will print an error message and an code in the terminal log. Refer the error code table below and take action accordingly. Additional informational and debug messages are written to the log file in the tool's **log** directory.

If you are unable to resolve the problem yourself, report the issue to your designated IT team contact with a screenshot of the error on the terminal and a copy of the log file.

| Error code      | Possible cause(s) | Suggested action |
| ----------- | ----------- | ----------- |
| 1001      | The tool was not able to execute the database dump | Check if the ELL software is running by logging in as a user. If you are able to login to the ELL, check if the database connection parameter in the tool configuration **collect.conf** matches the ELL database setup.|
| 1002      | The tool was not able to extract specific tables from the database| Same as above |
| 1003      | The tool was not able to process the extracted tables. This is usually because the extraction step did not happen correctly| Same as above |
| 1004      | The tool was not able to package the collected data as a tar.gz file| Check the available disk space on the computer or for any other errors. |
| 1005      | The tool was not able to successfully complete the cleanup of temporary files generated by it| This can be ignored. |
| 1006      | The tool was not able to successfully generate a completion report file| Check the available disk space on the computer or for any other errors.|
| 1007      | The tool was not able to process the extracted audio file metadata elements or copy over an individual audio file from the ELL. | Check the available disk space on the computer or for any other errors.|
| 9999      | Some unforeseen error occurred during execution| Report it to your designated IT team contact with a screenshot of the terminal window and a copy of the log file from the **log** directory|

## Uninstalling the tool

Note: **DO NOT** uninstall the tool until you have successfully uploaded the data package as instructed. 

To uninstall, simply delete the directory you extracted the tool to. This will remove the tool, its log files and the collected data package.
