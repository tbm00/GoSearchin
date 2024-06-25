import os
import sys
import __init__

# Add the parent directory of 'app' to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)