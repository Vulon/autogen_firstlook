from autogen_firstlook.engine import Engine
import asyncio
from autogen_firstlook.logs import config_logs
from autogen_firstlook.settings import Settings


def main():
    settings = Settings()
    config_logs(settings)
    engine = Engine(settings)
    asyncio.run(engine.run())


if __name__ == "__main__":
    main()
