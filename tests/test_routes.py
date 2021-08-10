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

import psycopg2
from service import status  # HTTP Status Codes
from service.models import DatabaseConnectionError, Shopcart, DataValidationError, db # init_db is in routes for now
from service.routes import app, init_db
from datetime import datetime

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/shopcarts"
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
        time_freeze = datetime.now()
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

    def _create_shopcart_with_item(self, shopcart_id, product_id):
        time_freeze = datetime.now()
        data = {
            "shopcart_id": shopcart_id,
            "product_id": product_id,
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
       self.assertIn(b"Shopcarts RESTful Service", resp.data)


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
        time_freeze = datetime.now()
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
        self.assertEqual(new_item[0]["shopcart_id"], shopcart.shopcart_id, "shopcart_id do not match")
        self.assertEqual(new_item[0]["product_id"], shopcart.product_id, "product_id do not match")
        self.assertEqual(new_item[0]["quantity"], shopcart.quantity, "quantity does not match")
        self.assertEqual(new_item[0]["price"], shopcart.price, "price does not match")
        self.assertEqual(new_item[0]["checkout"], shopcart.checkout, "checkout does not match")
        #self.assertEqual(new_item["time_added"], shopcart.time_added, "time_added does not match")


    def test_create_duplicate_item(self):
        """Test Create a Shopcart item that already exists"""
        time_freeze = datetime.now()
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
        item1 = self._create_shopcart_with_item(1234, 100)
        item2 = self._create_shopcart_with_item(1234, 101)
        item3 = self._create_shopcart_with_item(1234, 102)
        resp = self.app.get(BASE_URL + "?shopcart_id={}".format(item1.shopcart_id))
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
        resp = self.app.get(BASE_URL+"?shopcart_id={}&product_id={}".format(item4.shopcart_id, item4.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["shopcart_id"], item4.shopcart_id)
        self.assertEqual(items[0]["product_id"], item4.product_id)


    def test_list_one_shopcart_item(self):
        """ Test list one shopcart item """
        item1 = self._create_shopcart_with_item(1234, 100)
        item2 = self._create_shopcart_with_item(1234, 101)
        item3 = self._create_shopcart_with_item(1234, 102)
        resp = self.app.get(BASE_URL+"?shopcart_id={}&product_id={}".format(item1.shopcart_id, item1.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.get_json()
        self.assertEqual(item[0]["product_id"], item1.product_id)
        resp = self.app.get(BASE_URL+"?shopcart_id={}&product_id={}".format(item2.shopcart_id, item2.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.get_json()
        self.assertEqual(item[0]["product_id"], item2.product_id)
        resp = self.app.get(BASE_URL+"?shopcart_id={}&product_id={}".format(item3.shopcart_id, item3.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.get_json()
        self.assertEqual(item[0]["product_id"], item3.product_id)


    def test_list_all_shopcarts_with_item(self):
        """ Test list all shopcarts with an item """
        product_id = 100
        item1 = self._create_shopcart_with_item(1234, product_id)
        item2 = self._create_shopcart_with_item(1235, product_id)
        item3 = self._create_shopcart_with_item(1236, product_id)
        resp = self.app.get(BASE_URL+"?product-id={}".format(product_id))
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
        time_freeze = datetime.now()
        new_item['price'] = "3.9"
        new_item['time_added'] = time_freeze
        resp = self.app.put(
            BASE_URL + "/{}/items/{}".format(new_item['shopcart_id'],new_item['product_id']),
            json=new_item,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_item = resp.get_json()
        self.assertEqual(updated_item['price'], 3.9)
        self.assertEqual(updated_item['quantity'], 2)
        # self.assertEqual(updated_item['time_added'], time_freeze)

        resp = self.app.put(
            BASE_URL + "/{}/items/{}".format(new_item['shopcart_id'],new_item['product_id']),
            json=new_item,
            content_type="application/json",
        )
       # time_freeze = datetime.now()
        updated_item = resp.get_json()
        self.assertEqual(updated_item['price'], 3.9)
        self.assertEqual(updated_item['quantity'], 3)

        #update item does not exist
        time_freeze = datetime.now()
        data = {
            "shopcart_id": 124,
            "product_id": 5678,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
            "checkout" : 0
        }

        resp = self.app.put(
            BASE_URL + "/123456/items/123",
            json=data,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_an_item(self):
        """ Test delete a item """
        #add a item
        shopcart = self._create_shopcart_with_item(1234, 100)
        resp = self.app.get("/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        #delete the item
        resp = self.app.delete("/api/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # make sure item not in database
        resp = self.app.get("/shopcarts/{}/items/{}".format(shopcart.shopcart_id,shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_all_items(self):
        """Test delete all items"""
        item1 = self._create_shopcart_with_item(1234, 100)
        item2 = self._create_shopcart_with_item(1234, 101)
        item3 = self._create_shopcart_with_item(1234, 102)

        resp = self.app.get(BASE_URL+"?shopcart_id=1234")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 3)

        resp = self.app.delete("/api/shopcarts/1234")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.app.get(BASE_URL+"?shopcart_id=1234")

        self.assertEqual(resp.get_json(), [])

    def test_checkout_item(self):
        """Test checkout item"""

        #create item
        item = self._create_item()
        resp = self.app.get("/shopcarts/1234/items/5678")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        information = resp.get_json()
        self.assertEqual(information["checkout"], 0)
        
        #test change checkout status
        resp = self.app.put("/api/shopcarts/1234/items/5678/checkout")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        information = resp.get_json()
        self.assertEqual(information["checkout"], 1)

        #test change checkout item already checkout
        resp = self.app.put("/api/shopcarts/1234/items/5678/checkout",)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        #test change status of item does not exist
        time_freeze = datetime.now()
        data = {
            "shopcart_id": 124,
            "product_id": 5678,
            "quantity": 1,
            "price": 0.01,
            "time_added": time_freeze,
            "checkout" : 0
        }

        resp = self.app.put("/api/shopcarts/12345/items/100/checkout",)
        
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_read_items(self):
        """ Test read items from a shopcart """
        shopcart_id = 1234
        item1 = self._create_shopcart_with_item(shopcart_id, 100)
        item2 = self._create_shopcart_with_item(shopcart_id, 101)
        item3 = self._create_shopcart_with_item(shopcart_id, 102)
        resp = self.app.get(BASE_URL+"/{}".format(shopcart_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["product_id"], item1.product_id)
        self.assertEqual(items[1]["product_id"], item2.product_id)
        self.assertEqual(items[2]["product_id"], item3.product_id)
    

    def test_read_404(self):
        """ Test read not found """
        shopcart_id1 = 1231
        shopcart_id2 = 1232
        shopcart_id3 = 1233
        shopcart_id1234 = 1234
        product_id = 100
        item1 = self._create_shopcart_with_item(shopcart_id1, product_id)
        item2 = self._create_shopcart_with_item(shopcart_id2, product_id)
        item3 = self._create_shopcart_with_item(shopcart_id3, product_id)
        resp = self.app.get(BASE_URL+"/{}".format(shopcart_id1234))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_query_items_with_product_id(self):
        """ Test list shopcarts with product id """
        shopcart_id1 = 1231
        shopcart_id2 = 1232
        shopcart_id3 = 1233
        product_id = 100
        item1 = self._create_shopcart_with_item(shopcart_id1, product_id)
        item2 = self._create_shopcart_with_item(shopcart_id2, product_id)
        item3 = self._create_shopcart_with_item(shopcart_id3, product_id)
        resp = self.app.get(BASE_URL+"?product_id={}".format(product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()
        self.assertEqual(items[0]["product_id"], item1.product_id)
        self.assertEqual(items[1]["product_id"], item2.product_id)
        self.assertEqual(items[2]["product_id"], item3.product_id)


    # def test_bad_request(self):
    #     """ Test error handlers bad request """
    #     product_id = 1000
    #     resp = self.app.get("/shopcarts?product-id{}".format(product_id, product_id))
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    # def test_server_error(self):
    #     """ Test error handlers internal server error """
    #     resp = self.app.put("/shopcarts?")
    #     self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    def test_method_not_allowed(self):
            """ Test error handlers method not allowed """
            resp = self.app.put(BASE_URL+"?")
            self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_unsupported_media(self):
        """ Test error handlers unsupported media type """
        shopcart_id = 123
        resp = self.app.post(BASE_URL+"/{}".format(shopcart_id))
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_checkout_all_items(self):
        """ Test checkout all items"""
        #test with no shopcart 
        resp = self.app.put("/api/shopcarts/{}/checkout".format(1234))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        #test with checkout all items in shopcart
        item1 = self._create_shopcart_with_item(1234, 100)
        item2 = self._create_shopcart_with_item(1234, 101)
        item3 = self._create_shopcart_with_item(1234, 102)

        resp = self.app.put("/api/shopcarts/{}/checkout".format(1234))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.get_json()

        for shopcart in result:
            self.assertEqual(shopcart['checkout'], 1)

    # @patch('psycopg2.connect')
    # def test_connection_error(self, mock_connect):
    #     """ Test Disconnect """
    #     mock_con = mock_connect.return_value
    #     mock_cur = mock_con.cursor.return_value
    #     mock_cur.fetchcall.return_value = ConnectionError()
    #     self.assertRaises(DatabaseConnectionError, Shopcart.init_db, 'test')
