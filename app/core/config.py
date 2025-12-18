import os
from dotenv import load_dotenv

load_dotenv()

# --- JWT Settings ---
# A strong, secret key is required for signing JWTs.
# For production, this should be set via environment variables.
# A fallback key is provided for local development, but this is not secure.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_insecure_default_secret_key_for_dev_only")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_HOURS = 24
