import os
import tempfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing import z2
from zope.configuration import xmlconfig
from zope.interface import alsoProvides
import pkg_resources

from zope.configuration import xmlconfig

class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import emc.sync
        xmlconfig.file('configure.zcml', emc.sync, context=configurationContext)        
        import emc.policy
        xmlconfig.file('configure.zcml', emc.policy, context=configurationContext)
                      
    def tearDownZope(self, app):
        pass
    
    def setUpPloneSite(self, portal):
     
        applyProfile(portal, 'emc.sync:default')
#        applyProfile(portal, 'xtshzz.policy:default')
     

FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(bases=(FIXTURE,), name="emcsync:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(bases=(FIXTURE,), name="emcsync:Functional")
