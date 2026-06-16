import re
from flask import (Blueprint, render_template, request, redirect, url_for, jsonify)
from application.queries.customer_cards_queries import (
    get_all_customer_cards, get_customer_card_by_number,
    create_customer_card, update_customer_card,
    delete_customer_card, get_all_percents,
    get_customer_purchase_statistics,
    is_universal_customer
)
from application.decorators import login_required, role_required

customer_card_routes = Blueprint("customer_card_routes", __name__)


def is_valid_name(text):
    if not text:
        return True
    return bool(re.match(r"^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ'\s\-]+$", text))


@customer_card_routes.route('/customer_cards')
@login_required
@role_required("manager", "cashier")
def customer_cards():
    search = request.args.get('search', '').strip()
    percent = request.args.get('percent', '').strip()

    customer_cards = get_all_customer_cards(search, percent)
    percents = get_all_percents()
    return render_template("customer_cards/customer_cards.html", customer_cards=customer_cards, search=search,
                           percents=percents, percent=percent)


@customer_card_routes.route('/customer_cards/add', methods=['POST'])
@login_required
@role_required("manager", "cashier")
def add_customer_card():
    data = request.form

    card_number = data.get("card_number", "").strip()
    cust_surname = data.get("cust_surname", "").strip()
    cust_name = data.get("cust_name", "").strip()
    cust_patronymic = data.get("cust_patronymic", "").strip()
    phone_number = data.get("phone_number", "").strip()

    if not card_number or not cust_surname or not cust_name or not phone_number:
        return jsonify({"success": False, "message": "All required fields must be filled!"})

    if not is_valid_name(cust_surname) or not is_valid_name(cust_name) or not is_valid_name(cust_patronymic):
        return jsonify({"success": False, "message": "Customer names must contain only letters!"})

    if len(phone_number) > 13:
        return jsonify({"success": False, "message": "Phone number cannot exceed 13 characters!"})

    try:
        pct = float(data.get("percent", 0))
        if pct < 0 or pct > 100:
            return jsonify({"success": False, "message": "Discount percent must be between 0 and 100!"})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid discount percent value!"})

    try:
        if get_customer_card_by_number(card_number):
            return jsonify({"success": False, "message": "Customer card with this number already exists!"})

        create_customer_card(data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@customer_card_routes.route('/customer_cards/get/<card_number>')
@login_required
@role_required("manager", "cashier")
def get_customer_card(card_number):
    customer_card = get_customer_card_by_number(card_number)
    if not customer_card:
        return jsonify({"success": False, "message": "Card not found!"}), 404
    return jsonify(dict(customer_card))


@customer_card_routes.route('/customer_cards/<card_number>/edit', methods=['POST'])
@login_required
@role_required("manager", "cashier")
def edit_customer_card(card_number):
    data = request.form

    cust_surname = data.get("cust_surname", "").strip()
    cust_name = data.get("cust_name", "").strip()
    cust_patronymic = data.get("cust_patronymic", "").strip()
    phone_number = data.get("phone_number", "").strip()

    if not cust_surname or not cust_name or not phone_number:
        return jsonify({"success": False, "message": "Required fields cannot be empty!"})

    if not is_valid_name(cust_surname) or not is_valid_name(cust_name) or not is_valid_name(cust_patronymic):
        return jsonify({"success": False, "message": "Customer names must contain only letters!"})

    if len(phone_number) > 13:
        return jsonify({"success": False, "message": "Phone number cannot exceed 13 characters!"})

    try:
        pct = float(data.get("percent", 0))
        if pct < 0 or pct > 100:
            return jsonify({"success": False, "message": "Discount percent must be between 0 and 100!"})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid discount percent value!"})

    try:
        update_customer_card(card_number, data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@customer_card_routes.route('/customer_cards/<card_number>/delete', methods=['POST'])
@login_required
@role_required("manager")
def delete_customer_card_route(card_number):
    try:
        delete_customer_card(card_number)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Cannot delete this customer card because it has already been used in existing store receipts. Operational history must be preserved."
        }), 400

@customer_card_routes.route('/customer_cards/<card_number>/statistics')
@login_required
@role_required('manager')
def customer_statistics(card_number):
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    stats = get_customer_purchase_statistics( card_number, date_from, date_to)
    universal = is_universal_customer(card_number, date_from, date_to)
    if not stats:
        return jsonify({
            "success": True,
            "receipts_count": 0,
            "total_spent": 0,
            "average_receipt": 0,
            "universal_customer": universal
        })

    return jsonify({
        "success": True,
        "receipts_count": stats["receipts_count"],
        "total_spent": float(stats["total_spent"]),
        "average_receipt": float(stats["average_receipt"]),
        "universal_customer": universal
    })