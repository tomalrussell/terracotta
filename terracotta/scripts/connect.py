"""scripts/connect.py

Use Flask development server to serve Terracotta client app.
"""

from typing import NoReturn

import os
import threading
import webbrowser
import urllib.request
from urllib.error import HTTPError, URLError

import click

from terracotta.scripts.click_types import Hostname
from terracotta.scripts.http_utils import find_open_port


@click.command(
    'connect',
    short_help='Connect to a running Terracotta instance and interactively '
               'explore data in it.'
)
@click.argument('terracotta-hostname', required=True, type=Hostname())
@click.option('--no-browser', is_flag=True, default=False, help='Do not open browser')
@click.option('--port', type=click.INT, default=None,
              help='Port to use [default: first free port between 5100 and 5199].')
def connect(terracotta_hostname: str, no_browser: bool = False, port: int = None) -> NoReturn:
    """Connect to a running Terracotta and interactively explore data in it.

    First argument is hostname and port to connect to (e.g. localhost:5000).
    """
    from terracotta.client.flask_api import create_app

    test_url = f'{terracotta_hostname}/keys'

    try:
        with urllib.request.urlopen(test_url, timeout=2):
            pass
    except (HTTPError, URLError):
        click.echo(
            f'Could not connect to {test_url}, check hostname and ensure '
            'that Terracotta is running on the server', err=True
        )
        raise click.Abort()

    # find suitable port
    port_range = [port] if port is not None else range(5100, 5200)
    port = find_open_port(port_range)
    if port is None:
        click.echo(f'Could not find open port to bind to (ports tried: {port_range})', err=True)
        raise click.Abort()

    def open_browser() -> NoReturn:
        webbrowser.open(f'http://127.0.0.1:{port}/')

    if not no_browser:
        threading.Timer(2, open_browser).start()

    client_app = create_app(terracotta_hostname)

    if os.environ.get('TC_TESTING'):
        return

    client_app.run(port=port)
