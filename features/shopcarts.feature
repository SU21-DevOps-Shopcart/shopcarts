Feature: The shopcart service back-end
    As a Shopper
    I need a RESTful shopcart service
    So that I can keep track of all my items

Background:
    Given the following shopcart_items
        | shopcart_id | product_id | price | quantity | 
        | 1234        | 1          | 0.99  | 1        | 
        | 1234        | 2          | 2.00  | 1        | 
        | 1234        | 3          | 2.00  | 1        | 
        | 5678        | 4          | 50.00 | 1        |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcarts RESTful Service" in the title
    And I should not see "404 Not Found"



Scenario: Create a Shopcart
    When I visit the "Home Page"
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "12"
    And I set the "Quantity" to "1"
    And I set the "Price" to "1.00"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "Clear" button
    Then the "Customer_ID" field should be empty
    And the "Product_ID" field should be empty
    And the "Quantity" field should be empty
    And the "Price" field should be empty
    When I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "12"
    And I press the "Retrieve" button
    Then I should see "1234" in the "Customer_ID" field
    And I should see "12" in the "Product_ID" field
    And I should see "1" in the "Quantity" field
    And I should see "1" in the "Price" field
    
Scenario: Checkout all items in one shopcart
    When I visit the "Home Page"
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1"
    And I press the "Retrieve" button
    Then I should see "0" in the "Checkout" field
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "2"
    And I press the "Retrieve" button
    Then I should see "0" in the "Checkout" field
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "3"
    And I press the "Retrieve" button
    Then I should see "0" in the "Checkout" field
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I press the "Checkout" button
    Then I should see the message "Item have been checkout!"
    When I press the "Clear" button 
    And I set the "Product_ID" to "1"
    And I set the "Customer_ID" to "1234"
    And I press the "Retrieve" button
    Then I should see "1" in the "Checkout" field
    When I change "Product_ID" to "2"
    And I press the "Retrieve" button
    Then I should see "1" in the "Checkout" field
    When I change "Product_ID" to "3"
    And I press the "Retrieve" button
    Then I should see "1" in the "Checkout" field

Scenario: List all Items in one shopcart
    When I visit the "Home Page"
    And I set the "Customer_ID" to "1234"
    And I press the "Search" button
    Then I should see the message "Success"
    Then I should see "1" in the results
    And I should see "2" in the results
    And I should see "3" in the results
    And I should not see "5678" in the results

Scenario: Delete a product in shopcart
    When I visit the "Home Page"
    And I set the "Customer_ID" to "1234"
    And I press the "Search" button
    Then I should see the message "Success"
    Then I should see "1" in the results
    And I should see "2" in the results
    And I should see "3" in the results
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1"
    When I press the "Delete" button
    Then I should see the message "Item has been Deleted!"
    When I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1" 
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Shopcart with shopcart_id '1234' and product_id '1' was not found."
    
Scenario: Update one item in a Shopcart
    When I visit the "Home Page"
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1234" in the results
    And I should see "1" in the results
    And I should see "1" in the results
    And I should see "0.99" in the results
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1"
    And I press the "Retrieve" button
    And I change "Quantity" to "2"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1"
    And I press the "Retrieve" button
    Then I should see "2" in the "Quantity" field

Scenario: Checkout an item in one shopcart
    When I visit the "Home Page"
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1"
    And I press the "Retrieve" button
    Then I should see "0" in the "Checkout" field
    When I press the "Checkout" button
    Then I should see the message "Item have been checkout!"
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "1"
    And I press the "Retrieve" button
    Then I should see "1" in the "Checkout" field





Scenario: Query shopcarts for a product_id
    When I visit the "Home Page"
    And I set the "Product_ID" to "4"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "5678" in the results
    And I should see "4" in the results
    And I should see "1" in the results
    And I should see "50" in the results


Scenario: Read shopcarts for a product_id and customer_id
    When I visit the "Home Page"
    And I set the "Product_ID" to "1"
    And I set the "Customer_ID" to "1234"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    Then I should see "1" in the "Quantity" field
    And I should see "0.99" in the "Price" field
    When I press the "Clear" button
    And I set the "Customer_ID" to "1234"
    And I set the "Product_ID" to "4"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Shopcart with shopcart_id '1234' and product_id '4' was not found."
    When I set the "Customer_ID" to "6789"
    And I set the "Product_ID" to "1"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Shopcart with shopcart_id '6789' and product_id '1' was not found."
    When I set the "Customer_ID" to "6789"
    And I set the "Product_ID" to "4"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Shopcart with shopcart_id '6789' and product_id '4' was not found."

