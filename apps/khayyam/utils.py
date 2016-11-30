"""
Created on Oct 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os, sys
import subprocess as sub
import logging
import smtplib
import traceback
# import pandas as pd 
# from string import Template

#============================
# Django imports
#----------------------------
# from .models import SublibraryInformation
from django.conf import settings
from .models import Workflow
from django.contrib.auth.models import User


logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=logging.DEBUG
    )


#==================================================
# Kronos initilaization and run
#--------------------------------------------------
def get_samples_file(data, *args, **kwargs):
    """make a samples file and save it in temporary working directory."""
    return "/genesis/shahlab/IDAP/dev/test/samples_file_short.txt"


class Runner(object):

    """
    Helper to hanlde:
    - sourcing python virtualenv
    - ssh connection
    - command execution
    """

    @staticmethod
    def add_pyvenv(cmd):
        """add 'source /path/to/virtualenv/python' to the command."""
        pyvenv = settings.KRONOS_PYTHON_VENV
        return 'source {0} && {1}'.format(pyvenv, cmd)

    @staticmethod
    def add_ssh(cmd):
        """add 'ssh genesis' to the command."""
        cmd = ' '.join([
        'export',
        'SGE_ROOT=%s' % settings.SGE_ROOT,
        'SGE_QMASTER_PORT=%s' % settings.SGE_QMASTER_PORT,
        'SGE_EXECD_PORT=%s' % settings.SGE_EXECD_PORT,
        'SGE_CELL=%s' % settings.SGE_CELL,
        '&&',
        cmd
        ])
        return 'ssh genesis {}'.format(repr(cmd))

    @staticmethod
    def run_cmd(cmd, cmd_args=[]):
        """run command with the given arguments."""
        cmd = cmd + ' ' + ' '.join(cmd_args)
        proc = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        print "Running command:", cmd #cmd_args
        cmdout, cmderr = proc.communicate()
        if cmdout:
            # logging.info(cmdout)
            print "cmdout: ", cmdout
        if cmderr:
            # logging.error(cmderr)
            print "cmderr: ", cmderr
        return proc.returncode


class Kronos(object):
    
    """
    Kronos manager.
    """

    def __init__(self, workflow_instance):
        """initialize."""
        self.workflow = workflow_instance
        self.script_template = None

        self.components_dir = None
        self.drmaa_library_path = None
        self.python_installation = None

    def init(self):
        """initialize the workflow."""
        pass

    def run(self):
        """run the workflow."""
        pass

    def make_script(self):
        """make the executable run script."""
        pass

    def picasso_hand_shake(self):
        """interface to Picasso app."""
        pass

def notify(run):
    """ send an email notification when workflow status changes."""
    Subject = "Status update for {}".format(run.get_workflow_display())
    To = User.objects.get(username=run.user).email
    From = settings.EMAIL_ADDRESS
    msg = "Hi {0},\n\n"
    msg += "There is an update in the status ({1}) of your workflow "
    msg += "run: {2}."
    msg += "\n\nPlease do NOT reply to this email."
    msg += "\nShalab Dev Team."
    url = settings.HOST_URL
    url += run.get_absolute_url()
    msg = msg.format(run.user, run.get_status_display(), url)
    Body = '\r\n'.join([
        'To: %s' % To,
        'From: %s' % From,
        'Subject: %s' % Subject,
        '', msg
        ])
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(From, settings.EMAIL_PASSWORD)
        server.sendmail(From, [To], Body)
        server.close()
        return True
    except:
        traceback.print_exc()
        return False
