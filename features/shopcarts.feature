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
    Then I should see "Avoman" in the title
    And I should not see "404 Not Found"

Scenario: Create a Shopcart item
    When I visit the "Home Page"
    Then I should see "Avoman" in the title
    And I should see "Cart (0)" in the "cart-link" element
    When I press the "Shop" link
    Then I should see "Shop | Avoman" in the title
    And I should see "A regular avocado" on the page
    When I press the "regular-avocado" link
    Then I should see "A regular avocado | Avoman" in the title
    And I should see "1" in the "quantity" element
    When I press the "Increment" button
    Then I should see "2" in the "quantity" element
    When I press the "Decrement" button
    Then I should see "1" in the "quantity" element
    When I press the "Decrement" button
    Then I should see "1" in the "quantity" element
    When I press the "Add" button
    Then I should see "Cart (1)" in the "cart-link" element

Scenario: View shopcart
    When I visit the "Home Page"
    And I press the "Cart" link
    Then I should see "Cart | Avoman" in the title
    And I should see "12345" in the "user_id" element
    When I press the "Edit" button
    Then I should see "12345" in the "id" field
    When I set the "id" to "1234"
    Then I should see "1234" in the "id" field
    When I press the "Save" button
    Then I should see "1234" in the "user_id" element
    And I should see "Cart (3)" in the "cart-link" element
    And I should see "1" "A regular avocado" in the cart
    And I should see "1" "A purple avocado" in the cart
    And I should see "1" "Sliced avocado" in the cart

Scenario: Update shopcart
    When I visit the "Home Page"
    And I press the "Cart" link
    Then I should see "Cart | Avoman" in the title
    When I press the "Edit" button
    And I set the "id" to "1234"
    Then I should see "1234" in the "id" field
    When I press the "Save" button
    Then I should see "1234" in the "user_id" element
    And I should see "Cart (3)" in the "cart-link" element
    And I should see "1" "A regular avocado" in the cart
    When I press the "Update a regular avocado" button
    Then I should see "2" "A regular avocado" in the cart
    When I press the "Remove a regular avocado" button
    Then I should not see "A regular avocado" in the cart


Scenario: Checkout shopcart
    When I visit the "Home Page"
    And I press the "Cart" link
    Then I should see "Cart | Avoman" in the title
    When I press the "Edit" button
    And I set the "id" to "1234"
    Then I should see "1234" in the "id" field
    When I press the "Save" button
    Then I should see "1234" in the "user_id" element
    And I should see "Cart (3)" in the "cart-link" element
    When I press the "Checkout" button
    Then I should see "Thank you | Avoman" in the title
    And I should see "Cart (0)" in the "cart-link" element
    