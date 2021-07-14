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
@app.route("/shopcarts", methods=["GET"])
def list_items():
    """ Return all of the Shopcarts """
    app.logger.info("Request for Shopcarts list")
    shopcarts = []
    results = []
    shopcart_param = request.args.get("shopcart-id")
    product_param = request.args.get("product-id")
    shopcart_id = (int(shopcart_param)) if shopcart_param else None
    product_id = (int(product_param)) if product_param else None
    if shopcart_id and product_id:
        shopcarts = Shopcart.find(shopcart_id, product_id)
    elif shopcart_id:
        shopcarts = Shopcart.find_by_shopcart_id(shopcart_id)
    else:
        shopcarts = Shopcart.all()

    if not shopcarts:
            app.logger.info("Returning 0 items")
            message = []
            return make_response(
                jsonify(message),
                status.HTTP_200_OK
            )
    if shopcart_id and product_id:
        results = [shopcarts.serialize()]
    else:
        results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d items", len(results))
    return make_response(
        jsonify(results),
        status.HTTP_200_OK
    )

######################################################################
# QUERY AN ITEM FROM A CUSTOMER'S SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def list_one_shopcart_item(shopcart_id):
    """ Query an item from a customer's Shopcart """
    app.logger.info("Request an item from the Shopcart")

    product_param = request.args.get("product-id")
    product_id = int(request.args.get("product-id")) if product_param else None

    if product_id:
        shopcarts = Shopcart.find(shopcart_id, product_id)
    else:
        shopcarts = Shopcart.find_by_shopcart_id(shopcart_id)

    if not shopcarts:
            app.logger.info("Returning 0 items")
            message = "no items found"
            return make_response(
                jsonify(message),
                status.HTTP_404_NOT_FOUND
            )
    if shopcart_id and product_id:
        results = [shopcarts.serialize()]
    else:
        results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d items", len(results))
    return make_response(
        jsonify(results),
        status.HTTP_200_OK
    )

######################################################################
# UPDATE AN EXISTING ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:product_id>", methods=["PUT"])
def update_item(shopcart_id,product_id):
    """
    Update a item

    when add item existing in database, will increase its quantity
    and changed price when was added

    This endpoint will update a item based the body that is posted
    """
    app.logger.info("Request to update item in shopcart: %s with id: %s",shopcart_id, product_id)
    check_content_type("application/json")

    shopcart = Shopcart.find(shopcart_id, product_id)

    if not shopcart:
        raise NotFound("item with shopcart id '{}' and item id '{}' was not found.".format(shopcart_id,product_id))
    
    else:
        shopcart_dict_database = shopcart.serialize()
        quantity = shopcart_dict_database['quantity']
        quantity = quantity + 1
        request_dict = request.get_json()
        request_dict['quantity'] = str(quantity)
        request_dict['shopcart_id'] = shopcart_id
        shopcart.deserialize(request_dict)
        shopcart.update()
        return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A ITEM
######################################################################

@app.route("/shopcarts/<int:shopcart_id>/items/<int:product_id>", methods=["DELETE"])
def delete_item(shopcart_id,product_id):
    """
    Delete a Item

    This endpoint will delete a Item based the id specified in the path
    """
    app.logger.info("Request to delete item in shopcart: %s with id: %s", shopcart_id,product_id)

    shopcart = Shopcart.find(shopcart_id, product_id)

    if shopcart:
        shopcart.delete()
    return make_response(jsonify(""), status.HTTP_204_NO_CONTENT)



######################################################################
# CLEAR SHOPCART
######################################################################

@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def clear_shopcart(shopcart_id):
    """
    Delete All items in specific cart

    This endpoint will delete a Item based the id specified in the path
    """
    app.logger.info("Request to delete items in shopcart: %s ", shopcart_id)

    shopcart = Shopcart.find_by_shopcart_id(shopcart_id)

    results = [item.serialize() for item in shopcart]

    if results:
        for i in results:
            print(i)
            shopcart = Shopcart.find(shopcart_id, i['product_id'])
            shopcart.delete()
    return make_response(jsonify(""), status.HTTP_204_NO_CONTENT)




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
        # message = shopcart.serialize()
        message = "item already exists"
        location_url = url_for("get_item", shopcart_id=shopcart.shopcart_id, product_id=shopcart.product_id, _external=True)

        app.logger.info("Shopcart item with shopcart_id: %d and product_id: %d already created", shopcart.shopcart_id, shopcart.product_id)
        return make_response(
            jsonify(message), status.HTTP_409_CONFLICT, {"Location": location_url}
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
