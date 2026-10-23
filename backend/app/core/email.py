import logging

logger = logging.getLogger(__name__)


def send_email_with_attachment_async(
    to_emails: list[str],
    subject: str,
    body: str,
    attachment_name: str,
    attachment_content: str,
) -> None:
    """
    Mock email dispatcher for local development.
    Uses FastAPI BackgroundTasks to run outside the main request thread.
    """
    logger.info("========== SIMULATING EMAIL DISPATCH ==========")
    logger.info(f"To: {', '.join(to_emails)}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body: {body}")
    logger.info(
        f"Attachment Included: {attachment_name} ({len(attachment_content)} bytes)"
    )
    logger.info("===============================================")
