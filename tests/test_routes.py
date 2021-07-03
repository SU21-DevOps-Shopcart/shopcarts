"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from service.models import db
from service.routes import app, init_db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()


    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_items(self):
        """ Test list items """
        resp = self.app.get("/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_an_item(self):
        """ Test get a item """
        resp = self.app.get("/items/{}".format(1))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_an_item(self):
        """ Test create a item """
        resp = self.app.post("/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


    def test_update_an_item(self):
        """ Test update an existings items """
        resp = self.app.put("/items/{}".format(1))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


    def test_delete_an_item(self):
        """ Test list items """
        resp = self.app.delete("/items/{}".format(1))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    

