"""
Models for Shopcarts Service

All of the models are stored in this module


Models
------
Shopcart - A Shopcart used in the Store

Attributes:
-----------
shopcart_id (integer) - cart id is the customer id
product_id (integer) - item id in a customer's cart 
quantity (integer) - number of like items in the cart
price (decimal) - price at time item is placed in cart
time_added (timestamp) - latest unix time item was added to the cart

"""
import os
import json
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger("flask.app")

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
HOST = os.environ.get('HOST', 'localhost')
USERNAME = os.environ.get('USERNAME', 'admin')
PASSWORD = os.environ.get('PASSWORD', 'pass')

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

def init_db(app):
    """Initialies the SQLAlchemy app"""
    Shopcart.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Shopcart(db.Model):
    """
    Class that represents a Shopcart
    """

    app = None

    # Table Schema
    shopcart_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    quantity = db.Column(db.Integer, nullable=False,default=0)
    price = db.Column(db.Float, nullable=False, default=0.00)
    time_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "Shopcart shopcart_id=[%d]>" % (self.shopcart_id)

    def create(self):
        """
        Creates a Shopcart item in the database
        """
        logger.info("Creating shopcart item %d %d", self.shopcart_id, self.product_id)
        # self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Shopcart item in the database
        """
        logger.info("Saving %d %d", self.shopcart_id, self.product_id)
        db.session.commit()

    def delete(self):
        """ Removes a Shopcart item from the database """
        logger.info("Deleting %d %d", self.shopcart_id, self.product_id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Shopcart item into a dictionary """
        return {
            "shopcart_id": self.shopcart_id, 
            "product_id": self.product_id, 
            "quantity": self.quantity, 
            "price": self.price,
            "time_added": self.time_added
            }

    def deserialize(self, data):
        """
        Deserializes a Shopcart item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
            self.time_added = data["time_added"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart item: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart item: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Shopcarts in the database """
        logger.info("Processing all Shopcarts")
        return cls.query.all()

    @classmethod
    def find(cls, shopcart_id, product_id):
        """ Finds a Shopcart item by it's shopcart_id and product_id """
        logger.info("Processing lookup for shopcart_id %d and product_id %d ...", shopcart_id, product_id)
        return cls.query.get((shopcart_id, product_id))

    @classmethod
    def find_or_404(cls, shopcart_id, product_id):
        """ Find a Shopcart item by it's shopcart_id and product_id """
        logger.info("Processing lookup or 404 for shopcart_id %d and product_id %d ...", shopcart_id, product_id)
        return cls.query.get_or_404((shopcart_id, product_id))

    @classmethod
    def find_by_shopcart_id(cls, shopcart_id):
        """ 
            Returns all Shopcart items with the given shopcart_id 
            Args:
                shopcart_id (int): the shopcart id of the Shopcart you want to match
        """
        logger.info("Processing lookup for shopcart_id %d ...", shopcart_id)
        return cls.query.filter(cls.shopcart_id == shopcart_id).all()

    @classmethod
    def find_by_product_id(cls, product_id):
        """ 
            Returns all shopcarts that contain item by product_id 
            Args:
                product_id (int): the product id of the item you want to match
        """
        logger.info("Processing lookup for product_id %d ...", product_id)
        return cls.query.filter(cls.product_id == product_id)

    # @classmethod
    # def find_by_name(cls, name):
    #     """Returns all YourResourceModels with the given name

    #     Args:
    #         name (string): the name of the YourResourceModels you want to match
    #     """
    #     logger.info("Processing name query for %s ...", name)
    #     return cls.query.filter(cls.name == name)

############################################################
#  P O S T G R E S Q L   D A T A B A S E   C O N N E C T I O N
############################################################

    @staticmethod
    def init_db(dbname='csrkuvtx'):
        """
        Initialized Postgresql database connection
        """
        opts = {}
        vcap_services = {}
        # Try and get VCAP from the environment or a file if developing
        if 'VCAP_SERVICES' in os.environ:
            Shopcart.logger.info('Running in Bluemix mode.')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
        # # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        # elif 'BINDING_CLOUDANT' in os.environ:
        #     Shopcart.logger.info('Found Kubernetes Bindings')
        #     creds = json.loads(os.environ['BINDING_CLOUDANT'])
        #     vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}
        else:
            Shopcart.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            creds = {
                "url": "postgres://csrkuvtx:UtfLipE9HDx5z9O9UHSZUNSL82kRglWt@kashin.db.elephantsql.com/csrkuvtx"
            }
            vcap_services = {"user-provided": [{"credentials": creds}]}

        # Look for User-provided-service in VCAP_SERVICES
        for service in vcap_services:
            if service.startswith('user-provided'):
                user_provided_service = vcap_services[service][0]
                # opts['username'] = cloudant_service['credentials']['username']
                # opts['password'] = cloudant_service['credentials']['password']
                # opts['host'] = cloudant_service['credentials']['host']
                # opts['port'] = cloudant_service['credentials']['port']
                opts['url'] = user_provided_service['credentials']['url']

        if any(k not in opts for k in ('url')):
            Shopcart.logger.info('Error - Failed to retrieve options. ' \
                             'Check that app is bound to a Cloudant service.')
            exit(-1)

            Shopcart.logger.info('ElephantSQL Endpoint: %s', opts['url'])
        # try:
        #     if ADMIN_PARTY:
        #         Pet.logger.info('Running in Admin Party Mode...')
        #     Pet.client = Cloudant(opts['username'],
        #                           opts['password'],
        #                           url=opts['url'],
        #                           connect=True,
        #                           auto_renew=True,
        #                           admin_party=ADMIN_PARTY,
        #                           adapter=Replay429Adapter(retries=10, initialBackoff=0.01)
        #                          )
        # except ConnectionError:
        #     raise AssertionError('Cloudant service could not be reached')

        try:
            if ADMIN_PARTY:
                Shopcart.logger.info('Running in Admin Party Mode...')
            Shopcart.conn = psycopg2.connect(database=dbname,
                                host=HOST,
                                port='5432',
                                user=USERNAME,
                                password=PASSWORD)
            Shopcart.conn.autocommit = True

        except ConnectionError:
            raise AssertionError('Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Shopcart.conn = psycopg2.connect(database=dbname,
                                         host=HOST,
                                         port='5432',
                                         user=USERNAME,
                                         password=PASSWORD)
            Shopcart.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except KeyError:
            cur = Shopcart.conn.cursor()
            cur.execute(query = ("CREATE DATABASE {}").format(dbname))

        if not Shopcart.database.exists():
            raise AssertionError('Database [{}] could not be obtained'.format(dbname))