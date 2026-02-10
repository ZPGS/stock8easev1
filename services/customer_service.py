from flask import Blueprint, jsonify, request, redirect, url_for, flash, render_template
from extensions import db
from services.billing_service import Billing
from services.account_service import Account
from sqlalchemy import func
from urllib.parse import quote
from datetime import datetime

# Initialize the Blueprint
customer_bp = Blueprint('customer_service', __name__)

# Helper function to generate WhatsApp link
def generate_whatsapp_link(customer_mobile, message):
    mobile = customer_mobile.replace("+", "").replace(" ", "")
    encoded_message = quote(message)
    return f"https://wa.me/{mobile}?text={encoded_message}"


# Helper function to prepare WhatsApp reminder
def prepare_whatsapp_message(customer_name, customer_mobile, reminder_details, total_amount_due, firm_name):
    if not all([customer_name, customer_mobile, reminder_details, total_amount_due, firm_name]):
        return {"status": "error", "message": "Missing required information."}

    message_body = (
        f"Dear {customer_name},\n\n"
        f"You have the following unpaid bills:\n"
        f"{reminder_details}\n\n"
        f"Total Amount Due: ₹{total_amount_due:.2f}\n\n"
        f"Please make the payment at your earliest convenience.\n\n"
        f"Regards,\n{firm_name}\nPowered by Stock8Ease"
    )

    whatsapp_url = generate_whatsapp_link(customer_mobile, message_body)

    return {
        "status": "success",
        "whatsapp_url": whatsapp_url
    }


# Route to display customer list with total unpaid bill
@customer_bp.route('/list')
def customer_list():
    customers = db.session.query(
        Billing.customer_name,
        Billing.customer_mobile,
        func.sum(Billing.total_price).label('total_unpaid')
    ).filter(Billing.status == 'Unpaid') \
     .group_by(Billing.customer_name, Billing.customer_mobile).all()

    return render_template('customer_list.html', customers=customers)


# Route to send reminder about unpaid bills
@customer_bp.route('/send_reminder/<customer_name>/<customer_mobile>', methods=['GET'])
def send_reminder(customer_name, customer_mobile):
    account = Account.query.first()
    firm_name = account.firm_name if account else "Your Store"

    unpaid_bills = Billing.query.filter_by(
        customer_name=customer_name,
        customer_mobile=customer_mobile,
        status='Unpaid'
    ).all()

    if not unpaid_bills:
        flash(f"No unpaid bills found for {customer_name}.")
        return redirect(url_for('customer_service.customer_list'))

    reminder_details = "\n".join([
        f"- Product: {bill.product_code}, Amount: ₹{bill.total_price}"
        for bill in unpaid_bills
    ])

    total_amount_due = sum(bill.total_price for bill in unpaid_bills)

    response = prepare_whatsapp_message(
        customer_name=customer_name,
        customer_mobile=customer_mobile,
        reminder_details=reminder_details,
        total_amount_due=total_amount_due,
        firm_name=firm_name
    )

    if response["status"] == "success":
        # 🔥 This opens WhatsApp on HOST device
        return redirect(response["whatsapp_url"])

    flash(response["message"])
    return redirect(url_for('customer_service.customer_list'))
