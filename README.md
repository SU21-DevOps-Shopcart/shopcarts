# Shopcart Rest API

Shopcart API.

## Overview

This project emulates Customer's shopcart. Actions like add items to shopcart, duplicate items' quantity, and etc can be achieved.

## Setup

You should clone this repository and the copy and paste the code into your project repo folder on your local computer.

```bash

## Contents

The project contains the following:

```text
.coveragerc         - settings file for code coverage options
.gitignore          - this will ignore vagrant and other metadata files
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/            - service python package
├── __init__.py     - package initializer
├── models.py       - module with business models
└── service.py      - module with service routes

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for busines models
└── test_service.py - test suite for service routes

Vagrantfile         - Vagrant file that installs Python 3 and PostgreSQL
```

Before running this project, make sure **virtualbox** , **vagrant**, and **postman** are installed.

In **shopcart** folder(make sure current path is /shopcart) type following instruction to have machine up, ssh into VM and go to **/vagrant** folder.

```bash
vagrant up

vagrant ssh

cd /vagrant
```

## Running

1. Running up project

   ```sh
   FLASK_APP=service:app flask run -h 0.0.0.0
   ```

2. open up postman
3. customer 1234 wants to add an item to shopcart,
   set following in **postman** and press **send**     button

   ```sh
   POST localhost:5000/shopcarts/1234

   {
       "product_id": "54",
       "quantity": "1",
       "price": "4.01",
       "time_added": "{{$isoTimesstamp}}"
   }
   ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    {
        "price": 4.01,
        "product_id": 54,
        "quantity": 1,
        "shopcart_id": 1234,
        "time_added": "Wed, 07 Jul 2021 07:10:26 GMT"
    }
    ```

4. Test if item is created, set following in **postman** and press **send** button

   ```sh
   GET localhost:5000/shopcarts/1234/items/54
   ```

   The server should response with following information, time_added will be different depend on when item is added

   ```sh
   {
        "price": 4.01,
        "product_id": 56,
        "quantity": 1,
        "shopcart_id": 1234,
        "time_added": "Wed, 07 Jul 2021 07:10:20 GMT"
    }
   ```

5. Add same item again using create item feature

   ```sh
   POST localhost:5000/shopcarts/1234

   {
       "product_id": "54",
       "quantity": "1",
       "price": "4.01",
       "time_added": "{{$isoTimesstamp}}"
   }
   ```

    The server should response with following information

    ```sh
    "item already exists"
    ```

6. Add different item using create item feature.

   ```sh
    POST localhost:5000/shopcarts/1234

    {
        "product_id": "55",
        "quantity": "1",
        "price": "4.01",
        "time_added": "{{$isoTimestamp}}"
    }
   ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    {
        "price": 4.01,
        "product_id": 55,
        "quantity": 1,
        "shopcart_id": 1234,
        "time_added": "Wed, 07 Jul 2021 08:38:55 GMT"
    }
    ```

7. List all items in shopcarts

   ```sh
   GET localhost:5000/shopcarts?
   ```

   The server should response with following information, time_added will be different depend on when item is added

   ```sh
   [
        {
            "price": 4.01,
            "product_id": 54,
            "quantity": 1,
            "shopcart_id": 1234,
            "time_added": "Wed, 07 Jul 2021 08:35:54 GMT"
        },
        {
            "price": 4.01,
            "product_id": 55,
            "quantity": 1,
            "shopcart_id": 1234,
            "time_added": "Wed, 07 Jul 2021 08:38:55 GMT"
        }
    ]
   ```

8. Add a customer's item

   ```sh
   POST localhost:5000/shopcarts/12345

   {
        "product_id": "55",
        "quantity": "1",
        "price": "4.01",
        "time_added": "{{$isoTimestamp}}"
    }
   ```

9.  Customer 1234 want to see his or her shopcart

    ```sh
    GET localhost:5000/shopcarts?shopcart-id=1234
    ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    [
        {
            "price": 4.01,
            "product_id": 54,
            "quantity": 1,
            "shopcart_id": 1234,
            "time_added": "Wed, 07 Jul 2021 08:35:54 GMT"
        },
        {
            "price": 4.01,
            "product_id": 55,
            "quantity": 1,
            "shopcart_id": 1234,
            "time_added": "Wed, 07 Jul 2021 08:38:55 GMT"
        }
    ]
    ```

10. customer 1234 want to add one more item 54 to his or her shopcart, but the price of item 54 changed because of Black Friday!

    ```sh
    PUT localhost:5000/shopcarts/1234/items/54

    {
        "product_id": "54",
        "quantity": "1",
        "price": "0.001",
        "time_added": "{{$isoTimestamp}}"
    }
    ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    {
        "price": 0.001,
        "product_id": 54,
        "quantity": 2,
        "shopcart_id": 1234,
        "time_added": "Wed, 07 Jul 2021 08:56:01 GMT"
    }
    ```

11. customer 1234 want to see detail about item 54 in his or her shopcart

    ```sh
    GET localhost:5000/shopcarts/1234/items/54
    ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    {
        "price": 0.001,
        "product_id": 54,
        "quantity": 2,
        "shopcart_id": 1234,
        "time_added": "Wed, 07 Jul 2021 08:56:01 GMT"
    }
    ```

12. customer 1234 remove item 55 out of his or her shopcart

    ```sh
    DELETE localhost:5000/shopcarts/1234/items/55
    ```

13. cutomer 1234 add item 57 to his or her shopcart

    ```sh
    POST localhost:5000/shopcarts/1234
    ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    {
        "price": 99999.0,
        "product_id": 57,
        "quantity": 1,
        "shopcart_id": 1234,
        "time_added": "Wed, 07 Jul 2021 09:03:33 GMT"
    }
    ```

14. Now all items in customer 1234's shopcart are followings

    ```sh
    GET localhost:5000/shopcarts?shopcart-id=1234
    ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    [
        {
            "price": 0.001,
            "product_id": 54,
            "quantity": 2,
            "shopcart_id": 1234,
            "time_added": "Wed, 07 Jul 2021 08:56:01 GMT"
        },
        {
            "price": 99999.0,
            "product_id": 57,
            "quantity": 1,
            "shopcart_id": 1234,
            "time_added": "Wed, 07 Jul 2021 09:03:33 GMT"
        }
    ]
    ```

15. customer 1234 accidently press **clear shopcart** button

    ```sh
    PUT localhost:5000/shopcarts/1234
    ```

16. when he or she checks shopcart again

    ```sh
    GET localhost:5000/shopcarts?shopcart-id=1234
    ```

    The server should response with following information, time_added will be different depend on when item is added

    ```sh
    []
    ```

## Shut down machine

1. press `ctr` + `c` and input `exit` to get out of virtual machine
2. input `vagrant halt` to shut down virtual machine


# nyu-travis-ci

[![Build Status](https://travis-ci.com/SU21-DevOps-Shopcart/shopcarts.svg?branch=main)](https://travis-ci.com/SU21-DevOps-Shopcart/shopcarts)
[![Codecov](https://img.shields.io/codecov/c/github/nyu-devops/lab-travis-ci.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


This repository is part of the NYU class **CSCI-GA.2810-001: DevOps and Agile Methodologies** taught by John Rofrano, Adjunct Instructor, NYU Curant Institute, Graduate Division, Computer Science.
