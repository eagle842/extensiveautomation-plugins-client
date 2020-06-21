#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive automation project
# Copyright (c) 2010-2018 Denis Machard
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
#
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensiveautomation.org
# -------------------------------------------------------------------

try:
    from PyQt4.QtCore import ( QObject, pyqtSignal )         
except ImportError:
    from PyQt5.QtCore import ( QObject, pyqtSignal )    

import Settings

import requests

import json

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import urllib.parse

import xml.etree.ElementTree as ET
import os
import html
import time
from xml.sax.saxutils import escape

class RestHpAlmClient(QObject):
    """
    Rest HP ALM client
    """
    Error = pyqtSignal(object)
    ConnectionOk = pyqtSignal()
    
    TestsExported = pyqtSignal(list, dict)
    ResultsExported = pyqtSignal(list, dict)
    LogAuthStatus = pyqtSignal(str)
    LogTestsStatus = pyqtSignal(str)
    LogResultsStatus = pyqtSignal(str)
    
    def __init__(self, parent, core, proxies={}):
        """
        """
        QObject.__init__(self, parent)
        self.__core = core
        
        self.WsProxies = proxies
        
        self.WsLwssoCookie = None
        self.WsQcSession = None
        self.WsXsrfToken = None
        
        self.loadConfig()

    def loadConfig(self):
        """
        """
        self.WsUsername = self.core().settings().cfg()["credentials"]["login"]
        self.WsPassword = self.core().settings().cfg()["credentials"]["password"]
        self.WsCheckSsl = self.core().settings().cfg()["qc-server"]["check-ssl"]
        # self.WsDomain = self.core().settings().cfg()["qc-server"]["domain"]
        self.WsProject = self.core().settings().cfg()["qc-server"]["project"]
        self.WsUrl = self.core().settings().cfg()["qc-server"]["url"]
        if self.WsUrl.endswith("/"): self.WsUrl = self.WsUrl[:-1]

    def core(self):
        """
        """
        return self.__core

    
    def RestFindTest(self, logger, testName):
        """
        """
        logger("Finding test (%s) in test plan..."  % testName)
        r = requests.get("%s/rest/raven/1.0/api/test?jql=%s" % (self.WsUrl, urllib.parse.quote('summary ~ "%s"'%testName)),
                        auth=requests.auth.HTTPBasicAuth(self.WsUsername, self.WsPassword ),
                        headers = {'content-type': 'application/json; charset=utf-8'},
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
 
        if r.status_code != 200:
            raise Exception("Unable to get tests from testplan - %s - %s" % (r.status_code, r.text ) )
        
        response = json.loads(r.text)
        ret = None
        if len(response) > 0:
            if "key" in response[0].keys():
                testId = response[0]["id"]
                testKey = response[0]["key"]
                ret = testKey
        return ret

           
    def RestCreateTest(self, logger, testName, testDescription):
        """
        """
        logger("Creating test (%s) in test plan" % testName )
        
        ret = None

        data = {
                "fields": {
                    "project":
                    {
                        "key": "%s" % self.WsProject
                    },
                    "summary": "%s" % testName,
                    "description": "%s" % testDescription,
                    "issuetype": {
                        "name": "Test"
                    }
                }
            }
        payload_data = json.dumps(data)
        r = requests.post("%s/rest/api/2/issue" % (self.WsUrl),
                        auth=requests.auth.HTTPBasicAuth(self.WsUsername, self.WsPassword ),
                        headers = {'content-type': 'application/json; charset=utf-8'},
                        data=payload_data,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            raise Exception("Unable to add test in JIRA - %s - %s" % (r.status_code, r.text.encode("utf8") ) )

        # response = ET.fromstring( r.text.encode("utf8") )
        # testId = response.find("./Fields/Field[@Name='id']/Value")
        response = json.loads(r.text)
        logger("Response when creating test (%s) in test plan : %s" % (testName, response) )
        ret = None
        if "key" in response.keys():
            testId = response["id"]
            testKey = response["key"]
            ret = testKey
        return ret

        
    def RestCreateRun(self, logger, testId, testStatus):
        """
        """
        logger("Creating run" )
        data = {
                "info" : {
                    "summary" : "Execution of automated test by Extensive Automation",
                    "description" : "This execution is automatically created by Extensive Automation",
                    "user" : "%s" % self.WsUsername
                },
                "tests" : [
                    {
                        "testKey" : "%s" % testId,
                        "status" : "%s" % testStatus
                    }
                        ]
            }
        payload_data = json.dumps(data)
        r = requests.post("%s/rest/raven/1.0/import/execution" % (self.WsUrl),
                        auth=requests.auth.HTTPBasicAuth(self.WsUsername, self.WsPassword ),
                        headers = {'content-type': 'application/json; charset=utf-8'},
                        data=payload_data,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to add test in JIRA - %s - %s" % (r.status_code, r.text.encode("utf8") ) )

        # response = ET.fromstring( r.text.encode("utf8") )
        # testId = response.find("./Fields/Field[@Name='id']/Value")
        response = json.loads(r.text)
        # logger("response for creating run : %s" % response)
        # if len(response) > 0:
        testKey = None
        if "key" in response['testExecIssue'].keys():
            testId = response['testExecIssue']["id"]
            testKey = response['testExecIssue']["key"]
            ret = testKey
        # testId = response["id"]
        # testKey = response["key"]
        ret = testKey
        return ret

    def RestGetTestInstanceSteps(self, logger, runId):
        """
        """
        logger("Get steps from test instance" )
        
        r = requests.get("%s/rest/domains/%s/projects/%s/runs/%s/run-steps" % (self.WsUrl, self.WsDomain, self.WsProject, runId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to get steps according to the test instances - %s - %s" % (r.status_code, r.text ) )

        oXml = ET.fromstring(r.text.encode("utf8"))
        steps = self.__findSteps(xml=oXml)
        return steps
    
    def RestUpdateRun(self, logger, runId, runStatus):
        """
        """
        logger("Updating run" )

        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % runStatus )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )

        r = requests.put("%s/rest/domains/%s/projects/%s/runs/%s" % (self.WsUrl, self.WsDomain, self.WsProject, runId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to update run - %s - %s" % (r.status_code, r.text ) )
        return True

    def RestUpdateRunStep(self, logger, stepId, runId, stepStatus, stepActual):
        """
        """
        logger("Running steps" )

        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run-step\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % stepStatus )
        data.append( "<Field Name=\"actual\"><Value>%s</Value></Field>" %  self.__gethtml(stepActual) )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )

        r = requests.put("%s/rest/domains/%s/projects/%s/runs/%s/run-steps/%s" % (self.WsUrl, 
                                                                                  self.WsDomain, 
                                                                                  self.WsProject, 
                                                                                  runId, 
                                                                                  stepId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to update run step - %s - %s" % (r.status_code, r.text ) )
        return True
        
    def RestAuthenticate(self, logger):
        """
        """
        self.WsLwssoCookie = None
        self.WsQcSession = None
        self.WsXsrfToken = None
        
        almAuth = "<alm-authentication><user>%s</user><password>%s</password></alm-authentication>""" % (self.WsUsername, 
                                                                                                         escape(self.WsPassword))
        logger("Connection to the REST API..." )
        r = requests.post("%s/authentication-point/alm-authenticate" % self.WsUrl,
                            headers = {'Content-Type': 'application/xml;charset=utf-8'},
                            data = almAuth.encode("utf8"),
                            proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception('Unable to connect to the rest api: %s - %s' % (r.status_code, r.text) )

        cookies = r.headers["set-cookie"]
        self.WsLwssoCookie = cookies.split("LWSSO_COOKIE_KEY=")[1].split(";", 1)[0]
        
        
        logger("Creating session..." )
        r = requests.post("%s/rest/site-session" % self.WsUrl,
                            cookies={'LWSSO_COOKIE_KEY': self.WsLwssoCookie},
                            proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            raise Exception('Unable to create the session to the rest api: %s - %s' % (r.status_code, r.text) )
        logger("Session ready" )
        
        cookies = r.headers["set-cookie"]
        self.WsQcSession = cookies.split("QCSession=")[1].split(";", 1)[0]
        self.WsXsrfToken = cookies.split("XSRF-TOKEN=")[1].split(";", 1)[0]
        
        logger("Successfully connected" )
        
    def RestLogout(self, logger):
        """
        """
        logger("Disconnection from the REST API..." )
        r = requests.get("%s/authentication-point/logout" % self.WsUrl, 
                            proxies=self.WsProxies, verify=self.WsCheckSsl,
                            cookies={'LWSSO_COOKIE_KEY': self.WsLwssoCookie} )
        if r.status_code != 200:
            raise Exception('Unable to disconnect from the rest api: %s - %s' % (r.status_code, r.text) )
        logger("Disconnected" )

    def testConnection(self, config={}):
        """
        """
        try:
            # connect
            r = requests.get("%s/rest/raven/1.0/api/settings/teststatuses" % self.WsUrl,
                            headers = {'content-type': 'application/json; charset=utf-8'},
                            verify=self.WsCheckSsl,
                            auth=requests.auth.HTTPBasicAuth(self.WsUsername, self.WsPassword ))
            
            if r.status_code == 200:
                self.ConnectionOk.emit()
            else:
                self.Error.emit( "Problem with connection\n%s %s" % (r.status_code, r.text) )
        except Exception as e:
            self.logAuthStatus("Error on HP connection" )
            self.Error.emit( "%s" % e )
            
    def addTestsInTestPlan(self, testcases, config={}):    
        """
        """
        try:
            # export one testcase
            for tc in testcases:
                
                funcParams = { 'logger': self.logTestsStatus, 
                               'testName': tc['testcase'],
                               'testDescription': tc['purpose'] }
                funcParams.update(config)
                testId = self.RestFindTest(self.logTestsStatus, tc['testcase'])
                if testId is None:
                    testId = self.RestCreateTest(self.logTestsStatus, tc['testcase'], tc['purpose'])

                # # create steps
                # i = 1
                # for stp in tc["steps"]:                
                #     self.RestCreateStep(logger=self.logTestsStatus, testId=testId, 
                #                         stepName="Step%s" % i, stepDescription=stp["action"], 
                #                         stepExpected=stp["expected"])
                #     i += 1

            self.TestsExported.emit(testcases, config)
        except Exception as e:
            self.logTestsStatus("Error on test(s) export" )
            self.Error.emit( "%s" % e )

    def addResultsInTestLab(self, testcases, config={}):
        """
        """
        try:
            self.logResultsStatus("testcases = %s"% testcases)
            for tc in testcases:
                self.logResultsStatus("tc = %s"% tc)
                # Search for an existing test with the same test name and create it if needed
                testId = self.RestFindTest(self.logTestsStatus, tc['testname'])
                self.logResultsStatus("testId = %s"% testId)
                if testId is None:
                    # funcParams = { 'logger': self.logTestsStatus, 
                    #            'testName': tc['testcase'],
                    #            'testDescription': tc['purpose'] }
                    testId = self.RestCreateTest(self.logTestsStatus, tc['testname'], "")
                    self.logResultsStatus("testId2 = %s"% testId)
                self.logResultsStatus("testId3 = %s"% testId)
                self.logResultsStatus("tc[result] = %s"% tc["result"])
                # create an execution with the status of the test
                self.RestCreateRun(self.logResultsStatus, testId, tc["result"])

        except Exception as e:
            self.logResultsStatus("Error on result(s) export" )
            self.Error.emit( "%s" % e )
            
    def logAuthStatus(self, status):
        """
        """
        self.LogAuthStatus.emit( "Status: %s" % status )
        
    def logTestsStatus(self, status):
        """
        """
        self.LogTestsStatus.emit( "Status: %s" % status )
        
    def logResultsStatus(self, status):
        """
        """
        self.LogResultsStatus.emit( "Status: %s" % status )