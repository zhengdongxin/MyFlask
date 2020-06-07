#!/usr/bin/python3

import sys
from app import create_app

app = create_app()

if __name__ == "__main__":
    if sys.argv[1:]:
        port = sys.argv[1:][0]
        app.run(host="0.0.0.0", port=port)
    app.run(debug=True)
