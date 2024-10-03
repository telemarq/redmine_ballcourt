
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="BALLCOURT",
    settings_files=['/etc/ballcourt.toml', 'ballcourt.toml', '.secrets.toml'],
    load_dotenv=True,
)

