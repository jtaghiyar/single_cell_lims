import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from khayyam.models import Workflow
from khayyam.utils import Runner

class Command(BaseCommand):
    help = "Clone registered workflows."

    def _is_uptodate(self, path):
        res = True
        if os.path.dirname(path) != settings.WORKFLOWS_ARCHIVE:
            res = False
        if not os.path.exists(path):
            res = False
        return res

    def handle(self, *args, **options):
        for wf in Workflow.objects.all():
            try:
                if wf.archive_path and self._is_uptodate(wf.archive_path):
                    continue
                self.stdout.write('Cloning workflow "%s" ...' % wf)
                dest = os.path.join(settings.WORKFLOWS_ARCHIVE, "%s" % wf)
                cmd = "git clone"
                cmd_args = [wf.repository, dest]
                returncode = Runner.run_cmd(cmd, cmd_args)
                if returncode == 0:
                    ## checkout to the proper version
                    cmd = "cd {} && git checkout {}".format(dest, wf.version)
                    cmd_args = ['&&', 'cd ..']
                    returncode = Runner.run_cmd(cmd, cmd_args)
                    if returncode == 0:
                        wf.archive_path = dest
                        wf.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                'Successfully cloned workflow "%s"' % wf
                                )
                            )
            except:
                raise CommandError('Failed to clone workflow "%s"' % wf)

