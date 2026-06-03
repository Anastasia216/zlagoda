from flask import(Blueprint, render_template, request, redirect, url_for, jsonify)
from application.queries.employee_queries import (get_all_employees, get_employee_by_id, create_employee,
                                                  update_employee, delete_employee)
from application.validation.employee_validation import(validate_employee)
employee_routes = Blueprint('employee_routes', __name__)

@employee_routes.route('/employees')
def employees():
    search = request.args.get('search','')
    employees = get_all_employees(search)
    return render_template('employees/employees.html', employees=employees, search=search)

@employee_routes.route('/employees/add')
def employees_add_page():
    return render_template('employees/add.html')

@employee_routes.route('/employees/add', methods=['POST'])
def add_employees():
    data = request.form
    create_employee(data)
    return jsonify({
        "success": True
    })

@employee_routes.route('/employees/get/<id_employee>')
def get_employee(id_employee):
    id_employee = get_employee_by_id(id_employee)
    return jsonify(dict(id_employee))

@employee_routes.route('/employees/<id_employee>/edit')
def employees_edit_page(id_employee):
    employee = get_employee_by_id(id_employee)
    return render_template('employees/edit.html', employee=employee)

@employee_routes.route('/employees/<id_employee>/edit', methods=['POST'])
def employee_edit(id_employee):
    data = request.form
    # errors = validate_employee(data)
    # if errors:
    #     employee = get_employee_by_id(id_employee)
    #     return render_template('employees/edit.html', errors=errors, old=data)
    update_employee(id_employee,data)
    return jsonify({
        "success": True
    })

@employee_routes.route('/employees/<id_employee>/delete')
def employee_delete_route(id_employee):
    delete_employee(id_employee)
    return jsonify({
        'success':True
    })

@employee_routes.route('/employees/reports')
def employees_reports_page():
    return render_template('employees/reports.html')

#@employee_routes.route('/employees/reports', methods=['POST'])
#def employee_reports():
##############################################################
###################################################################
# need to write it later
###################################################################
