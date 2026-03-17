
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from api.models import Task
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def check_upcoming_tasks():
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    
    upcoming_tasks = Task.objects.filter(
        deadline__gte=now,
        deadline__lte=tomorrow
    ).exclude(status='done')
    
    for task in upcoming_tasks:
        subject = "[Assignment Reminder] Your task is due soon"
        body = f'Hello, your task "{task.title}" is due on {task.deadline.strftime("%Y-%m-%d %H:%M:%S")}. Please complete it on time.'
        
        try:
            send_mail(
                subject,
                body,
                None, # DEFAULT_FROM_EMAIL
                [task.user.email],
                fail_silently=False,
            )
            logger.info(f"Sent reminder for task {task.id} to {task.user.email}")
        except Exception as e:
            logger.error(f"Failed to send email for task {task.id}: {e}")

class Command(BaseCommand):
    help = 'Starts the reminder scheduler'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler()
        
        scheduler.add_job(check_upcoming_tasks, 'cron', hour=8, minute=0)

        self.stdout.write("Starting scheduler...")
        try:
            check_upcoming_tasks()
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write("Stopping scheduler...")
