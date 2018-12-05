#-*- coding: UTF-8 -*-
from Products.CMFCore.utils import getToolByName
from zope import event
import logging                      
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import xml.etree.ElementTree as ET
from emc.memberArea.events import BackMemberCreatedEvent

class Recieve(BrowserView):
    """receive weixin.
    """

    def abort(self,status):
        template ="""            
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf8" />
            <title>Error: %s</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans;}
              body {background-color: #fff; border: 1px solid #ddd;
                    padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error: %s</h1>
            <p>不可以通过 GET 方式直接进行访问。</p>
        </body>
    </html>
    """ % (status,status) 
        return template     
    
    def  __call__(self):
        ev = self.request.environ
        if ev['REQUEST_METHOD'] =="GET":
            # valid request from weixin
            return self.abort(403)                      
        else:
            body =  self.request.get('BODY')
            users = self.parserxml(body.strip())
            for i  in users:
                user = self.fetch_userinfo(i)
                tmp = self.create_user(user)
                logging.info("Receive users")                   
            return ""
    
    def fetch_userinfo(self,element):
        "parameter element is a 'xml.etree.ElementTree.Element' instance"
        user={}
        user['username'] = element.findtext("./identityNo")
        user['fullname'] = element.findtext("./userName")
        user['safe_level'] = element.findtext("./psnSecretLevelCode")
        user['available'] = element.findtext("./endFlag").strip()
        return user
        
    def parserxml(self,xml):
        """
        parser user data xml,fetch all users data
        """
        root = ET.fromstring(xml)
#         xmlp = ET.XMLParser(encoding="gb2312")
#         fobj = self.str2file(xml)
#         f = ET.parse(fobj,parser=xmlp)
        mdtype = root.findtext("./mdtype")
        if mdtype != "User":return []
        ug = root.iterfind("./data/User")
        return ug

    def getMermberByid(self,id):
        ""
        mt = getToolByName(self.context, 'portal_membership')
        return mt.getMemberById(id)        
        
    def exist(self,id):
        "check user iff is exist"

        return self.getMermberByid(id) is None
    
    def create_user(self,udic):
        "create a user that its properties come from udic parameters" 
        regtool = getToolByName(self.context, 'portal_registration')
        username = udic['username']
        aval = udic['available']

        if aval=="0":return 0
        elif not self.exist(username) :return 0
        passwd = "[%s}" % username
        properties = {'username':username,
                      'safe_level': udic['safe_level'],
                      'email':'demo@plone.org',
        # Full name must always be utf-8 encoded
                      'fullname': udic['fullname'].encode("utf-8")
                      }             
        try:
        # addMember() returns MemberData object
            member = regtool.addMember(username, passwd, properties=properties)     
            if member != None:
                event.notify(BackMemberCreatedEvent(member))
                return 1
        except ValueError, e:
            logging.info("Can not create the user:" + unicode(e))           
        return None                  
