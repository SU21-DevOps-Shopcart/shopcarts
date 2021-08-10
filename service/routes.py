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

from datetime import datetime
import os
import sys
import logging
from flask import Flask, json, jsonify, request, url_for, make_response, abort
from flask_restx import Api, Resource, fields, reqparse, inputs
from . import status # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Shopcart, DataValidationError, DatabaseConnectionError

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for root URL")
    ## Return html instead of json
    return app.send_static_file("index.html")


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Shopcarts Demo REST API Service',
          description='This is a sample shopcarts service.',
          default='shopcarts',
          default_label='Shopcarts operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          prefix='/api'
         )

shopcart_model = api.model('Shopcart', {
    'shopcart_id': fields.Integer(require=True,
                                description='The customer record id'),
    'product_id': fields.Integer(require=True,
                                description='The product id of the item'),
    'quantity': fields.Integer(require=True,
                                description='The number of items in a shopcart'),
    'price': fields.Float(require=True,
                                description='The price of an item in a shopcart'),
    'time_added': fields.DateTime(require=True,
                                description='Time in which an item was added to a shopcart'),
    'checkout': fields.Integer(require=True,
                                description='if one item checked out, if zero item is not checked out')
})


# query string arguments
shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument('shopcart_id', type=str, required=True, help='List all Shopcarts')
shopcart_args.add_argument('product_id', type=str, required=True, help='List all Shopcarts with this product_id')

######################################################################
#  PATH: /shopcarts
######################################################################
@api.route('/shopcarts', strict_slashes=False)
class ShopcartCollection(Resource):
    """
    ShopcartCollection class
    Allows the introspection of a customer's shopcart
    GET /shopcarts - Returns all shopcarts in the db
    """

    #------------------------------------------------------------------
    # LIST ALL ITEMS
    #------------------------------------------------------------------
    @api.doc('list_shopcarts')
    @api.expect(shopcart_args, validate=True)
    @api.marshal_list_with(shopcart_model)
    def get(self):
        print('list')
        """ Return all of the Shopcarts """
        app.logger.info("Request for Shopcarts list")
        shopcarts = []
        results = []
        parser = reqparse.RequestParser()
        parser.add_argument('shopcart_id', type=int)
        parser.add_argument('product_id', type=int)
        args = parser.parse_args()
        shopcart_id = args['shopcart_id'] if args['shopcart_id'] else None
        product_id = args['product_id'] if args['product_id'] else None
        if shopcart_id and product_id:
            app.logger.info('Returning item with shopcart id %s and product id %s', args['shopcart_id'], args['product_id'])
            shopcarts = Shopcart.find(shopcart_id, product_id)
        elif not shopcart_id and product_id:
            app.logger.info('Returning all shopcarts with product id: %s', args['product_id'])
            shopcarts = Shopcart.find_by_product_id(product_id)
        elif shopcart_id and not product_id:
            app.logger.info('Returning all items with shopcart id: %s', args['shopcart_id'])
            shopcarts = Shopcart.find_by_shopcart_id(shopcart_id)
        else:
            app.logger.info('Returning unfiltered list of all shopcarts')
            shopcarts = Shopcart.all()

        if not shopcarts:
            app.logger.info("Returning 0 items")
            message = []
            return message, status.HTTP_200_OK
                
        if shopcart_id and product_id:
            results = [shopcarts.serialize()]
        else:
            results = [shopcart.serialize() for shopcart in shopcarts]
        app.logger.info("Returning %d items", len(results))
        return results, status.HTTP_200_OK        


######################################################################
#  PATH: /shopcarts/{shopcart_id}
######################################################################
@api.route('/shopcarts/<shopcart_id>')
@api.param('shopcart_id', 'The Shopcart identifier')
class ShopcartResource(Resource):
    """
    ShopcartResource class
    Allows the operations on a customer's shopcart
    GET /shopcarts/{shopcart_id} - Retrieves items from a customer's shopcart
    POST /shopcarts/{shopcart_id} - Adds a new item to a customer's shopcart
    DELETE /shopcarts/{shopcart_id} - Removes all items from a customer's shopcart
    """

    #------------------------------------------------------------------
    # ADD A NEW SHOPCART ITEM
    #------------------------------------------------------------------
    @api.doc('create_shopcarts')
    @api.response(400, 'The posted data was not vaild')
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self, shopcart_id):
        """
        Creates a new Shopcart item
        This endpoint will create a Shopcart item based on the data in the body that is posted
        """
        app.logger.info("Request to create a Shopcart item")
        check_content_type("application/json")
        shopcart = Shopcart()
        app.logger.debug('Payload = %s', api.payload)
        app.logger.info(api.payload)
        api.payload["shopcart_id"] = int(shopcart_id)
        # api.payload["time_added"] = datetime.strptime(api.payload["time_added"], "%a, %d %b %Y %H:%M:%S")
        shopcart.deserialize(api.payload)
        item = Shopcart.find(api.payload["shopcart_id"], api.payload["product_id"])
        if not item:
            shopcart.create()
            app.logger.info("Shopcart with shopcart_id [%d] and product_id [%d created", shopcart.shopcart_id, shopcart.product_id)
            location_url = api.url_for(ShopcartResource, shopcart_id=shopcart.shopcart_id, product_id=shopcart.product_id, _external=True)
            return shopcart.serialize(), status.HTTP_201_CREATED, {"Location": location_url}
        else:
            app.logger.info("Shopcart item with shopcart_id: %d and product_id: %d already created", shopcart.shopcart_id, shopcart.product_id)
            location_url = api.url_for(ShopcartResource, shopcart_id=shopcart.shopcart_id, product_id=shopcart.product_id, _external=True)
            return "item already exists", status.HTTP_409_CONFLICT, {"Location": location_url}
                

    #------------------------------------------------------------------
    # READ ITEMS FROM A CUSTOMER'S SHOPCART
    #------------------------------------------------------------------
    @api.doc('get_shopcarts')
    @api.response(404, 'Shopcart not found')
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """ Read items from a customer's Shopcart """
        app.logger.info("Request an item from the Shopcart")
        shopcarts = Shopcart.find_by_shopcart_id(int(shopcart_id))
        if not shopcarts:
            app.logger.info("Returning 0 items")
            return [], status.HTTP_404_NOT_FOUND

        results = [items.serialize() for items in shopcarts]
        app.logger.info("Returning %d items", len(results))
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # CLEAR SHOPCART
    #------------------------------------------------------------------
    @api.doc('clear_shopcart')
    @api.response(204, 'Shopcart deleted')
    @api.marshal_with(shopcart_model)
    def delete(self, shopcart_id):
        """
        Delete All items in specific cart
        This endpoint will delete a Item based the id specified in the path
        """
        app.logger.info("Request to delete items in shopcart: %s ", shopcart_id)

        shopcart = Shopcart.find_by_shopcart_id(shopcart_id)

        results = [item.serialize() for item in shopcart]

        if results:
            for i in results:
                shopcart = Shopcart.find(shopcart_id, i['product_id'])
                shopcart.delete()
        return '', status.HTTP_204_NOCONTENT

    #------------------------------------------------------------------
    # CHECKOUT SHOPCART
    #------------------------------------------------------------------
    @api.doc('checkout_shopcart')
    @api.response(204, 'Shopcart checked out')
    @api.marshal_with(shopcart_model)
    def put(shopcart_id):
        """
        Checkout all item in shopcart

        This endpoint will update a item based the body that is posted
        """
        app.logger.info("Request to checkout all items in shopcart: %s", shopcart_id)
        shopcarts = Shopcart.find_by_shopcart_id(shopcart_id)

        if not shopcarts:
            raise NotFound("item with shopcart id '{}' was not found.".format(shopcart_id))

        else:
            results = [shopcart.serialize() for shopcart in shopcarts]
            print(results)
            for product in results:
                print(product)
                product_id = product['product_id']
                product['checkout'] = str(1)
                shopcart = Shopcart.find(shopcart_id, product_id)
                shopcart.deserialize(product)
                shopcart.update()
            shopcarts = Shopcart.find_by_shopcart_id(shopcart_id)
            results = [shopcart.serialize() for shopcart in shopcarts]
            return '', status.HTTP_204_NOCONTENT
######################################################################
#  PATH: /shopcarts/{shopcart_id}/items/{product_id}
######################################################################
@api.route('/shopcarts/<shopcart_id>/items/<product_id>')
@api.param('shopcart_id', 'The Shopcart identifier')
@api.param('product_id', 'The Product identifier')
class ShopcartItems(Resource):
    """
    ShopcartItems class
    Allows the operations on a customer's shopcart
    GET /shopcarts/{shopcart_id}/items/{product_id} - Retrieves items from a customer's shopcart
    DELETE /shopcarts/{shopcart_id}/items/{product_id} - Removes one item from a customer's shopcart
    PUT /shopcarts/{shopcart_id}/items/{product_id} - Removes one item from a customer's shopcart
    """

    #------------------------------------------------------------------
    # DELETE ITEM
    #------------------------------------------------------------------
    @api.doc('delete_shopcart_item')
    @api.response(204, 'Item deleted')
    def delete(self, shopcart_id, product_id):
        """
        Delete a Item

        This endpoint will delete a Item based the id specified in the path
        """
        app.logger.info("Request to delete item in shopcart: %s with id: %s", shopcart_id,product_id)

        shopcart = Shopcart.find(int(shopcart_id), int(product_id))

        if shopcart:
            shopcart.delete()
            app.logger.info('Shopcart with id [%s] and product id [%s] was deleted', shopcart_id, product_id)
        return '', status.HTTP_204_NO_CONTENT

    # ------------------------------------------------------------------
    # CHECKOUT AN EXISTING ITEM
    # ------------------------------------------------------------------
    @api.doc('checkout_item')
    @api.response(204, 'Item checked out')
    @api.marshal_with(shopcart_model)
    def put(shopcart_id, product_id):
        """
        Checkout an item

        This endpoint will update a item based the body that is posted
        """
        app.logger.info("Request to checkout item in shopcart: %s with id: %s", shopcart_id, product_id)

        shopcart = Shopcart.find(shopcart_id, product_id)

        if not shopcart:
            raise NotFound("item with shopcart id '{}' and item id '{}' was not found.".format(shopcart_id, product_id))

        else:
            shopcart_dict_database = shopcart.serialize()
            app.logger.info("changing checkout status from 0 to 1")
            shopcart_dict_database['checkout'] = str(1)
            shopcart.deserialize(shopcart_dict_database)
            shopcart.update()
            return '', status.HTTP_204_NOCONTENT

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
# CHECKOUT AN EXISTING ITEM
######################################################################
# @app.route("/shopcarts/<int:shopcart_id>/items/<int:product_id>/checkout", methods=["PUT"])
# def checkout_item(shopcart_id,product_id):
#     """
#     Checkout an item
#
#     This endpoint will update a item based the body that is posted
#     """
#     app.logger.info("Request to checkout item in shopcart: %s with id: %s",shopcart_id, product_id)
#
#     shopcart = Shopcart.find(shopcart_id, product_id)
#
#
#     if not shopcart:
#         raise NotFound("item with shopcart id '{}' and item id '{}' was not found.".format(shopcart_id,product_id))
#
#     else:
#         shopcart_dict_database = shopcart.serialize()
#         app.logger.info("changing checkout status from 0 to 1")
#         shopcart_dict_database['checkout'] = str(1)
#         shopcart.deserialize(shopcart_dict_database)
#         shopcart.update()
#         return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

######################################################################
# CHECKOUT ALL ITEM IN SHOPCART
######################################################################
# @app.route("/shopcarts/<int:shopcart_id>/checkout", methods=["PUT"])
# def checkout_shopcarts(shopcart_id):
#     """
#     Checkout all item in shopcart
#
#     This endpoint will update a item based the body that is posted
#     """
#     app.logger.info("Request to checkout all items in shopcart: %s",shopcart_id)
#     shopcarts = Shopcart.find_by_shopcart_id(shopcart_id)
#
#     if not shopcarts:
#         raise NotFound("item with shopcart id '{}' was not found.".format(shopcart_id))
#
#     else:
#         results = [shopcart.serialize() for shopcart in shopcarts]
#         print(results)
#         for product in results:
#             print(product)
#             product_id = product['product_id']
#             product['checkout'] = str(1)
#             shopcart = Shopcart.find(shopcart_id, product_id)
#             shopcart.deserialize(product)
#             shopcart.update()
#         shopcarts = Shopcart.find_by_shopcart_id(shopcart_id)
#         results = [shopcart.serialize() for shopcart in shopcarts]
#         return make_response(jsonify(results),status.HTTP_200_OK)


######################################################################
# CLEAR SHOPCART
######################################################################

# @app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
# def clear_shopcart(shopcart_id):
#     """
#     Delete All items in specific cart
#
#     This endpoint will delete a Item based the id specified in the path
#     """
#     app.logger.info("Request to delete items in shopcart: %s ", shopcart_id)
#
#     shopcart = Shopcart.find_by_shopcart_id(shopcart_id)
#
#     results = [item.serialize() for item in shopcart]
#
#     if results:
#         for i in results:
#             shopcart = Shopcart.find(shopcart_id, i['product_id'])
#             shopcart.delete()
#     return make_response(jsonify(""), status.HTTP_204_NO_CONTENT)




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
