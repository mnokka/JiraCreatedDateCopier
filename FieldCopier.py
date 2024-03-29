# Used to copy values from one custom field to another
#
# 9.10.2019 mika.nokka1@gmail.com 
# 
# NOTE: For this POC removed .netrc authetication, using pure arguments
# 
#JQL query for chosen isseus: JQLQuery="project=xxxxx"  (incoded)
# SKIP variable for possible dry run
# Target date picker custom field incoded
# 
#
# Python V2
#
#from __future__ import unicode_literals

#import openpyxl 
import sys, logging
import argparse
#import re
from collections import defaultdict
from ChangeIssue import Authenticate  # no need to use as external command
from ChangeIssue import DoJIRAStuff

import glob
import re
import os
import time
import unidecode
from jira import JIRA, JIRAError
from collections import defaultdict

start = time.clock()
__version__ = u"0.1"

# should pass via  parameters
#ENV="demo"
ENV=u"PROD"

logging.basicConfig(level=logging.DEBUG) # IF calling from Groovy, this must be set logging level DEBUG in Groovy side order these to be written out



def main(argv):
    
    JIRASERVICE=u""
    JIRAPROJECT=u""
    PSWD=u''
    USER=u''
  
    logging.debug (u"--Created date field copier starting --") 

 
    parser = argparse.ArgumentParser(usage="""
    {1}    Version:{0}     -  mika.nokka1@gmail.com
    
    USAGE:
    ---password | -w <JIRA password>
    --service   | -s <JIRA service>
    --user   | -u <JIRA user>

    Change project ID, target date picker ID in code
    (use SKIP variable for dry run)

    """.format(__version__,sys.argv[0]))

   
    parser.add_argument('-v','--version', help='<Version>', action='store_true')
    
    parser.add_argument('-w','--password', help='<JIRA password>')
    parser.add_argument('-u','--user', help='<JIRA user>')
    parser.add_argument('-s','--service', help='<JIRA service>')
    #parser.add_argument('-p','--project', help='<JIRA project>')
 
        
    args = parser.parse_args()
    
    if args.version:
        print ("Tool . version: %s"  % __version__)
        sys.exit(2)    
           
    #filepath = args.filepath or ''
    
    JIRASERVICE = args.service or ''
    PSWD= args.password or ''
    USER= args.user or ''
    #RENAME= args.rename or ''
    #ASCII=args.ascii or ''
    
    # quick old-school way to check needed parameters
    if (JIRASERVICE=='' or  PSWD=='' or USER=='' ):
        parser.print_help()
        sys.exit(2)
        
     
    Authenticate(JIRASERVICE,PSWD,USER)
    jira=DoJIRAStuff(USER,PSWD,JIRASERVICE)
    
    Parse(JIRASERVICE,JIRAPROJECT,PSWD,USER,ENV,jira)



############################################################################################################################################
# Parse attachment files and add to matching Jira issue
#

#NOTE: Uses hardcoded sheet/column value

def Parse(JIRASERVICE,JIRAPROJECT,PSWD,USER,ENV,jira):

    # Change these according the need, or add as program arguments
    JQLQuery="project=MIG"  # TODO: ARGUMENT

    i=1      
    SKIP=0 # DRYRUN=1 , real operation =0
    for issue in jira.search_issues(JQLQuery, maxResults=200):

                #TODO:BUG: if more than one match will fail
                myissuekey=format(issue.key)
                logging.debug("Jira issue key (from Jira): {0}".format(myissuekey))
                #logging.debug("ISSUE: {0}:".format(issue))
                #logging.debug("ID{0}: ".format(issue.id))

                # Change these according the need, or add as program arguments
                TargetCustomField=issue.fields.customfield_14705  #TODO:ARGUMENT  
                TargetCustomFieldString="customfield_14705"
                SourceFieldValue=issue.fields.created
                
                #issue.fields.created
                logging.debug("Source created date field value: {0}".format(SourceFieldValue))
                logging.debug("Target custom field ID string: {0}".format(TargetCustomFieldString))
                logging.debug("Target custom field value: {0}".format(TargetCustomField))
                
       
                
                if (SKIP==0):
                    #sys.exit(5)  #to be sure not to doit first time
                    try:
                        #issue.update(fields={SourceCustomFieldString: int(TargetCustomField)})  #TODO:ARGUMENT
                        issue.update(fields={TargetCustomFieldString: SourceFieldValue})  #TODO:ARGUMENT
                        logging.debug("*** Copy operation done***")
                        time.sleep(0.7) # prevent jira crashing for script attack
                    except JIRAError as e: 
                        logging.debug(" ********** JIRA ERROR DETECTED: ***********")
                        logging.debug(" ********** Statuscode:{0}    Statustext:{1} ************".format(e.status_code,e.text))
                    #sys.exit(5) 
                    else: 
                        logging.debug("All OK")
                    #sys.exit(5)
                else:
                    logging.debug("SKIPPED ACTIONS. DRYRUN ONLY")
                
                i=i+1
                logging.debug("---------------------------------------------------------------")


    
    
  
        
    end = time.clock()
    totaltime=end-start
    print ("Time taken:{0} seconds".format(totaltime))
       
            
    print ("*************************************************************************")
        

 
  

    
logging.debug ("--Python exiting--")
if __name__ == "__main__":
    main(sys.argv[1:]) 