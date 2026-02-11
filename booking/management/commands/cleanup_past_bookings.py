from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from booking.models import Booking


class Command(BaseCommand):
    help = "Soft-delete past bookings older than retention policy."

    def add_arguments(self, parser):
        parser.add_argument(
            "--retention-days",
            type=int,
            default=getattr(settings, "BOOKING_RETENTION_DAYS", getattr(settings, "RETENTION_DAYS", 30)),
            help="Retention period (in days) before soft-deleting past bookings.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List eligible bookings without applying cleanup.",
        )

    def handle(self, *args, **options):
        enabled = getattr(settings, "BOOKING_CLEANUP_ENABLED", getattr(settings, "CLEANUP_ENABLED", True))
        retention_days = max(0, options["retention_days"])

        if not enabled:
            self.stdout.write(self.style.WARNING("Booking cleanup is disabled by configuration."))
            return

        cutoff = timezone.now() - timedelta(days=retention_days)
        cutoff_date = cutoff.date()
        cutoff_time = cutoff.time().replace(microsecond=0)

        eligible_q = Q(date__lt=cutoff_date) | Q(date=cutoff_date, time__lt=cutoff_time)
        queryset = Booking.all_objects.filter(is_deleted=False).filter(eligible_q)

        count = queryset.count()
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(f"Dry run: {count} booking(s) eligible for cleanup."))
            return

        now = timezone.now()
        updated = queryset.update(is_deleted=True, deleted_at=now, deleted_by_id=None)
        self.stdout.write(self.style.SUCCESS(f"Soft-deleted {updated} booking(s)."))
