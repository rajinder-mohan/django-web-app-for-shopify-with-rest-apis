$.validator.addMethod("validate_url", function(value, element){
return value.match(/^(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9./]+$/g);
}, "Please enter valid url.");

$.validator.addMethod("validate_emailid", function(value, element){
return value.match(/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/);
}, "Please enter valid email.");

// register magento merchant

$("#signmagento").validate({

     rules: {

         name:{
            required: true,
         },

      email: {
        required: true,
        validate_emailid:true

      },
      platform: {
        required: true,
      },

      mag_domain: {
        required: true,
        validate_url: true
      }
   },
     submitHandler: function(form){
       $.ajax({

          url: form.action,
          method: form.method,
          data: $(form).serialize(),
          success: function(response){

            var $container = $("html,body");

             if(response.email=='error')
                    {

                      $('.email').addClass('error');
                      $('.show_email_error').show();

                      var $scrollTo = $('.email');

                      $container.animate({scrollTop: $scrollTo.offset().top - $container.offset().top + $container.scrollTop(), scrollLeft: 0},300);
                      return false
                    }
              if(response.domain=='error')
                    {
                             $('.mag_domain').addClass('error');
                             var $scrollTo = $('.mag_domain');
                             $('.show_web_error').show();
                             $container.animate({scrollTop: $scrollTo.offset().top - $container.offset().top + $container.scrollTop(), scrollLeft: 0},300);

                             return false
                     }

               if(typeof response.exception!='undefined')
                     {
                              alert('Exception Exists');
                              return false
                      }

               if(typeof response.Success!='undefined')
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



                            window.location.href= merchant_dashoboar;
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
function varients(elmnt){
var selectvalues = $(elmnt).val();
if(selectvalues=="false"){
  return false;
}
var parent_id = $(elmnt).parent('div').attr("data-id");
var selectsiblings = $(elmnt).siblings("select");
var value_array=[];
var final_array=[];
var check = 0;
value_array.push(selectvalues);
$(selectsiblings).each(function(){
  var valselected=$(this).val();
  if(valselected=="false"){
    check=1;
    return false;
  }
  else{
    value_array.push(valselected);
  }

});
if(check==0){
  final_array.push({
    [parent_id]:value_array
  });
  $.ajax({
      type: 'GET',
      url:  'view_varient_product',
      data: {'product_data': JSON.stringify(final_array)},
      success: function (response) {

        var new_images="";
        if(typeof response.price != "undefined"){
          $(elmnt).siblings('span.product-price').html(response.price);
        }
        if(typeof response.images != "undefined"){
          var imgs=response.images;
          for(i=0;i<imgs.length;i++){
            new_images ="<img src='"+imgs[i]+"'>";
          }
          alert(new_images)
          $("#images_slider"+parent_id).html(new_images);
          $("#images_slider"+parent_id).addClass("mvp-custom-class");
        }
      }
  });
}
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
/*------------------Add Products to magento-------------------------*/
// $(document).click('#add_product',function(){
//   var token=$("[name='csrfmiddlewaretoken']").val();
//   $.ajax({
//       type: 'POST',
//       url:  add_products_url,
//       data: {
//         "product_id":"1",
//         "csrfmiddlewaretoken":token
//       },
//       success: function (response) {
//         alert(response);
//       }
//   });
// });
