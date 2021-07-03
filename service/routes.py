"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes

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
    #"Reminder: return some useful information in json format about the service here",
    return (
        jsonify(
            name = "item demo list API service",
            version="1.0",
            paths=url_for("list_items", _external=True)
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
# RETRIEVE A ITEM
######################################################################
@app.route("/items/<int:item_id>", methods=["GET"])
def get_items(item_id):
    """
    Retrieve a single item

    This endpoint will return a item based on it's id
    """
    app.logger.info("Request for pet with id: %s", item_id)
    return (
        "Reminder: return specific item",
        status.HTTP_200_OK
    )

######################################################################
# ADD A NEW ITEM
######################################################################
@app.route("/items", methods=["POST"])
def create_items():
    """
    Creates a item
    This endpoint will create a item based the data in the body that is posted
    """
    app.logger.info("Request to create an item")
    return (
       "Reminder: add new item",
       status.HTTP_200_OK
    )

######################################################################
# UPDATE AN EXISTING ITEM
######################################################################
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_items(item_id):
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
def delete_items(item_id):
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
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Shopcart.init_db(app)


