"""Randomised test data generators for unique, repeatable test runs."""
import uuid

from faker import Faker

_fake = Faker()

_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def unique_email(domain: str = "example.com") -> str:
    return f"ae_{uuid.uuid4().hex[:12]}@{domain}"


def new_user() -> dict:
    """A fresh, randomised user payload used across UI sign-up and API flows."""
    birth_date = _fake.date_of_birth(minimum_age=18, maximum_age=60)
    first_name = _fake.first_name()
    last_name = _fake.last_name()
    return {
        "name": f"{first_name} {last_name}",
        "email": unique_email(),
        "password": "Pass@1234",
        "title": "Mr",
        "birth_date": str(birth_date.day),
        "birth_month": _MONTHS[birth_date.month - 1],
        "birth_year": str(birth_date.year),
        "first_name": first_name,
        "last_name": last_name,
        "company": _fake.company(),
        "address1": _fake.street_address(),
        "address2": _fake.secondary_address(),
        "country": "United States",
        "state": _fake.state(),
        "city": _fake.city(),
        "zipcode": _fake.zipcode_in_state("CA"),
        "mobile_number": _fake.phone_number(),
    }


def payment_details() -> dict:
    return {
        "name_on_card": _fake.name(),
        "card_number": "4242 4242 4242 4242",
        "cvc": str(_fake.random_int(100, 999)),
        "expiry_month": str(_fake.random_int(1, 12)),
        "expiry_year": str(_fake.random_int(2027, 2030)),
    }


def contact_message() -> dict:
    return {
        "name": _fake.name(),
        "email": unique_email(),
        "subject": "Automated contact form submission",
        "message": _fake.paragraph(),
    }