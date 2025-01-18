jQuery(document).ready(function($) {
  "use strict";

  //Contact
  $('form.contactForm').submit(function() {
    var f = $(this).find('.form-group'),
      ferror = false,
      emailExp = /^[^\s()<>@,;:\/]+@\w[\w\.-]+\.[a-z]{2,}$/i;

    f.children('input').each(function() { // run all inputs

      var i = $(this); // current input
      var rule = i.attr('data-rule');

      if (rule !== undefined) {
        var ierror = false; // error flag for current input
        var pos = rule.indexOf(':', 0);
        if (pos >= 0) {
          var exp = rule.substr(pos + 1, rule.length);
          rule = rule.substr(0, pos);
        } else {
          rule = rule.substr(pos + 1, rule.length);
        }

        switch (rule) {
          case 'required':
            if (i.val() === '') {
              ferror = ierror = true;
            }
            break;

          case 'minlen':
            if (i.val().length < parseInt(exp)) {
              ferror = ierror = true;
            }
            break;

          case 'email':
            if (!emailExp.test(i.val())) {
              ferror = ierror = true;
            }
            break;

          case 'checked':
            if (! i.is(':checked')) {
              ferror = ierror = true;
            }
            break;

          case 'regexp':
            exp = new RegExp(exp);
            if (!exp.test(i.val())) {
              ferror = ierror = true;
            }
            break;
        }
        i.next('.validation').html((ierror ? (i.attr('data-msg') !== undefined ? i.attr('data-msg') : 'wrong Input') : '')).show('blind');
      }
    });
    f.children('textarea').each(function() { // run all inputs

      var i = $(this); // current input
      var rule = i.attr('data-rule');

      if (rule !== undefined) {
        var ierror = false; // error flag for current input
        var pos = rule.indexOf(':', 0);
        if (pos >= 0) {
          var exp = rule.substr(pos + 1, rule.length);
          rule = rule.substr(0, pos);
        } else {
          rule = rule.substr(pos + 1, rule.length);
        }

        switch (rule) {
          case 'required':
            if (i.val() === '') {
              ferror = ierror = true;
            }
            break;

          case 'minlen':
            if (i.val().length < parseInt(exp)) {
              ferror = ierror = true;
            }
            break;
        }
        i.next('.validation').html((ierror ? (i.attr('data-msg') != undefined ? i.attr('data-msg') : 'wrong Input') : '')).show('blind');
      }
    });
    if (ferror) return false;
    else var str = $(this).serialize();
    var action = $(this).attr('action');
    if( ! action ) {
      action = 'contactform/contactform.php';
    }
    $.ajax({
      type: "POST",
      url: action,
      data: str,
      success: function(msg) {
        // alert(msg);
        if (msg == 'OK') {
          $("#sendmessage").addClass("show");
          $("#errormessage").removeClass("show");
          $('.contactForm').find("input, textarea").val("");
        } else {
          $("#sendmessage").removeClass("show");
          $("#errormessage").addClass("show");
          $('#errormessage').html(msg);
        }

      }
    });
    return false;
  });

});

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('subscribe-form');

  if (!form) {
    console.error('Subscribe form not found');
    return;
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission

    const emailInput = form.querySelector('input[name="email"]');
    const userEmail = emailInput ? emailInput.value.trim() : '';

    if (!userEmail) {
      console.error('Email address is empty');
      const errorMessage = document.getElementById('error-message');
      errorMessage.textContent = 'Please enter a valid email address.';
      errorMessage.classList.add('show');
      errorMessage.classList.remove('hidden');
      return;
    }

    // Initialize EmailJS
    emailjs.init('VGfOGzIGXBFSpITum'); // Replace with your public key

    // Prepare the email parameters
    const emailParams = {
      to_email: userEmail,
      admin_email: 'your-admin-email@example.com', // Replace with your admin email
    };

    // Send form data
    emailjs.send('service_ek4oquw', 'template_idnoju5', emailParams)
      .then(function (response) {
        console.log('SUCCESS!', response.status, response.text);
        const successMessage = document.getElementById('success-message');
        successMessage.classList.add('show'); // Show success message
        successMessage.classList.remove('hidden');
        document.getElementById('error-message').classList.add('hidden'); // Hide error message
        form.reset(); // Clear the form
      })
      .catch(function (error) {
        console.error('FAILED...', error);
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = 'An error occurred. Please try again.';
        errorMessage.classList.add('show'); // Show error message
        errorMessage.classList.remove('hidden');
        document.getElementById('success-message').classList.add('hidden'); // Hide success message
      });
  });
});
