#-*- coding: UTF-8 -*-
import json
import hmac
from hashlib import sha1 as sha
from Products.CMFCore.utils import getToolByName
from emc.sync.testing import INTEGRATION_TESTING,FUNCTIONAL_TESTING 


from zope.component import getUtility
from plone.keyring.interfaces import IKeyManager

from plone.app.testing import TEST_USER_ID, login, TEST_USER_NAME, \
    TEST_USER_PASSWORD, setRoles
from plone.testing.z2 import Browser
import  unittest
from plone.namedfile.file import NamedBlobFile
import os
import requests

def getFile(filename):
    """ return contents of the file with the given name """
    filename = os.path.join(os.path.dirname(__file__), filename)
    return open(filename, 'r')

class TestView(unittest.TestCase):
    
#     layer = FUNCTIONAL_TESTING
# 
#     def setUp(self):
#         portal = self.layer['portal']
#         setRoles(portal, TEST_USER_ID, ('Manager',))                              
#         self.portal = portal
                         
        
    def test_post_xml(self):
        def _make_xml(content):
            return """
            <?xml version="1.0" encoding="gb2312"?>
<root>
<mdtype>User</mdtype> 报文类型
<data>
<User>
<xh>9999999</xh>     排序
<code>0001A110000000000T4H</code> 系统流水号
<endFlag>0</endFlag>    是否离职代码  0为否 1为离职
<id>0001A110000000000T4H</id>    系统流水号
<fcFlag>0</fcFlag>   封存标志
<identityNo>110101197909181529</identityNo> 身份证号
<name>顾蕾</name>   姓名
<gender>2</gender> 性别代码    1为男 2为女
<userName>顾蕾</userName>   姓名
<psnSecretLevelName>重要</psnSecretLevelName>  密级
<psnSecretLevelCode>80</psnSecretLevelCode>  密级代码
<deptCode>B000001173</deptCode>  部门主数据编码
<mdCode>D000004740</mdCode>  用户主数据编码
</User>
</data>
</root>
        """ % content
        headers = {'Content-Type': 'application/xml'}
        request = self.layer['request']        
        keyManager = getUtility(IKeyManager)
        secret = keyManager.secret()
        auth = hmac.new(secret, TEST_USER_NAME, sha).hexdigest()
        #模拟用户数据库发来数据
        request.form = {
                        '_authenticator': auth,
                        'echostr':"ok",
                        'timestamp':'20141110',
                        'nonce':'2018',
                        'signature':'73ced4a61919b480adcc70f151e99f5edd5690c5',
                        'data': _make_xml("haha")}
        view = self.portal.restrictedTraverse('@@receive_userdata')
        result = view.render()

    def test_post_xml_with_requests(self):
        def _make_xml(content):
            return """
            <?xml version="1.0" encoding="utf-8"?>
<root>
<mdtype>User</mdtype>
<data>
<User>
<xh>9999999</xh>
<code>0001A110000000000T4H</code>
<endFlag>1</endFlag>
<id>0001A110000000000T4H</id>
<fcFlag>0</fcFlag>
<identityNo>%(idNo)s</identityNo>
<name>%(name)s</name>
<gender>2</gender>
<userName>%(name)s</userName>
<psnSecretLevelName>%(level)s</psnSecretLevelName>
<psnSecretLevelCode>80</psnSecretLevelCode>
<deptCode>B000001173</deptCode>
<mdCode>D000004740</mdCode>
</User>
</data>
</root>
        """ % dict(idNo=content,
#                    name= "sss",
                    name= u"顾蕾".encode("utf-8"),
#                    level = "ooo")                 
                    level = u"重要".encode("utf-8"))
        xml = _make_xml('110101197909181550')
        headers = {'Content-Type': 'application/xml'}

        requests.post('http://127.0.0.1:8080/Plone8/@@receive_userdata',auth=('admin2', 'qzm2tEZ5'),data=xml, headers=headers)        

 
