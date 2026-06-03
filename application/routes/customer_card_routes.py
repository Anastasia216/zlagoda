from flask import (Blueprint, render_template, request, redirect, url_for, jsonify)
from application.queries.customer_cards_queries import (get_all_customer_cards, get_customer_card_by_number, create_customer_card, update_customer_card, delete_customer_card)
from application.validation.customer_card_validation import validate_customer_card

customer_card_routes = Blueprint("customer_card_routes", __name__)

@customer_card_routes.route('/customer_cards')
def customer_cards():
    search = request.args.get('search', '')
    customer_cards = get_all_customer_cards(search)
    return render_template("customer_cards/customer_cards.html", customer_cards=customer_cards, search=search)

@customer_card_routes.route('/customer_cards/add')
def add_customer_card_page():
    return render_template("customer_cards/add.html")

@customer_card_routes.route('/customer_cards/add', methods=['POST'])
def add_customer_card():
    create_customer_card(request.form)
    return jsonify({
        "success": True
    })

@customer_card_routes.route('/customer_cards/get/<card_number>')
def get_customer_card(card_number):

    customer_card = get_customer_card_by_number(card_number)

    return jsonify(dict(customer_card))

@customer_card_routes.route('/customer_cards/<card_number>/edit')
def edit_customer_card_page(card_number):
    customer_card = get_customer_card_by_number(card_number)
    return render_template('customer_cards/edit.html', customer_card=customer_card)

@customer_card_routes.route('/customer_cards/<card_number>/edit', methods=['POST'])
def edit_customer_card(card_number):
    data = request.form
    errors = validate_customer_card(data)
    if errors:
        customer_card = get_customer_card_by_number(card_number)
        return render_template('customer_cards/edit.html', errors=errors, old=data, customer_card=customer_card)
    update_customer_card(card_number, data)
    return jsonify({
        "success": True
    })

@customer_card_routes.route('/customer_cards/<card_number>/delete')
def delete_customer_card_route(card_number):
    delete_customer_card(card_number)
    return jsonify({
        'success': True
    })

#@customer_card_routes.route('/customer_cards/reports')
#def customer_card_reports_page():
  #  return render_template("customer_cards/reports.html")

