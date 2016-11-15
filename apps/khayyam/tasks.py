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
from .utils import Runner, FileHandler, get_samples_file, notify
from django.conf import settings


#============================
# Celery imports
#----------------------------
from celery import shared_task, Task
from celery.registry import tasks


#============================
# Celery tasks
#----------------------------
class KronosTask(Task):
    # ignore_result = True
    default_retry_delay = 2 * 60
    max_tries = 3
    # file_handler = FileHandler()

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
        qsub_options = ' -hard -q shahlab.q'
        qsub_options += ' -pe ncpus {num_cpus}'
        qsub_options += ' -l mem_free={mem} -l mem_token={mem}'
        qsub_options += ' -w n'
        qsub_options = repr(qsub_options)

        wdir = os.path.join(settings.WORKING_DIR_ROOT, pname, run.user, run_id)
        # if not os.path.exists(wdir):
        #     os.makedirs(wdir)
        samples_file = get_samples_file(run.get_data(), wdir)

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
        pk = args[0][0]
        run = Run.objects.get(pk=pk)
        status = ["D", "F", "S"]
        i = randint(0,2)
        run.status = status[i]
        run.save()
        print "notifying user ..."
        success = notify(run)
        if success:
            print "notification sent."
        else:
            print "notification failed."


@shared_task(base=KronosTask)
def run_workflow(pk):
    kt = KronosTask()
    return kt.run(pk)


@shared_task
def stop_workflow(id):
    """force a workflow to stop running."""
    ## should add a task revoke here to kill
    ## the running workflow and then update the status
    run = Run.objects.get(pk=id)
    run.status = "S"
    run.save()
    print "stopped the workflow with run ID %s" % run.run_id


# def kill(pid):
#     """kill the job with the given pid."""
#     import os
#     import signal
#     os.kill(pid, signal.SIGTERM)
