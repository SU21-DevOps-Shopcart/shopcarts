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
from flask import Flask, json, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from . import status # HTTP Status Codes
from werkzeug.exceptions import NotFound

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
            #paths=url_for("list_items", _external=True)
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL ITEMS
######################################################################
@app.route("/items", methods=["GET"])
def list_items():
    """ Return all of the items """
    app.logger.info("Request for item list")
    
    return make_response(
        "Reminder: return all the items",
        status.HTTP_200_OK
    )

######################################################################
# UPDATE AN EXISTING ITEM
######################################################################
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """
    Update a item

    This endpoint will update a item based the body that is posted
    """
    app.logger.info("Request to update item with id: %s", item_id)
    return(
        "Reminder: update an existing item with id",
        status.HTTP_200_OK
    )

######################################################################
# DELETE A ITEM
######################################################################

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    Delete a Item

    This endpoint will delete a Item based the id specified in the path
    """
    app.logger.info("Request to delete item with id: %s", item_id)

    return(
        "Reminder: delete an existing item with id",
        status.HTTP_200_OK
    )



######################################################################
# RETRIEVE A SHOPCART ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:product_id>", methods=["GET"])
def get_item(shopcart_id, product_id):
    """
    Retrieve a single Shopcart item
    This endpoint will return a Shopcart item based on it's shopcart_id and product_id
    """
    app.logger.info("Request for Shopcart item with shopcart_id: %d and product_id: %d", shopcart_id, product_id)
    shopcart = Shopcart.find(shopcart_id, product_id)
    if not shopcart:
        raise NotFound("Shopcart with shopcart_id '{}' and product_id '{}' was not found.".format(shopcart_id, product_id))

    app.logger.info("Returning Shopcart item with shopcart_id: %d and product_id: %d", shopcart.shopcart_id, shopcart.product_id)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
#  ADD A NEW SHOPCART ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["POST"])
def create_item(shopcart_id):
    """
    Creates a new Shopcart item
    This endpoint will create a Shopcart item based on the data in the body that is posted
    """
    app.logger.info("Request to create a Shopcart item")
    check_content_type("application/json")
    shopcart = Shopcart()
    data = request.get_json()
    data["shopcart_id"] = shopcart_id
    shopcart.deserialize(data)
    item = Shopcart.find(shopcart_id, data["product_id"])
    if not item:
        shopcart.create()
        message = shopcart.serialize()
        location_url = url_for("get_item", shopcart_id=shopcart.shopcart_id, product_id=shopcart.product_id, _external=True)

        app.logger.info("Shopcart with shopcart_id [%d] and product_id [%d created")
        return make_response(
            jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
        )
    else:
        print(item.quantity)
        shopcart.quantity = str(int(item.quantity) + 1) 
        shopcart.update()
        message = shopcart.serialize()
        location_url = url_for("get_item", shopcart_id=shopcart.shopcart_id, product_id=shopcart.product_id, _external=True)

        app.logger.info("Shopcart item already created")
        return make_response(
            jsonify(message), status.HTTP_200_OK, {"Location": location_url}
        )

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
