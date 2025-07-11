import sys
from cli_app import run_cli
from web_app import run_web_api

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        run_web_api()
    else:
        run_cli()
