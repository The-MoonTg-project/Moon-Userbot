import os
import environs

try:
    env = environs.Env()
    env.read_env("./.env")
except FileNotFoundError:
    print("No .env file found, using os.environ.")

api_id = int(os.getenv("API_ID", env.int("API_ID")))
api_hash = os.getenv("API_HASH", env.str("API_HASH"))

STRINGSESSION = os.getenv("STRINGSESSION", env.str("STRINGSESSION"))

second_session = os.getenv("SECOND_SESSION", env.str("SECOND_SESSION", ""))

db_type = os.getenv("DATABASE_TYPE", env.str("DATABASE_TYPE"))
db_url = os.getenv("DATABASE_URL", env.str("DATABASE_URL", ""))
db_name = os.getenv("DATABASE_NAME", env.str("DATABASE_NAME"))

apiflash_key = os.getenv("APIFLASH_KEY", env.str("APIFLASH_KEY"))
rmbg_key = os.getenv("RMBG_KEY", env.str("RMBG_KEY", ""))
vt_key = os.getenv("VT_KEY", env.str("VT_KEY", ""))
gemini_key = os.getenv("GEMINI_KEY", env.str("GEMINI_KEY", ""))
vca_api_key = os.getenv("VCA_API_KEY", env.str("VCA_API_KEY", ""))
cohere_key = os.getenv("COHERE_KEY", env.str("COHERE_KEY", ""))

pm_limit = int(os.getenv("PM_LIMIT", env.int("PM_LIMIT", 4)))

test_server = bool(os.getenv("TEST_SERVER", env.bool("TEST_SERVER", False)))
modules_repo_branch = os.getenv(
    "MODULES_REPO_BRANCH", env.str("MODULES_REPO_BRANCH", "master")
)
