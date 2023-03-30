# KITE ECUBE English Language Lab Data Collection Tool

## About

This is the KITE ECUBE English Language Lab (ELL) data collection tool. 

Read more about KITE [here](https://kite.kerala.gov.in) and the ECUBE ELL [here](https://kite.kerala.gov.in/ecubeenglish.html)

The ECUBE ELL is built with Moodle, the popular free and open source Learning Management System (LMS). However, While the Moodle installation itself is a standard one, the ELL installation process achieves the rather complex feat of installing all of the software dependencies first, including PHP, the Apache webserver and the MySQL database. The ELL installation package is therefore fully self-contained and is installed using a well-oiled installation script.
The tool collects data from the language lab database and the language lab computer's filesystem. The objective is to be able to analyze 

1. students' activities in the LMS and their performance (from the data recorded in the database), and 
2. students' spoken language outputs (from audio recordings saved to the file system).



The Moodle installation is preloaded with student usernames using a standardized naming scheme the incorporates the class, section and individual student roll number values. The teacher role has a similarly standardized username, as does the 'hm' (headmaster / headmistress) role.

The ELL is supported on KITE's own customized Ubuntu distribution KITE OS and on the standard Ubuntu 20.04 distribution. A docker based package is also available [here](https://docker.com) that can of course run anywhere.

### What data is collected?

* The Moodle database, in the form of a mysqldump sql file
* Audio files (webm/ogg)


### Who is this tool intended for
This script is intended for use by educational organizations that run the KITE ECUBE ELL software. Some technical proficiency is required to ensure the necessary prerequisites are met and to actually execute the tool. The person running the tool should be able to understand the following content and familiar with executing the steps as indicated.

### Do this before running the script

#### 1. Software
If you are running the ELL on KITE OS, software prerequisites should already be met. No action is required. But please do make the following checks just to be sure.
1. Python 3.8 +
2. The ELL is installed under /opt/lampp
3. 

#### 2. Configuration
#### 3. Information required

###  How to execute the script
### Reading the logs
### Upload the data file
