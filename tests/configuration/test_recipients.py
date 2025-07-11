from src.configuration.recipients import (
    add_recipient_email,
    get_recipient_emails,
    remove_recipient_email,
)


def test_can_add_recipient_email(test_session_maker):
    email = "test@recipient.com"
    add_recipient_email(test_session_maker, email)
    emails = get_recipient_emails(test_session_maker)
    assert len(emails) == 1
    assert email == emails[0]


def test_can_get_recipient_email(test_session_maker):
    emails = ["test1@recipient.com", "test2@recipient.com", "test3@recipient.com"]
    for email in emails:
        add_recipient_email(test_session_maker, email)
    retrieved_emails = get_recipient_emails(test_session_maker)
    assert len(retrieved_emails) == len(emails)
    for email in emails:
        assert email in retrieved_emails


def test_can_remove_recipient_email(test_session_maker):
    emails = ["test1@recipient.com", "test2@recipient.com", "test3@recipient.com"]

    for email in emails:
        add_recipient_email(test_session_maker, email)

    remove_recipient_email(test_session_maker, emails[0])  # Remove the first email
    retrieved_emails = get_recipient_emails(test_session_maker)
    assert len(retrieved_emails) == len(emails) - 1
    assert emails[0] not in retrieved_emails  # First email should be removed
