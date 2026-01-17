from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.utils.timezone import now

# cron command 15 3 * * * /path/to/venv/bin/python /path/to/project/manage.py purge_old_ics --days 7

class Command(BaseCommand):
    help = "delete /media/ical/* older than N days (default 7)"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7)

    def handle(self, *args, **opts):
        cutoff = now() - timedelta(days=opts["days"])
        # list files under "ical/"
        dirs, files = default_storage.listdir("ical")
        deleted = 0
        for name in files:
            path = f"ical/{name}"
            try:
                mtime = default_storage.get_modified_time(path)
            except Exception:
                # fall back to created time if available
                mtime = default_storage.get_created_time(path)
            if mtime < cutoff:
                default_storage.delete(path)
                deleted += 1
        self.stdout.write(f"deleted {deleted} files")