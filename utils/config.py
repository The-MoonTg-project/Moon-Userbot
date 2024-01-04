import environs

env = environs.Env()
env.read_env("./.env")

api_id = env.int("API_ID")
api_hash = env.str("API_HASH")

db_type = env.str("DATABASE_TYPE")
db_url = env.str("DATABASE_URL", "")
db_name = env.str("DATABASE_NAME")

apiflash_key = env.str("APIFLASH_KEY")
rmbg_key = env.str("RMBG_KEY")
vt_key = env.str("VT_KEY")
gemini_key = env.str("GEMINI_KEY")
vca_api_key = env.str("VCA_API_KEY")

pm_limit = env.int("PM_LIMIT")

test_server = env.bool("TEST_SERVER", False)
modules_repo_branch = env.str("MODULES_REPO_BRANCH", "master")