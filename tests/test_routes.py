"""
Shopcarts API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models import Shopcart, DataValidationError, db # init_db is in routes for now
from service.routes import app, init_db
from datetime import datetime

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/shopcarts"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Shopcart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_item(self):
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
        resp = self.app.post(
            BASE_URL + "/{}".format(shopcart.shopcart_id), json=shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(
            resp.status_code, status.HTTP_201_CREATED, "Could not create Shopcart item"
        )
        return shopcart


    def test_index(self):
        """Test the Home Page"""
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Shopcarts REST API Service")

    def test_get_item(self):
        """Get a single Shopcart Item"""
        # get a shopcart item
        shopcart = self._create_item()
        print(shopcart)
        resp = self.app.get(
            "/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_id"], shopcart.product_id)

    def test_get_item_not_found(self):
        """Get a Shopcart item thats not found"""
        resp = self.app.get("/shopcarts/0/items/0")
        print(resp.status_code)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_item(self):
        """Create a new Shopcart item"""
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
        resp = self.app.post(
            BASE_URL + "/{}".format(shopcart.shopcart_id), json=shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        #print(time_freeze.strftime("%A, %d %m %y"))
        #print(time_freeze.ctime())
        # Check the data is correct
        new_item = resp.get_json()
        self.assertEqual(new_item["shopcart_id"], shopcart.shopcart_id, "shopcart_id do not match")
        self.assertEqual(new_item["product_id"], shopcart.product_id, "product_id do not match")
        self.assertEqual(new_item["quantity"], shopcart.quantity, "quantity does not match")
        self.assertEqual(new_item["price"], shopcart.price, "price does not match")
        #self.assertEqual(new_item["time_added"], shopcart.time_added, "time_added does not match")
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(new_item["shopcart_id"], shopcart.shopcart_id, "shopcart_id do not match")
        self.assertEqual(new_item["product_id"], shopcart.product_id, "product_id do not match")
        self.assertEqual(new_item["quantity"], shopcart.quantity, "quantity does not match")
        self.assertEqual(new_item["price"], shopcart.price, "price does not match")
        #self.assertEqual(new_item["time_added"], shopcart.time_added, "time_added does not match")