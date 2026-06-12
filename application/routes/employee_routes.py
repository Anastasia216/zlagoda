from uuid import uuid4
from datetime import datetime, date
from flask import(Blueprint, render_template, request, redirect, url_for, jsonify)
from application.queries.employee_queries import (get_all_employees, get_employee_by_id, create_employee, update_employee, delete_employee,get_all_roles)
from application.validation.employee_validation import(validate_employee)
from application.decorators import login_required, role_required
employee_routes = Blueprint('employee_routes', __name__)

@employee_routes.route('/employees')
@login_required
@role_required('manager')
def employees():
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    employees = get_all_employees(search, role)
    roles = get_all_roles()
    today = date.today()

    max_birth_date = today.replace(
        year=today.year - 18
    )

    return render_template(
        'employees/employees.html', employees=employees, search=search, role=role, roles=roles, max_birth_date=max_birth_date.isoformat())
@employee_routes.route('/employees/add')
@login_required
@role_required('manager')
def employees_add_page():
    return render_template('employees/add.html')

@employee_routes.route('/employees/add', methods=['POST'])
@login_required
@role_required('manager')
def add_employees():
    data = request.form.to_dict()

    errors = validate_employee(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "<br>".join(errors)
        })

    data["id_employee"] = str(uuid4())
    id_employee = create_employee(data)
    return jsonify({
        "success": True,
        "id_employee": data["id_employee"]
    })

@employee_routes.route('/employees/get/<id_employee>')
@login_required
@role_required('manager')
def get_employee(id_employee):
    id_employee = get_employee_by_id(id_employee)
    return jsonify(dict(id_employee))

@employee_routes.route('/employees/<id_employee>/edit')
@login_required
@role_required('manager')
def employees_edit_page(id_employee):
    employee = get_employee_by_id(id_employee)
    return render_template('employees/edit.html', employee=employee)

@employee_routes.route('/employees/<id_employee>/edit', methods=['POST'])
@login_required
@role_required('manager')
def employee_edit(id_employee):
    data = request.form
    errors = validate_employee(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "<br>".join(errors)
        })
    update_employee(id_employee,data)
    return jsonify({
        "success": True
    })

@employee_routes.route('/employees/<id_employee>/delete', methods=['POST'])
@login_required
@role_required('manager')
def employee_delete_route(id_employee):
    try:
        delete_employee(id_employee)
        return jsonify({
            'success': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': "Cannot delete this employee because they have generated active register receipts. Operational history must be preserved."
        }), 400

@employee_routes.route('/employees/reports')
@login_required
@role_required('manager')
def employees_reports_page():
    return render_template('employees/reports.html')
