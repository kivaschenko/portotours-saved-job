try:
    from django.core.management.base import NoArgsCommand as BaseCommand
except ImportError:
    from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load base Calendar and Rules data into the db"

    def handle(self, **options):
        import datetime
        from schedule.models import Calendar
        from schedule.models import Rule

        print("checking for existing data ...")
        try:
            cal = Calendar.objects.get(name="Experience Calendar")
            print("It looks like you already have loaded Experience Calendar, quitting.")
            import sys
            sys.exit(1)
        except Calendar.DoesNotExist:
            print("Experience Calendar not found in db.")
            print("Install it...")

        print("Create Experience Calendar ...")
        cal = Calendar(name="Experience Calendar")
        cal.save()
        print("The Experience Calendar is created.")
        print("Do we need to install the most common rules?")
        try:
            rule = Rule.objects.get(name="Daily")
        except Rule.DoesNotExist:
            print("Need to install the basic rules")
            rule = Rule(frequency="YEARLY", name="Yearly", description="will recur once every Year")
            rule.save()
            print("YEARLY recurrence created")
            rule = Rule(frequency="MONTHLY", name="Monthly", description="will recur once every Month")
            rule.save()
            print("Monthly recurrence created")
            rule = Rule(frequency="WEEKLY", name="Weekly", description="will recur once every Week")
            rule.save()
            print("Weekly recurrence created")
            rule = Rule(frequency="DAILY", name="Daily", description="will recur once every Day")
            rule.save()
            print("Daily recurrence created")
        print("Rules installed.")
