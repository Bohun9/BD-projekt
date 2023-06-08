from flask import Blueprint
from .db import get_cursor, get_table

bp = Blueprint("query", __name__, url_prefix="/query")

# queries statements are in sql functions


# by default row converted to json is list of values, even when cursor factory is specified
def with_names(table):
    return list(map(dict, table))


@bp.route("/participants/<int:id>", methods=("GET",))
def query_participants(id):
    # print(get_table("OrganizationMember"))
    # print(get_table("Participation"))
    # print(get_table("Protest"))
    get_cursor().execute("SELECT * FROM query_participants(%s);", (id,))
    result = get_cursor().fetchall()
    return with_names(result)
