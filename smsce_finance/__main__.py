from smsce_finance.cli import App


def start() -> None:
    """Configure logs and start cli app."""
    App().parse()


if __name__ == "__main__":
    start()
