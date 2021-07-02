"""
Shopcarts Service

Paths:
------
GET /shopcarts - Returns a list all of all Shopcarts
GET /shopcarts/{id} - Returns the Shopcart with a given shopcart_id and product_id
POST /shopcarts/{id}/items/{id} - creates a new Shopcart record in the database
PUT /shopcarts/{id}/items/{id} - updates a Shopcart record in the database
DELETE /shopcarts/{id}/items/{id} - deletes a Shopcart record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from . import status # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Shopcart, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for root URL")
    return (
        jsonify(
            name="Shopcarts REST API Service",
            version="1.0",
            #paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  ADD A NEW SHOPCART ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:product_id>", methods=["POST"]) #"/shopcarts/<int:shopcart_id>/items/<int:product_id>"
def create_shopcart(shopcart_id, product_id):
    """
    Creates a new Shopcart item
    This endpoint will create a Shopcart item based on the data in the body that is posted
    """
    app.logger.info("Request to create a Shopcart item")
    if request.is_json:
        app.logger.info("got json")
    req = request.get_json()
    app.logger.info(req)
    check_content_type("application/json")
    #shopcart = Shopcart()
    #shopcart.deserialize(request.get_json())
    #shopcart.create()
    #message = shopcart.serialize()
    #location_url = url_for("get_shopcarts", shopcarts_id=shopcart.shopcart_id, product_id=shopcart.product_id, _external=True)

    #app.logger.info("Shopcart with shopcart_id [%d] and product_id [%d created")
    #return make_response(
    #    jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    #)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Shopcart.init_db(app)

def check_content_type(media_type):
    """Check that the media type is correct"""
    content_type = request.headers.get("Content_Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type)
    )
