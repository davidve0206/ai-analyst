from sqlalchemy.orm import sessionmaker

from src.configuration.db import RecipientEmail


def add_recipient_email(session_maker: sessionmaker, emails: str):
    session = session_maker()
    try:
        # Add new emails
        for email in emails:
            session.add(RecipientEmail(email=email))
        session.commit()
    finally:
        session.close()


def remove_recipient_email(session_maker: sessionmaker, id: int):
    session = session_maker()
    try:
        # Remove a single recipient email by ID
        session.query(RecipientEmail).filter(RecipientEmail.id == id).delete()
        session.commit()
    finally:
        session.close()


def get_recipient_emails(session_maker: sessionmaker) -> list[str]:
    session = session_maker()
    try:
        results = session.query(RecipientEmail).all()
        return [result.email for result in results]
    finally:
        session.close()
