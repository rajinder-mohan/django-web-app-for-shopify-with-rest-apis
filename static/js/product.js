$.validator.addMethod("price_validate", function(value, element) {
    return /^[0-9]{0,7}\.[0-9]{0,2}$/.test(value);
}, "Only 7 digits allowed before decimal and 2 digits after decimal.");

$.validator.addMethod("smaller_price", function(value, element) {
  var selling = document.getElementById("exampleInputSellingAmount").value;

  if (selling == ''){
    selling = 0.0;
  }

  return parseFloat(selling) > parseFloat(value);

}, "WholeSale Price must be smaller than Selling Price");


$.validator.addMethod("larger_price", function(value, element) {
  var wholesale = document.getElementById("exampleInputWholeSaleAmount").value;

  if (wholesale == ''){
    wholesale = 0.0;
  }
  return parseFloat(wholesale) < parseFloat(value);

  
}, "Selling Price must be greater than WholeSale Price");


$.validator.addMethod("minquantity", function(value, element){
  return parseInt(value) >= 1;
}, "Quantity must be greater than or equal to 1");

$.validator.addMethod("validate_title", function(value, element){
  return /^[a-zA-Z]{1,}[a-zA-Z0-9 _,-]{1,50}$/.test(value);
}, "Title must start with characters only and include alphanumeric and special characters like -_,");
  
  $("#add-product").validate({
       rules: {
        title: {
          required: true,
          maxlength: 50,
          validate_title: true
        },
        description: "required",
        selling_price: {
          required: true,
          price_validate: true,
          larger_price: true
        },
        wholesale_price: {
          required: true,
          price_validate: true,
          smaller_price: true
        },
        dropshipping_price: {
          price_validate: true
        },
        sku: {
          alphanumeric: true
        },
        barcode: {
          alphanumeric: true
        },
        password: {
          required: true,
        },
        quantity: {
          required: true,
          minquantity: true
        }
       },
       submitHandler: function(form){
        form.submit();
       }
    });

  var $input = $('#title').keyup(function(e) {
 var max = 50; 
 
 if ($input.val().length > max) 
  {  
    $input.val($input.val().substr(0, max)); 
  }
   });

   var $input1 = $('#description').keyup(function(e) {
 var max1 = 1000; 
 
 if ($input1.val().length > max1) 
  {  
    $input1.val($input1.val().substr(0, max1)); 
  }
   });

   var selling_field = document.getElementById('exampleInputSellingAmount');

selling_field.addEventListener('change', function() {
    var v = parseFloat(this.value);
    if (isNaN(v)) {
        this.value = '';
    } else {
        this.value = v.toFixed(2);
    }
});

 var dropshipping_field = document.getElementById('exampleInputDropshippingAmount');

dropshipping_field.addEventListener('change', function() {
    var v = parseFloat(this.value);
    if (isNaN(v)) {
        this.value = '';
    } else {
        this.value = v.toFixed(2);
    }
});

var wholesale_field = document.getElementById('exampleInputWholeSaleAmount');

wholesale_field.addEventListener('change', function() {
    var v = parseFloat(this.value);
    if (isNaN(v)) {
        this.value = '';
    } else {
        this.value = v.toFixed(2);
    }
});

 var $sku_input = $('#sku').keyup(function(e) {
 var max = 90; 
 
 if ($sku_input.val().length > max) 
  {  
    $sku_input.val($sku_input.val().substr(0, max)); 
  }
   });

 var $barcode_input = $('#barcode').keyup(function(e) {
 var max = 90; 
 
 if ($barcode_input.val().length > max) 
  {  
    $barcode_input.val($barcode_input.val().substr(0, max)); 
  }
   });
