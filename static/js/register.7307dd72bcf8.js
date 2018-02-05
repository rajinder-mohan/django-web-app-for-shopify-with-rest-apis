var register_form = $('#signup_form');
signupform();

var existing_error = "no";

function signupform(){

	register_form.submit(function(event) {

		var first_name = document.getElementById("first_name").value;

		var last_name = document.getElementById("last_name").value;

		var emailid = document.getElementById("emailid").value;

		var vendor = document.getElementById("vendor").value;

		var password = document.getElementById("passInput").value;

		if (first_name == ''){
			alert("first_name :  "+first_name);
			document.getElementById("first_name").addClass("error");
			existing_error = "yes";
		}
		else{
			existing_error = "no";	
		}

		if (last_name == ''){
			alert("last_name :  "+last_name);
			document.getElementById("last_name").addClass("error");
			existing_error = "yes";
		}
		else{
			existing_error = "no";	
		}

		if (emailid == ''){
			alert("emailid :   "+emailid);
			document.getElementById("emailid").addClass("error");
			existing_error = "yes";
		}
		else{
			existing_error = "no";	
		}

		if (vendor == ''){
			alert("vendor  :  "+vendor);
			document.getElementById("vendor").addClass("error");
			existing_error = "yes";
		}
		else{
			existing_error = "no";	
		}

		if (password == ''){
			alert("password :   "+password);
			document.getElementById("passInput").addClass("error");
			existing_error = "yes";
		}
		else{
			existing_error = "no";	
		}

		if (existing_error == "no"){
			$(document.body).addClass('show_gif');

			$.ajax({
		        type: mem_frm.attr('method'),
		        url: mem_frm.attr('action'),
		        data: mem_frm.serialize(),
		        success: function (response) {

		        	 $(document.body).removeClass('show_gif');
		        	
		        	var resp = JSON.parse(response);
		        	if (resp.error){
		        		$('#message-error').html(resp.error);
						$('#popup_error').modal('show');
						return false;	
		        	}
		        	else{
		        		$('#message-success').html(resp.success);
						$('#popup_success').modal('show');

						$("#popup_success").on('hidden.bs.modal', function () {
						    window.location = "/profile";
						});	
		        	}
		        }
		    });
		}
			
	    event.preventDefault();
	});
}

$('#first_name').blur(function(event){
	var fname = $(this).val();
	if (fname == ''){
		$(this).addClass("error");
	}
});

$('#first_name').click(function(event){
	$(this).removeClass("error");
});

$('#last_name').blur(function(event){
	var fname = $(this).val();
	if (fname == ''){
		$(this).addClass("error");
	}
});

$('#last_name').click(function(event){
	$(this).removeClass("error");
});