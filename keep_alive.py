"""
Keep-alive HTTP server for Render / Heroku deployments.
"""

import os
import threading
from flask import Flask, Response

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return Response("OK", status=200)

def _run():
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )

def keep_alive(loop=None):
    """Start keep-alive server in a daemon thread.
    
    Args:
        loop: Optional event loop parameter (accepted for compatibility, not used).
    """
    t = threading.Thread(target=_run)
    t.daemon = True
    t.start()
