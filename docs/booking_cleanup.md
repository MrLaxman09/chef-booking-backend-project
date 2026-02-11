# Booking Cleanup and Past Booking Handling

## What is implemented

- Past booking detection uses booking date + time in backend UTC comparison.
- Soft delete is used for removal:
  - `is_deleted`
  - `deleted_at`
  - `deleted_by`
- Normal booking queries exclude soft-deleted records by default.
- User dashboard separates upcoming and past bookings.
- Users can remove only their own past bookings.
- Admin dashboard supports `Upcoming`, `Past`, `All Active`, and `Archived` booking scopes.
- Admin can archive bookings and permanently delete archived bookings.

## Configuration

In `chef_booking/settings.py`:

- `BOOKING_CLEANUP_ENABLED = True`
- `BOOKING_RETENTION_DAYS = 30`
- `CLEANUP_ENABLED` and `RETENTION_DAYS` are also available aliases.

## Scheduled cleanup command

Management command:

```bash
python manage.py cleanup_past_bookings
```

Options:

```bash
python manage.py cleanup_past_bookings --dry-run
python manage.py cleanup_past_bookings --retention-days 7
```

## Suggested scheduler setup (Linux cron)

Run daily at 02:00 server time:

```cron
0 2 * * * /path/to/python /path/to/project/manage.py cleanup_past_bookings >> /var/log/chef_booking_cleanup.log 2>&1
```

## Permission rules

- User remove endpoint (`/bookings/remove/<id>/`) allows only the booking owner.
- Bulk clear endpoint (`/bookings/clear-past/`) affects only current user's past bookings.
- Admin booking actions are protected by superuser-only middleware in `custom_admin.views.admin_required`.
