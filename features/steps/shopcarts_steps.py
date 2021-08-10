######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Shopcarts Steps

Steps file for shopcarts.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect
from datetime import datetime
import logging

@given('the following shopcart_items')
def step_impl(context):
    """ Delete all Shopcart items and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the shopcart items and delete them one by one
    context.resp = requests.get(context.base_url + '/api/shopcarts')
    # logging.info(context.resp)
    expect(context.resp.status_code).to_equal(200)
    for item in context.resp.json():

        ######################################################################
        # change the path from '/shopcarts' to '/api/shopcarts'
        ######################################################################

        context.resp = requests.delete(context.base_url + '/api/shopcarts/' + str(item["shopcart_id"]) + '/items/' + str(item["product_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new items
    for row in context.table:
        create_url = context.base_url + '/api/shopcarts/' + row["shopcart_id"]
        data = {
            'product_id': row['product_id'],
            'quantity': row['quantity'],
            'price': row['price'],
            'time_added': str(datetime.now().strftime("%a, %d %b %Y %H:%M:%S")),
            'checkout': 0
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

