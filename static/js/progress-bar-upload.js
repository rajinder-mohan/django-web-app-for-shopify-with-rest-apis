/*$(document).ready(function(event){
  var data = '{"csrfmiddlewaretoken": "'+csrf_token+'"}';
  document.getElementById("fileupload").setAttribute("data-form-data", data);
  
});*/


$(function () {

  $(".js-upload-photos").click(function () {
    
    $("#fileupload").click();
  });

  $("#fileupload").fileupload({
    dataType: 'json',
    sequentialUploads: true,

    start: function (e) {
      $("#modal-progress").modal("show");
    },

    stop: function (e) {
      $("#modal-progress").modal("hide");
    },

    progressall: function (e, data) {
      var progress = parseInt(data.loaded / data.total * 100, 10);
      var strProgress = progress + "%";
      $(".progress-bar").css({"width": strProgress});
      $(".progress-bar").text(strProgress);
    },

    done: function (e, data) {

      /*var token_data = "{'csrfmiddlewaretoken': '"+csrf_token+"', 'token': '"+data.result+"'}";

      document.getElementById("fileupload").setAttribute("data-form-data", token_data);*/
      if (data.result.is_valid) {
        document.getElementById("token").value = data.result.token;
        $('#view_image').attr('src', data.result.url);
        $('#view_image').attr('style', 'display: block; width: 100%;');
      }
      else{
        $("#message-error").html(data.result.message);
         $('#popup_error').modal('show');
        return false; 
      }
    }

  });

});
