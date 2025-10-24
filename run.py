import os
from flask import Flask
from flaskr import create_app  # o la función donde creas tu app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ usa el puerto que Render define
    app.run(host="0.0.0.0", port=port)