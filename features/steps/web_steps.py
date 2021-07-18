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
Web Steps

Steps file for web interactions with Silenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
import time
from behave import when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

ID_PREFIX = 'shopcarts_'

@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    #context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    time.sleep(0.05) 
    expect(context.driver.title).to_contain(message)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower() + "-input"
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)


@then('I should see "{quantity}" "{item}" in the cart')
def step_impl(context, quantity, item):
    element_id = ID_PREFIX + item.lower().replace(" ", "-") + "-quantity"
    element = context.driver.find_element_by_id(element_id)

    expect(element.text).to_equal("Quantity: " + quantity)

@then('I should not see "{item}" in the cart')
def step_impl(context, item):
    element_id = ID_PREFIX + item.lower().replace(" ", "-") + "-card"
    context.driver.implicitly_wait(0)
    elements = context.driver.find_elements(By.ID,element_id)
    expect(len(elements)).to_be(0)

##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = ID_PREFIX + button.lower().replace(" ","-") + '-btn'
    context.driver.find_element_by_id(button_id).click()
    time.sleep(0.1)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when('I press the "{location}" link')
def step_impl(context, location):
    location_id = location.lower()
    #elements = context.driver.find_elements_by_link_text(link).click()
    elements = context.driver.find_elements_by_xpath("//a[@href]")
    for element in elements:
        if (str(element.get_attribute("href")) == str(context.base_url + "/" + location_id)):
            element.click()
            break

@then('I should see "{name}" on the page')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, name),
            name
        )
    )
    expect(found).to_be(True)

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################

@then('I should see "{text_string}" in the "{element_name}" element')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id)

    expect(element.text).to_equal(text_string)

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower() + "-input"
    element = context.driver.find_element_by_id(element_id)

    expect(element.get_attribute('value')).to_equal(text_string)
