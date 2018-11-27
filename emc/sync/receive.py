#-*- coding: UTF-8 -*-
from five import grok
import json
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from zope import event
# from emc.sync.interfaces import ISendWechatEvent
# from emc.sync.events import SendWechatEvent
from Products.statusmessages.interfaces import IStatusMessage
import six
import os
import inspect
import hashlib
import logging
# from emc.sync.parser import parse_user_msg
# from emc.sync.utilities import to_binary, to_text                     
    
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import xml.etree.ElementTree as ET
from cStringIO import StringIO

class Recieve(BrowserView):
    """receive weixin.
    """
    
    grok.context(INavigationRoot)
    grok.name('receive_userdata')
    grok.require('zope2.View')

        
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
        from zope import event
        import pdb
        pdb.set_trace()
#         from emc.sync.events import ReceiveWechatEvent

        ev = self.request.environ

        if ev['REQUEST_METHOD'] =="GET":
            # valid request from weixin

            return self.abort(403)           
            
        else:

            body =  self.request.get('BODY')
            users = self.parserxml(body.strip())
# 分析原始xml，返回名类型message实例            
#             message = parse_user_msg(body)
            logging.info("Receive message")                    
#             event.notify(ReceiveWechatEvent(message))
            return ""

    def str2file(self,text):
        "transfer text to ram file object"

        return StringIO(text)
    
    def fetch_userinfo(self,element):
        "parameter element is a 'xml.etree.ElementTree.Element' instance"
        user={}
        user['username'] = element.findtext("./identityNo")
        user['fullname'] = element.findtext("./userName")
        user['safe_level'] = element.findtext("./psnSecretLevelCode")
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
        users = root.findall("./data/user")
        return users

    def exist(self,id):
        "check user iff is exist"
        mt = getToolByName(self.context, 'portal_membership')
        return mt.getMemberById(id) is None
    
    def create_user(self,udic):
        "create a user that its properties come from udic parameters" 
        regtool = getToolByName(site.context, 'portal_registration')
        username = udic['username']
        passwd = "[%s}" % username
        properties = {
                      'safe_level': udic['safe_level'],
        # Full name must always be utf-8 encoded
                      'fullname': udic['fullname'].encode("utf-8"),
                      'email': ''
                      }
        try:
        # addMember() returns MemberData object
            member = regtool.addMember(username, passwd, properties=properties)
        except ValueError, e:
        # Give user visual feedback what went wrong
#             IStatusMessage(request).addStatusMessage(_(u"Could not create the user:") + unicode(e), "error")
            return None        
               
