"""
Test cases for Shopcart Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_models.py:TestShopcartsModel

"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Shopcart, DataValidationError, db
from service import app
from datetime import datetime

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Shopcarts   M O D E L   T E S T   C A S E S
######################################################################

class TestShopcartModel(unittest.TestCase):
    """ Test Cases for Shopcart Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Shopcart.init_db(app)
        #pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()
        #pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables
        #pass

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()
        #pass

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_XXXX(self):
        """ Test something """
        self.assertTrue(True)
    
    def test_create_an_item_in_the_shopcart(self):
        """Create a item and assert that it exists"""
        #shopcart = Shopcart(name="fido", category="dog", available=True, gender=Gender.Male)
        time_freeze = datetime.utcnow
        shopcart = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.shopcart_id, 1234)
        self.assertEqual(shopcart.product_id, 5678)
        self.assertEqual(shopcart.quantity, 1)
        self.assertEqual(shopcart.price, 5.99)
        self.assertEqual(shopcart.time_added, time_freeze)
        #self.assertTrue(True)
