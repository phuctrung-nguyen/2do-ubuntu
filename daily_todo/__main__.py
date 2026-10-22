"""Launch with python3 -m daily_todo from the project root."""

from .app import Todo


def main():
    return Todo().run(None)


if __name__ == '__main__':
    raise SystemExit(main())
