"""Persistence for extracted business contacts."""

from typing import List, Tuple

from .database import get_connection
from .schemas import BusinessInfo


def save_contact(info: BusinessInfo, raw_email: str) -> int:
    """Insert a contact and return its new id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO contacts
                (name, title, company, email, phone, address, website,
                 other_info, raw_email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                info.name,
                info.title,
                info.company,
                info.email,
                info.phone,
                info.address,
                info.website,
                info.other_info,
                raw_email,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_contacts() -> List[Tuple]:
    """Return all contacts, newest first."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT * FROM contacts ORDER BY extracted_at DESC"
        )
        return cursor.fetchall()
    finally:
        conn.close()


def delete_contact(contact_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
    finally:
        conn.close()
