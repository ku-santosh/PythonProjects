import os
from flask import Flask, g
from api.v1.endpoints.perspective import perspective_bp
from api.v1.endpoints.column_state import column_state_bp
from api.v1.endpoints.filter_model import filter_model_bp
from api.database.database import close_db_connection

# Initialize the Flask application
app = Flask(__name__)

# Register the blueprint for the API routes
app.register_blueprint(perspective_bp, url_prefix='/api/v1/perspectives')
app.register_blueprint(column_state_bp, url_prefix='/api/v1/perspectives/column_state')
app.register_blueprint(filter_model_bp, url_prefix='/api/v1/perspectives/filter_model')


# Add a teardown function to close the database connection and cursor
@app.teardown_appcontext
def teardown_db(exception=None):
    conn = g.pop('db_conn', None)
    curr = g.pop('db_curr', None)
    close_db_connection(conn, curr)

if __name__ == '__main__':
    app.run(debug=True)