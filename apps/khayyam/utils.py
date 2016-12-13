"""
Created on Oct 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os, sys
import subprocess as sub
import logging
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
    user = User.objects.get(username=run.user)
    addr_to = user.email
    addr_from = settings.EMAIL_ADDRESS
    url = settings.HOST_URL
    url += run.get_absolute_url()
    status = run.get_status_display()
    if status == "Done":
        color = "green"
    else:
        color = "red"

    msg = MIMEMultipart('multipart')
    msg['Subject'] = "Status update for your workflow run"
    msg['To'] = addr_to
    msg['From'] = addr_from
    html = """
    <html>
        <head></head>
        <body>
            <p>Hi {user},</p>
            <p>There is an update in the status of the following workflow run:<p>
            <ul style="list-style-type:cicle">
                <li><b>Run ID:</b> <a href="{url}">{run_id}</a></li>
                <li><b>Workflow name:</b> {workflow_name}</li>
                <li><b>Date:</b> {date}</li>
                <li><b>Current status:</b> <font color="{color}">{status}</font></li>
            </ul>
            <p>
            You can access the results and logfiles or re-run the workflow using the Run ID link above.<br>
            Please do not reply to this email.<br><br>
            Cheers,<br>
            Integrated data analysis platform (IDAP),<br>
            Shahlab Dev Team.
            </p>
        </body>
    </html>
    """.format(
    user = user.first_name,
    run_id = run.run_id,
    workflow_name = run.get_workflow_display(),
    date = run.date,
    status = status,
    color = color,
    url = url,
    )

    body = MIMEText(html, 'html')
    msg.attach(body)

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(addr_from, settings.EMAIL_PASSWORD)
        server.sendmail(addr_from, [addr_to], msg.as_string())
        server.close()
        return True
    except:
        traceback.print_exc()
        return False

