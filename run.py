"""Local entrypoint to run the Flask app."""

from __future__ import annotations

import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", "5050")),
        debug=False,
        use_reloader=False,
    )
