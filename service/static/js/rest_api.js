$(function () {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

  // Updates the form with data from the response
  function update_form_data(res) {
    
    $("#shopcart_customer_id").val(res.shopcart_id);
    $("#shopcart_product_id").val(res.product_id);
    $("#shopcart_quantity").val(res.quantity);
    $("#shopcart_price").val(res.price);
    if (res.checkout == 1){
      $("#shopcart_checkout").val(1);
    } else {
      $("#shopcart_checkout").val(0);
    }
  }

  /// Clears all form fields
  function clear_form_data() {
    $("#shopcart_customer_id").val("");
    $("#shopcart_product_id").val("");
    $("#shopcart_quantity").val("");
    $("#shopcart_price").val("");
    $("#shopcart_checkout").val("");
  }

  // Updates the flash message area
  function flash_message(message) {
    $("#flash_message").empty();
    $("#flash_message").append(message);
  }

  // ****************************************
  // Create a Shopcart item
  // ****************************************

  $("#create-btn").click(function () {
    var shopcart_id = $("#shopcart_customer_id").val();
    var product_id = $("#shopcart_product_id").val();
    var quantity = $("#shopcart_quantity").val();
    var price = $("#shopcart_price").val();

    var data = {
      product_id: parseInt(product_id),
      quantity: parseInt(quantity),
      price: price,
      time_added: new Date(),
      checkout: "0",
    };

    var ajax = $.ajax({
      type: "POST",
      url: `/api/shopcarts/${shopcart_id}`,
      contentType: "application/json",
      data: JSON.stringify(data),
    });

    ajax.done(function (res) {
      update_form_data(res);
      flash_message("Success");
      $("#flash_message").attr("class", "text-success");
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
      $("#flash_message").attr("class", "text-danger");
    });
  });

  // ****************************************
  // Update a Shopcart item
  // ****************************************

  $("#update-btn").click(function () {
    var shopcart_id = $("#shopcart_customer_id").val();
    var product_id = $("#shopcart_product_id").val();
    var quantity = $("#shopcart_quantity").val();
    var price = $("#shopcart_price").val();

    var data = {
      product_id: product_id,
      quantity: parseInt(quantity),
      price: price,
      time_added: new Date(),
      checkout: "0",
    };

    var ajax = $.ajax({
      type: "PUT",
      url: `/shopcarts/${shopcart_id}/items/${product_id}`,
      contentType: "application/json",
      data: JSON.stringify(data),
    });

    ajax.done(function (res) {
      update_form_data(res);
      flash_message("Success");
      $("#flash_message").attr("class", "text-success");
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
      $("#flash_message").attr("class", "text-danger");
    });
  });

  // ****************************************
  // Retrieve a Shopcart item
  // ****************************************

  $("#retrieve-btn").click(function () {
    var shopcart_id = $("#shopcart_customer_id").val();
    var product_id = $("#shopcart_product_id").val();
    var queryString = "";
    if(shopcart_id){
        queryString+="/api/shopcarts?shopcart_id="+shopcart_id;
    }

    if(product_id) {
        queryString="/shopcarts/"+shopcart_id+"/items/"+product_id;
    }

    var ajax = $.ajax({
      type: "GET",
      url: queryString,
      contentType: "application/json",
      data: "",
    });

    if(product_id){
      ajax.done(function (res) {
        //alert (JSON.stringify(res))
        update_form_data(res);
        flash_message("Success");
        $("#flash_message").attr("class", "text-success");
      });
      
    }
    else{
      ajax.done(function (res) {
        //alert(res.toSource())
        $("#search_results").empty();
        var header = `
          <table class="table-dark w-100" cellpadding="3">
            <thead>
              <tr>
                <th class="col-12 col-md-2 text-center">Customer ID</th>
                <th class="col-12 col-md-3 text-center">Product ID</th>
                <th class="col-12 col-md-4 text-center">Quantity</th>
                <th class="col-12 col-md-3 text-center">Price</th>
                <th class="col-12 col-md-3 text-center">Checkout</th>
              </tr>
            </thead>
        `;
  
        var firstItem = "";
        var rows = res.map((item) => {
          // copy the first result to the form
          if (!firstItem) update_form_data(item);
          // build table
          return `<tr><td class="text-center">
            ${item.shopcart_id}
            </td><td class="text-center">
            ${item.product_id}
            </td><td class="text-center">
            ${item.quantity}
            </td><td class="text-center">
            ${item.price}
            </td><td class="text-center">
            ${item.checkout}
            </td></tr>`;
        });
  
        var table = header.concat(...rows, "</table>");
  
        $("#search_results").append(table);
  
        flash_message("Success");
        $("#flash_message").attr("class", "text-success");
      });
    }

     
    ajax.fail(function (res) {
      clear_form_data();
      flash_message(res.responseJSON.message);
      $("#flash_message").attr("class", "text-danger");
    });
  });

  // ****************************************
  // Delete a Shopcart item
  // ****************************************

  $("#delete-btn").click(function () {
    var shopcart_id = $("#shopcart_customer_id").val();
    var product_id = $("#shopcart_product_id").val();
    var queryString = "";

    if(shopcart_id){
      queryString+=shopcart_id;
    }
    if(product_id){
      queryString+="/items/"+product_id
    }

    
    var ajax = $.ajax({
      type: "DELETE",
      url: `/shopcarts/`+queryString,
      //contentType: "application/json",
    });

    ajax.done(function (res) {
      clear_form_data();
      flash_message("Item has been Deleted!");
      $("#flash_message").attr("class", "text-success");
    });

    ajax.fail(function (res) {
      flash_message("Server error!");
      $("#flash_message").attr("class", "text-danger");
    });
  });

  // ****************************************
  // Clear the form
  // ****************************************

  $("#clear-btn").click(function () {
    $("#shopcart_customer_id").val("");
    $("#shopcart_checkout").val("");
    flash_message("");
    $("#search_results").empty();
    var header = `
        <table class="table-dark w-100" cellpadding="3">
          <thead>
            <tr>
              <th class="col-12 col-md-2 text-center">Customer ID</th>
              <th class="col-12 col-md-3 text-center">Product ID</th>
              <th class="col-12 col-md-4 text-center">Quantity</th>
              <th class="col-12 col-md-3 text-center">Price</th>
              <th class="col-12 col-md-3 text-center">Checkout</th>
            </tr>
          </thead>
        </table>
      `;
    $("#search_results").append(header);
    clear_form_data();
  });

  // ****************************************
  // Search for a Shopcart item
  // ****************************************

  $("#search-btn").click(function () {
    var shopcart_id = $("#shopcart_customer_id").val();
    var product_id = $("#shopcart_product_id").val();

    var queryString = "";

    if (shopcart_id) {
      queryString += "shopcart_id=" + shopcart_id;
    }

    if (product_id) {
      if (queryString.length > 0) {
        queryString += "&product_id=" + product_id;
      } else {
        queryString += "product_id=" + product_id;
      }
    }

    var ajax = $.ajax({
      type: "GET",
      url: "/api/shopcarts?" + queryString,
      //contentType: "application/json",
      data: "",
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      $("#search_results").empty();
      var header = `
        <table class="table-dark w-100" cellpadding="3">
          <thead>
            <tr>
              <th class="col-12 col-md-2 text-center">Customer ID</th>
              <th class="col-12 col-md-3 text-center">Product ID</th>
              <th class="col-12 col-md-4 text-center">Quantity</th>
              <th class="col-12 col-md-3 text-center">Price</th>
              <th class="col-12 col-md-3 text-center">Checkout</th>
            </tr>
          </thead>
      `;

      var firstItem = "";
      var rows = res.map((item) => {
        // copy the first result to the form
        if (!firstItem) update_form_data(item);
        // build table
        return `<tr><td class="text-center">
          ${item.shopcart_id}
          </td><td class="text-center">
          ${item.product_id}
          </td><td class="text-center">
          ${item.quantity}
          </td><td class="text-center">
          ${item.price}
          </td><td class="text-center">
          ${item.checkout}
          </td></tr>`;
      });

      var table = header.concat(...rows, "</table>");

      $("#search_results").append(table);

      flash_message("Success");
      $("#flash_message").attr("class", "text-success");
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
      $("#flash_message").attr("class", "text-danger");
    });
  });

  // ****************************************
  // Checkout a Shopcart item
  // ****************************************

  $("#checkout-btn").click(function () {
    var shopcart_id = $("#shopcart_customer_id").val();
    var product_id = $("#shopcart_product_id").val();
    var quantity = $("#shopcart_quantity").val();
    var price = $("#shopcart_price").val();


    var queryString = "";

    var data = {
      product_id: product_id,
      quantity: parseInt(quantity),
      price: price,
      time_added: new Date(),
    };
    if (shopcart_id){
      queryString+= "/shopcarts/" + shopcart_id;
    }

    if(product_id){
      queryString+= "/items/" + product_id;
    }

    queryString+= "/checkout"

    var ajax = $.ajax({
      type: "PUT",
      url: queryString,
      contentType: "application/json",
      data: JSON.stringify(data),
    });
    ajax.done(function (res) {
      update_form_data(res);
      flash_message("Item have been checkout!");
      $("#flash_message").attr("class", "text-success");
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
      $("#flash_message").attr("class", "text-danger");
    });
  });
});
