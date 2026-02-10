from app import app
from run import app as run
from extensions import db
from services.stock_service import Stock  # Import models
from services.billing_service import Billing  # Import models
from services.reports_service import Report  # Import models
from services.reminders_service import Reminder  # Import models
#from services.templates_service import Template  # Import models
from services.account_service import Account  # Import models
from services.dashboard_service import Dashboard  # Import models
from services.party_service import Party  # Import models
from services.staff_service import Staff  # Import models
from services.billing_service import Billing  # Import models
from services.party_service import Party  # Import models

# Initialize the app and db
with run.app_context():
    # Create the database tables if they don't exist
    db.create_all()

    print("Database tables created successfully!")
