import os
from flask import Flask, g
from api.v1.endpoints.perspective import perspective_bp
from api.database.database import close_db_connection

# Initialize the Flask application
app = Flask(__name__)

# Register the blueprint for the API routes
app.register_blueprint(perspective_bp, url_prefix='/api/v1')

# Add a teardown function to close the database connection and cursor
@app.teardown_appcontext
def teardown_db(exception=None):
    conn = g.pop('db_conn', None)
    curr = g.pop('db_curr', None)
    close_db_connection(conn, curr)

if __name__ == '__main__':
    app.run(debug=True)