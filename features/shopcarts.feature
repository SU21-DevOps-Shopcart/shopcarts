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
