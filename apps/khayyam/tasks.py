"""
Created on Oct 28, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import absolute_import

import os
from random import randint
import subprocess as sub


#============================
# Django imports
#----------------------------
from .models import Run, Workflow
from .utils import FileHandler, get_samples_file
from django.conf import settings


#============================
# Celery imports
#----------------------------
from celery import shared_task, Task


#============================
# Helpers
#----------------------------
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
        return 'ssh genesis {}'.format(repr(cmd))

    @staticmethod
    def run_cmd(cmd, cmd_args=[]):
        """run command with the given arguments."""
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


#============================
# Celery tasks
#----------------------------
class KronosTask(Task):
    # ignore_result = True
    default_retry_delay = 2 * 60
    max_tries = 3
    file_handler = FileHandler()

    def run(self, pk, *args, **kwargs):
        """perform kronos run command."""
        try:
            print "running the workflow ..."
            cmd = self.makecmd(pk)
            cmd = Runner.add_pyvenv(cmd)
            cmd = Runner.add_ssh(cmd)
            retval = Runner.run_cmd(cmd)
            return retval

        except Exception as exc:
            raise self.retry(exc=exc)
    
    def makecmd(self, pk):
        """create a Kronos run command."""
        run = Run.objects.get(pk=pk)
        njobs = run.kronos.num_jobs
        npipes = run.kronos.num_pipelines
        run_id = run.run_id

        wf = Workflow.objects.get(pk=run.workflow)            
        cdir = wf.components_dir
        pname = str(wf)
        python = wf.python_venv
        setup_file = wf.setup_file
        config_file = wf.config_file

        scheduler = "sge"
        wdir = os.path.join(str(wf), run.user)
        samples_file = get_samples_file(run.get_data(), wdir)
        qsub_options = ' -hard -q shahlab.q'
        qsub_options += ' -pe ncpus {num_cpus}'
        qsub_options += ' -l mem_free={mem} -l mem_token={mem}'
        qsub_options += ' -w n'
        qsub_options = repr(qsub_options)

        cmd = "kronos run"
        cmd_args = [
        '-b', "sge",
        '-c', cdir,
        '-e', pname,
        '-i', samples_file,
        '-j', njobs,
        '-n', npipes,
        '-p', python,
        '-q', qsub_options,
        '-r', run_id,
        '-s', setup_file,
        '-w', wdir,
        '-y', config_file,
        ]
        return cmd + ' ' + ' '.join(map(str, cmd_args))
        
    def on_success(self, retval, task_id, *args, **kwargs): 
        """update the run status on success."""       
        msg = "this is in on_success call from task {0} with return value {1}."
        id = args[0][0]
        run = Run.objects.get(pk=id)
        status = ["D", "F", "S"]
        i = randint(0,2)
        run.status = status[i]
        run.save()
        print msg.format(task_id, retval)

run_workflow = KronosTask()

@shared_task
def stop_workflow(id):
    """force a workflow to stop running."""
    run = Run.objects.get(pk=id)
    run.status = "S"
    run.save()
    print "stopped the workflow with run ID %s" % run.run_id
