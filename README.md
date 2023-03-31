# KITE ECUBE ELL Data Collection Tool

### About

This is the KITE ECUBE English Language Lab (ELL) data collection tool. Read more about KITE [here](https://kite.kerala.gov.in) and the ECUBE ELL [here](https://ecube.kite.kerala.gov.in). If you are unfamiliar with the ELL software technology and its packaging, read [this wiki page](https://github.com/IT-for-Change/ecube-data-collection/wiki) first.

## Who is this tool intended for

This tool is intended for use by organizations that run the KITE ECUBE ELL software and interested in analyzing student engagement and performance data. Some technical proficiency is required to use the tool to 1) ensure the necessary prerequisites are met, and 2) actually execute the tool. The person running the tool should be able to understand the rest of the content in this README and able to execute the tasks mentioned.

## KITE OS vs. Docker vs. Ubuntu deployments of the ELL

The ELL can be deployed on a computer in different ways - computers can run the ELL on KITE OS, or as a docker container on any OS, or on plain Ubuntu OS. See [here](https://kite.kerala.gov.in/llabdownload.html) for details of supported OS versions. The data collection tool should work on all these flavours, but since the largest deployment of the tool so far is on [KITE OS](https://kite.kerala.gov.in/KITE/index.php/welcome/downloads), the tool is designed to assume a KITE OS deployment by default, and the tool's default configuration values correspond to KITE OS. 

This README too reflects the fact, and focuses on KITE OS deployments. If you are using a docker-based deployment on any OS or a plain Ubuntu OS deployment, skip to the section at the bottom of this readme for instructions on pre-requisites and for customizing the tool's configuration values.

## What data is collected by the tool?

* The ELL database, in the form of a mysqldump sql file
* Audio files (webm/ogg)

All of the collected data is packaged into a single tar.gz file. The rest of this document

## Prerequisites

### 1. Software checks

If you are running the ELL on KITE OS, all software prerequisites should already be met. But please do make the following checks just to be sure.

1. The presence of Python 3.8 + on the system. Do this by opening a terminal window and executing the command:

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

### 2. Configuration

1. The ELL uses a MySQL database. The tool connects to this database to download data. The configuration parameters to connect to the database are specified in the **collect.conf** file. The values reflect the ELL installation defaults on KITE OS. No action is required if you are running the tool on the default KITE OS setup of the ELL.
2. The tool assumes the ELL has been installed under the **/opt/lampp/** directory. If you are running ELL on KITE OS, this is the default installation location and no action is required to change anything.


### 3. Mandatory information required by the tool

#### School code
When you run the tool, it will prompt you to enter a **school code**. This code uniquely identifies your school and associates the collected data with the school. This information is mandatory for the tool to execute. Contact your IT administrator to obtain this information before executing the tool.


## How to execute the script
## Reading the logs
## Upload the data file
