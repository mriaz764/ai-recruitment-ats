import uuid
from datetime import datetime, timezone


def generate_ics(
    title: str,
    description: str,
    location: str,
    start_at: datetime,
    end_at: datetime,
    organizer_email: str,
    attendee_emails: list[str],
) -> str:
    """Generates an RFC-5545 compliant iCalendar string."""
    # ICS requires UTC time formatted as YYYYMMDDTHHMMSSZ
    fmt = "%Y%m%dT%H%M%SZ"
    start_str = start_at.astimezone(timezone.utc).strftime(fmt)
    end_str = end_at.astimezone(timezone.utc).strftime(fmt)
    now_str = datetime.now(timezone.utc).strftime(fmt)
    
    uid = f"{uuid.uuid4()}@your-ats.com"

    attendees_str = "\n".join(
        [f"ATTENDEE;RSVP=TRUE:mailto:{email}" for email in attendee_emails]
    )

    # Use strict line breaks required by calendar clients
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Your ATS//Calendar Service//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now_str}",
        f"DTSTART:{start_str}",
        f"DTEND:{end_str}",
        f"SUMMARY:{title}",
        f"DESCRIPTION:{description}",
        f"LOCATION:{location}",
        f"ORGANIZER:mailto:{organizer_email}",
        attendees_str,
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        "BEGIN:VALARM",
        "TRIGGER:-PT15M",
        "DESCRIPTION:Reminder",
        "ACTION:DISPLAY",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    return "\n".join(line for line in ics_lines if line)