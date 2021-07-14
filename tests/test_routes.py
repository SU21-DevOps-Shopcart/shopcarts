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


    def _create_shopcart_with_item(self, shopcart_id, product_id):
        time_freeze = datetime.utcnow()
        data = {
            "shopcart_id": shopcart_id,
            "product_id": product_id,
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
        """Test Get a single Shopcart Item"""
        # get a shopcart item
        shopcart = self._create_shopcart_with_item(1234, 100)
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


    def test_create_duplicate_item(self):
        """Test Create a Shopcart item that already exists"""
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
        # add the item again for an error
        resp = self.app.post(
            BASE_URL + "/{}".format(shopcart.shopcart_id), json=shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)


    def test_list_items(self):
        """ Test list items """
        item1 = self._create_shopcart_with_item(1234, 100)
        item2 = self._create_shopcart_with_item(1234, 101)
        item3 = self._create_shopcart_with_item(1234, 102)
        resp = self.app.get("/shopcarts?shopcart-id={}".format(item1.shopcart_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["shopcart_id"], item1.shopcart_id)
        self.assertEqual(items[1]["shopcart_id"], item2.shopcart_id)
        self.assertEqual(items[2]["shopcart_id"], item3.shopcart_id)
        self.assertEqual(items[0]["product_id"], item1.product_id)
        self.assertEqual(items[1]["product_id"], item2.product_id)
        self.assertEqual(items[2]["product_id"], item3.product_id)
        """ Test list items shopcart_id and product_id"""
        item4 = self._create_shopcart_with_item(1234, 103)
        resp = self.app.get("/shopcarts?shopcart-id={}&product-id={}".format(item4.shopcart_id, item4.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["shopcart_id"], item4.shopcart_id)
        self.assertEqual(items[0]["product_id"], item4.product_id)


    def test_list_one_shopcart_item(self):
        """ Test list one shopcart item """
        item1 = self._create_shopcart_with_item(1234, 100)
        item2 = self._create_shopcart_with_item(1234, 101)
        item3 = self._create_shopcart_with_item(1234, 102)
        resp = self.app.get("/shopcarts?shopcart-id={}&product-id={}".format(item1.shopcart_id, item1.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.get_json()
        self.assertEqual(item[0]["product_id"], item1.product_id)
        resp = self.app.get("/shopcarts?shopcart-id={}&product-id={}".format(item2.shopcart_id, item2.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.get_json()
        self.assertEqual(item[0]["product_id"], item2.product_id)
        resp = self.app.get("/shopcarts?shopcart-id={}&product-id={}".format(item3.shopcart_id, item3.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.get_json()
        self.assertEqual(item[0]["product_id"], item3.product_id)


    def test_list_all_shopcarts_with_item(self):
        """ Test list all shopcarts with an item """
        product_id = 100
        item1 = self._create_shopcart_with_item(1234, product_id)
        item2 = self._create_shopcart_with_item(1235, product_id)
        item3 = self._create_shopcart_with_item(1236, product_id)
        resp = self.app.get("/shopcarts?product-id={}".format(product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["shopcart_id"], item1.shopcart_id)
        self.assertEqual(items[1]["shopcart_id"], item2.shopcart_id)
        self.assertEqual(items[2]["shopcart_id"], item3.shopcart_id)


    def test_update_an_item(self):
        """ Test update an existings items """
        #create a item
        shopcart = self._create_shopcart_with_item(1234, 100)
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
      #  self.assertEqual(updated_item['time_added'], time_freeze)


    def test_delete_an_item(self):
        """ Test delete a item """
        #add a item
        shopcart = self._create_shopcart_with_item(1234, 100)
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
        item1 = self._create_shopcart_with_item(1234, 100)
        item2 = self._create_shopcart_with_item(1234, 101)
        item3 = self._create_shopcart_with_item(1234, 102)

        resp = self.app.get("/shopcarts?shopcart_id=123")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 3)

        resp = self.app.put("/shopcarts/1234")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.app.get("/shopcarts?shopcart_id=123")

        self.assertEqual(resp.get_json(), "no items found")


    def test_read_items(self):
        """ Test read items from a shopcart """
        shopcart_id = 1234
        item1 = self._create_shopcart_with_item(shopcart_id, 100)
        item2 = self._create_shopcart_with_item(shopcart_id, 101)
        item3 = self._create_shopcart_with_item(shopcart_id, 102)
        resp = self.app.get("/shopcarts/{}".format(shopcart_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["product_id"], item1.product_id)
        self.assertEqual(items[1]["product_id"], item2.product_id)
        self.assertEqual(items[2]["product_id"], item3.product_id)
    

