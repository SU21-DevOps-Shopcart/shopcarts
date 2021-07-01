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
    
    def test_create_an_item(self):
        """Create a item and assert that it exists"""
        #shopcart = Shopcart(name="fido", category="dog", available=True, gender=Gender.Male)
        time_freeze = datetime.utcnow()
        shopcart = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.shopcart_id, 1234)
        self.assertEqual(shopcart.product_id, 5678)
        self.assertEqual(shopcart.quantity, 1)
        self.assertEqual(shopcart.price, 5.99)
        self.assertEqual(shopcart.time_added, time_freeze)
    
    def test_create_an_item_in_a_shopcart(self):
        """Create an item in the shopcart database and assert it exists"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        time_freeze = datetime.utcnow()
        shopcart = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        self.assertTrue(shopcart != None)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(shopcart.shopcart_id, 1234)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        self.assertEqual(shopcarts[0].shopcart_id, 1234)
        self.assertEqual(shopcarts[0].product_id, 5678)
        self.assertEqual(shopcarts[0].quantity, 1)
        self.assertEqual(shopcarts[0].price, 5.99)
        self.assertEqual(shopcarts[0].time_added, time_freeze)

    def test_update_to_an_item_in_a_shopcart(self):
        """Create an item in the shopcart database and update the quantity"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        time_freeze = datetime.utcnow()
        shopcart = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        self.assertTrue(shopcart != None)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts[0].quantity, 1)
        shopcart.quantity = 2
        shopcart.update()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        self.assertEqual(shopcarts[0].shopcart_id, 1234)
        self.assertEqual(shopcarts[0].product_id, 5678)
        self.assertEqual(shopcarts[0].quantity, 2)
        self.assertEqual(shopcarts[0].price, 5.99)
        self.assertEqual(shopcarts[0].time_added, time_freeze)

    def test_delete_an_item(self):
        """Delete a Shopcart item"""
        time_freeze = datetime.utcnow()
        shopcart = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        shopcart.create()
        self.assertEqual(len(Shopcart.all()), 1)
        # delete the item and make sure it isn't in the database
        shopcart.delete()
        self.assertEqual(len(Shopcart.all()), 0)

    def test_serialize_a_shopcart_item(self):
        """Test serialization of a Shopcart item"""
        time_freeze = datetime.utcnow()
        shopcart = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        data = shopcart.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("shopcart_id", data)
        self.assertEqual(data["shopcart_id"], shopcart.shopcart_id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], shopcart.product_id)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], shopcart.quantity)
        self.assertIn("price", data)
        self.assertEqual(data["price"], shopcart.price)
        self.assertIn("time_added", data)
        self.assertEqual(data["time_added"], shopcart.time_added)

    def test_deserialize_a_Shopcart_item(self):
        """Test deserialization of a Shopcart item"""
        time_freeze = datetime.utcnow()
        data = {
            "shopcart_id": 1234,
            "product_id": 5678,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
        }
        shopcart = Shopcart()
        shopcart.deserialize(data)
        self.assertNotEqual(shopcart, None)
        self.assertEqual(shopcart.shopcart_id, 1234)
        self.assertEqual(shopcart.product_id, 5678)
        self.assertEqual(shopcart.quantity, 1)
        self.assertEqual(shopcart.price, 0.01)
        self.assertEqual(shopcart.time_added, time_freeze)

    def test_deserialize_missing_data(self):
        """Test deserialization of a Shopcart item with missing data"""
        data = {"shopcart_id": 1, "product_id": 999, "price": 0.05}
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)
        
    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_find_a_Shopcart_item(self):
        """Find a Shopcart item by shopcart_id and product_id"""
        # make Shopcart item #1
        time_freeze = datetime.utcnow()
        shopcart_1 = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        shopcart_1.create()
        # make Shopcart item #2
        time_freeze = datetime.utcnow()
        shopcart_2 = Shopcart(shopcart_id=1235, product_id=6678, quantity=1, price=6.00, time_added=time_freeze)
        shopcart_2.create()
        # make Shopcart item #3
        time_freeze = datetime.utcnow()
        shopcart_3 = Shopcart(shopcart_id=1236, product_id=7678, quantity=1, price=9.99, time_added=time_freeze)
        shopcart_3.create()

        # make sure they got saved
        self.assertEqual(len(Shopcart.all()), 3)
        # find the 2nd pet in the list
        shopcart = Shopcart.find(shopcart_2.shopcart_id, shopcart_2.product_id)
        self.assertIsNot(shopcart, None)
        self.assertEqual(shopcart.shopcart_id, shopcart_2.shopcart_id)
        self.assertEqual(shopcart.product_id, shopcart_2.product_id)
        self.assertEqual(shopcart.quantity, shopcart_2.quantity)
        self.assertEqual(shopcart.price, shopcart_2.price)
        self.assertEqual(shopcart.time_added, shopcart_2.time_added)

    def test_find_or_404_found(self):
        """Find or return 404 found"""
        # make Shopcart item #1
        time_freeze = datetime.utcnow()
        shopcart_1 = Shopcart(shopcart_id=1234, product_id=5678, quantity=1, price=5.99, time_added=time_freeze)
        shopcart_1.create()
        # make Shopcart item #2
        time_freeze = datetime.utcnow()
        shopcart_2 = Shopcart(shopcart_id=1235, product_id=6678, quantity=1, price=6.00, time_added=time_freeze)
        shopcart_2.create()
        # make Shopcart item #3
        time_freeze = datetime.utcnow()
        shopcart_3 = Shopcart(shopcart_id=1236, product_id=7678, quantity=1, price=9.99, time_added=time_freeze)
        shopcart_3.create()

        # make sure they got saved
        self.assertEqual(len(Shopcart.all()), 3)
        # find the 2nd pet in the list
        shopcart = Shopcart.find_or_404(shopcart_2.shopcart_id, shopcart_2.product_id)
        self.assertIsNot(shopcart, None)
        self.assertEqual(shopcart.shopcart_id, shopcart_2.shopcart_id)
        self.assertEqual(shopcart.product_id, shopcart_2.product_id)
        self.assertEqual(shopcart.quantity, shopcart_2.quantity)
        self.assertEqual(shopcart.price, shopcart_2.price)
        self.assertEqual(shopcart.time_added, shopcart_2.time_added)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, Shopcart.find_or_404, 0, 0)

