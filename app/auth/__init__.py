from flask import Blueprint
from passlib.context import CryptContext

auth = Blueprint('auth', __name__)

# Passlib config:
pwd_context = CryptContext(
    # Replace this list with the hash(es) you wish to support.
    # The first hash will be the default
    schemes=["pbkdf2_sha256"]
    # Optionally, set the number of rounds that should be used.
    # Leaving this alone is usually safe, and will use passlib's defaults.
    ## pbkdf2_sha256__rounds = 29000,
    )

from . import views