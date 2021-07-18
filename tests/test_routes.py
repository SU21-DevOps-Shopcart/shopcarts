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
            "checkout": 0
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

    def _create_item_with_id(self, id):
        time_freeze = datetime.utcnow()
        data = {
            "shopcart_id": 1234,
            "product_id": id,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
            "checkout": 0
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
        """Test Get a single Shopcart Item"""
        # get a shopcart item
        shopcart = self._create_item()
        resp = self.app.get(
            "/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_id"], shopcart.product_id)

    def test_get_item_not_found(self):
        """Test Get a Shopcart item thats not found"""
        resp = self.app.get("/shopcarts/0/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_item(self):
        """Test Create a new Shopcart item"""
        time_freeze = datetime.utcnow()
        data = {
            "shopcart_id": 1234,
            "product_id": 5678,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
            "checkout": 0
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
        # Check the data is correct
        new_item = resp.get_json()
        self.assertEqual(new_item["shopcart_id"], shopcart.shopcart_id, "shopcart_id do not match")
        self.assertEqual(new_item["product_id"], shopcart.product_id, "product_id do not match")
        self.assertEqual(new_item["quantity"], shopcart.quantity, "quantity does not match")
        self.assertEqual(new_item["price"], shopcart.price, "price does not match")
        self.assertEqual(new_item["checkout"], shopcart.checkout, "checkout does not match")
        #self.assertEqual(new_item["time_added"], shopcart.time_added, "time_added does not match")
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(new_item["shopcart_id"], shopcart.shopcart_id, "shopcart_id do not match")
        self.assertEqual(new_item["product_id"], shopcart.product_id, "product_id do not match")
        self.assertEqual(new_item["quantity"], shopcart.quantity, "quantity does not match")
        self.assertEqual(new_item["price"], shopcart.price, "price does not match")
        self.assertEqual(new_item["checkout"], shopcart.checkout, "checkout does not match")
        #self.assertEqual(new_item["time_added"], shopcart.time_added, "time_added does not match")

    def test_create_duplicate_item(self):
        """Test Create a Shopcart item that already exists"""
        time_freeze = datetime.utcnow()
        data = {
            "shopcart_id": 1234,
            "product_id": 5678,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
            "checkout": 0
        }
        shopcart = Shopcart()
        shopcart.deserialize(data)
        resp = self.app.post(
            BASE_URL + "/{}".format(shopcart.shopcart_id), json=shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # add the item again for an error
        resp = self.app.post(
            BASE_URL + "/{}".format(shopcart.shopcart_id), json=shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_list_items(self):
        """ Test list items """
        item1 = self._create_item_with_id(100)
        item2 = self._create_item_with_id(101)
        item3 = self._create_item_with_id(102)
        resp = self.app.get("/shopcarts?shopcart_id=123")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["shopcart_id"], 1234)
        self.assertEqual(items[1]["shopcart_id"], 1234)
        self.assertEqual(items[2]["shopcart_id"], 1234)
        self.assertEqual(items[0]["product_id"], 100)
        self.assertEqual(items[1]["product_id"], 101)
        self.assertEqual(items[2]["product_id"], 102)

    def test_update_an_item(self):
        """ Test update an existings items """
        #create a item
        shopcart = self._create_item()
        resp = self.app.get("/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        #update item
        new_item = resp.get_json()
        logging.debug(new_item)
        time_freeze = datetime.utcnow()
        new_item['price'] = "3.9"
        new_item['time_added'] = time_freeze
        resp = self.app.put(
            "/shopcarts/{}/items/{}".format(new_item['shopcart_id'],new_item['product_id']),
            json=new_item,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_item = resp.get_json()
        self.assertEqual(updated_item['price'], 3.9)
        self.assertEqual(updated_item['quantity'], 2)
     #   self.assertEqual(updated_item['time_added'], time_freeze)

        resp = self.app.put(
            "/shopcarts/{}/items/{}".format(new_item['shopcart_id'],new_item['product_id']),
            json=new_item,
            content_type="application/json",
        )
       # time_freeze = datetime.utcnow()
        updated_item = resp.get_json()
        self.assertEqual(updated_item['price'], 3.9)
        self.assertEqual(updated_item['quantity'], 3)

        #update item does not exist
        time_freeze = datetime.utcnow()
        data = {
            "shopcart_id": 124,
            "product_id": 5678,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
            "checkout" : 0
        }

        resp = self.app.put(
            "/shopcarts/123456/items/123",
            json=data,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)








    def test_delete_an_item(self):
        """ Test delete a item """
        #add a item
        shopcart = self._create_item()
        resp = self.app.get("/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        #delete the item
        resp = self.app.delete("/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # make sure item not in database
        resp = self.app.get("/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_all_items(self):
        """Test delete all items"""
        item1 = self._create_item_with_id(100)
        item2 = self._create_item_with_id(101)
        item3 = self._create_item_with_id(102)

        resp = self.app.get("/shopcarts?shopcart_id=123")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 3)

        resp = self.app.put("/shopcarts/1234")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.app.get("/shopcarts?shopcart_id=123")

        self.assertEqual(resp.get_json(), "no items found")

    def test_checkout_item(self):
        """Test checkout item"""

        #create item
        item = self._create_item_with_id(100)
        resp = self.app.get("/shopcarts/1234/items/100")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        information = resp.get_json()
        self.assertEqual(information["checkout"], 0)
        
        #test change checkout status
        resp = self.app.put("/shopcarts/1234/items/100/checkout",
                            json=information,
                            content_type="application/json",
            )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        information = resp.get_json()
        self.assertEqual(information["checkout"], 1)

        #test change checkout item already checkout
        resp = self.app.put("/shopcarts/1234/items/100/checkout",
                            json=information,
                            content_type="application/json",
            )

        information = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

        #test change status of item does not exist
        time_freeze = datetime.utcnow()
        data = {
            "shopcart_id": 124,
            "product_id": 5678,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
            "checkout" : 0
        }

        resp = self.app.put("/shopcarts/12345/items/100/checkout",
                            json=data,
                            content_type="application/json",
            )
        
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


        




        


    

