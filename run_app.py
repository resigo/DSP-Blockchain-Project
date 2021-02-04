from app import app
import os
import sys

if len(sys.argv) == 1:
    sys.argv.append("5000")
    sys.argv.append("8000")

if len(sys.argv) == 2:
    sys.argv[2].append("8000")


os.environ['APPLICATION_PORT'] = sys.argv[1]
os.environ['CONNECTED_NODE_PORT'] = sys.argv[2]


app.run(debug=True, port=sys.argv[1])
