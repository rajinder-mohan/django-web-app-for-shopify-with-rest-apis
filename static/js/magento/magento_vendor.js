$.validator.addMethod("validate_url", function(value, element){
return value.match(/(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g);
}, "Please enter valid url.");



// register magento vendor

$("#signmagento").validate({

     rules: {

         name:{
            required: true,
         },

      email: {
        required: true,


      },
      platform: {
        required: true,
      },

      website: {
        required: true,
        validate_url: true
      },
      country: {
        required : true
     }
   },
     submitHandler: function(form){
       $.ajax({

          url: form.action,
          method: form.method,
          data: $(form).serialize(),
          success: function(response){

            var $container = $("html,body");

            var namerror=response.indexOf("Name");
            var emailerror=response.indexOf("Email");
            var websiterror=response.indexOf("Website");
            var exception=response.indexOf("exception");
            var success=response.indexOf("success");
            $('.name').removeClass('error');
            $('.show_name_error').hide();
            $('.email').removeClass('error');
            $('.show_email_error').hide();
            $('.website').removeClass('error');
            $('.show_web_error').hide();
            $('.success').hide();
            $('.success').removeClass('greenish');

            if(namerror!='-1')
                   {
                     $('.name').addClass('error');
                     $('.show_name_error').show();

                     var $scrollTo = $('.name');

                     $container.animate({scrollTop: $scrollTo.offset().top - $container.offset().top + $container.scrollTop(), scrollLeft: 0},300);
                     return false
                   }

             if(emailerror!='-1')
                    {
                      $('.email').addClass('error');
                      $('.show_email_error').show();

                      var $scrollTo = $('.email');

                      $container.animate({scrollTop: $scrollTo.offset().top - $container.offset().top + $container.scrollTop(), scrollLeft: 0},300);
                      return false
                    }
              if(websiterror!='-1')
                    {
                             $('.website').addClass('error');
                             var $scrollTo = $('.website');

                             $container.animate({scrollTop: $scrollTo.offset().top - $container.offset().top + $container.scrollTop(), scrollLeft: 0},300);
                             $('.show_web_error').show();
                             return false
                     }

               if(exception!='-1')
                     {
                              window.location('/magento/vendor_login');
                              return false
                      }

               if(success!='-1')
                     {
                       $('.success').addClass('greenish');
                       $("html, body").animate({ scrollTop: 0 }, "slow");
                       $('.success').show();

                              return false
                      }

          }
     });
  }
});







// #login magento vendor

$("#login_magentoform").validate({

     rules: {

         loginemail:{
            required: true,
         },

      loginpassword: {
        required : true
     }
   },
     submitHandler: function(form){
       $.ajax({

          url: form.action,
          method: form.method,
          data: $(form).serialize(),
          success: function(data){

            var emailerror=data.indexOf("emailerror");
            var status=data.indexOf("status");
            var shop=data.indexOf("shop");
            var passworderror=data.indexOf("passworderror");
            var done=data.indexOf("success");

            $('#loginemailerror').removeClass('error');
            $('#passInput').removeClass('error');
            $('.login_email_error').hide();
            $('.status').hide();
            $('.show_pass_error').hide();
            $('.shop').hide();
               if(emailerror!='-1')
                     {
                       $('#loginemailerror').addClass('error');

                       $('.login_email_error').show();

                              return false
                      }

              if(status!='-1')
                    {
                      $('.status').show();
                             return false
                     }

             if(shop!='-1')
                   {
                     $('.shop').show();
                            return false
                    }

              if(passworderror!='-1')
                    {
                      $('#passInput').addClass('error');

                      $('.show_pass_error').show();

                             return false
                     }

             if(done!='-1')
                   {



                            window.location.href= '/magento/vendor_dashboard'
                    }

          }
     });
  }
});







// vendor forget

$('#forget_password_button').click(function(){

  var e=$.trim($("#email").val());
  var p=$.trim($("#forgetto").val());
  var token=$("[name='csrfmiddlewaretoken']").val();
  $("#mag_vender_forget_email_msg").css('display','none');
  $("#mag_vender_forget_email_success_msg").css('display','none');
  var email_regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  if(e==""|| e==null){
    $("#mag_vender_forget_email_msg").html("This field is required.");
    $("#mag_vender_forget_email_msg").show();
  }
  else if(!email_regex.test(e)){
    $("#mag_vender_forget_email_msg").html("Not a valid email.");
    $("#mag_vender_forget_email_msg").show();
  }
  else{
    $.ajax({
        type: 'POST',
        url:  p,
        data: {'email': e,"csrfmiddlewaretoken":token},
        success: function (response) {
          if(response.status==1){
            $("#mag_vender_forget_email_success_msg").html(response.msg);
            $("#mag_vender_forget_email_success_msg").show();
          }
          else{
            $("#mag_vender_forget_email_msg").html(response.msg);
            $("#mag_vender_forget_email_msg").show();
          }
        }
    });
  }
});


function calDropPrice(counter,elmnt){
  var value=elmnt.value;
  if(value=="" || value==null){
    value=0
  }
  var t_price = document.getElementById("t_price").value;
  var reg = new RegExp('^[0-9]+$');
  if(reg.test(value)){
    dropshiping_price = (value * t_price)/ 100;
    document.getElementById("dropshipping_price_0"+counter).innerHTML =t_price-dropshiping_price;
    document.getElementById("drop_price"+counter).innerHTML =t_price-dropshiping_price;
  }
  else{
    return false;
  }
}
function wholeSalePrice(counter,elmnt){
  var value=elmnt.value;
  if(value=="" || value==null){
    value=0
  }
  var t_price = document.getElementById("t_price").value;
  var reg = new RegExp('^[0-9]+$');
  if(reg.test(value)){
    wholesale_price = (value * t_price)/ 100;
    document.getElementById("wholesale_price_0"+counter).innerHTML =t_price-wholesale_price;
    document.getElementById("wholesale_price"+counter).innerHTML =t_price-wholesale_price;
  }
  else{
    return false;
  }
}

function changeAccess(elmnt,counter){
  var access=elmnt.checked;
  var vendor = document.getElementById("v_id"+counter).value;
  var merchant = document.getElementById("m_id"+counter).value;
  $.ajax({
      type: 'POST',
      url:  allowmerchantaccess,
      data: {'access': access,"vendor":vendor,"merchant":merchant,"csrfmiddlewaretoken":token},
      success: function (response) {
        alert(response.msg)
      }
  });

}
$.urlParam = function(name){
  var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
  if(results == null || results == "")
  {
    return results
  }
  else{
    return results[1] || 0;
  }

}

$( document ).ready(function() {

    var today = new Date().toISOString().split('T')[0];
  var param_value=$.urlParam('tabv');

  if(param_value == null || param_value == "")
  {
    return false
  }
  else{

    var a='#'+param_value;
    $(a).trigger("click");
  }

});
function updatePaypal(){
  var email=document.getElementById("new_paypal_mail").value;
  if(email=="" & email==null){
    alert("Please enter your paypal email.")
  }
  else{
    $.ajax({
        type: 'GET',
        url:  'vendor_update_paypal',
        data: {'paypal_email': email},
        success: function (response) {
          if(typeof response.error != "undefined"){
            alert(response.error)
          }
          if(typeof response.success != "undefined"){
            alert(response.success)
          }
        }
    });
  }
}
