from flask import Blueprint, request
from protest.db import add_row_to_table
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__)


def add_organization_member(name, last_name, age, login, password):
    hashed_password = generate_password_hash(password)
    add_row_to_table(
        "OrganizationMember",
        {
            "name": name,
            "last_name": last_name,
            "age": age,
            "login": login,
            "hashed_password": hashed_password,
            "organizer_privilege": False,
        },
    )
    return "OK"


@bp.route("/register_member", methods=("POST",))
def register_member():
    return add_organization_member(
        name=request.form["name"],
        last_name=request.form["last_name"],
        age=request.form["age"],
        login=request.form["login"],
        password=request.form["password"],
    )
