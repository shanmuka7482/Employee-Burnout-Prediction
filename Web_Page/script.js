document.getElementById("Designation").addEventListener("input", function (e) {
  const min = parseInt(e.target.min);
  const max = parseInt(e.target.max);
  const value = parseInt(e.target.value);
  if (value < min) {
    e.target.value = min;
  } else if (value > max) {
    e.target.value = max;
  }
});

document
  .getElementById("Resource_Allocation")
  .addEventListener("input", function (e) {
    const min = parseInt(e.target.min);
    const max = parseInt(e.target.max);
    const value = parseInt(e.target.value);
    if (value < min) {
      e.target.value = min;
    } else if (value > max) {
      e.target.value = max;
    }
  });

document
  .getElementById("Mental_Fatigue_Score")
  .addEventListener("input", function (e) {
    const min = parseInt(e.target.min);
    const max = parseInt(e.target.max);
    const value = parseInt(e.target.value);
    if (value < min) {
      e.target.value = min;
    } else if (value > max) {
      e.target.value = max;
    }
  });

const genderInput = document.getElementById("Gender");
const allowedGenders = ["Male", "Female"];

genderInput.addEventListener("change", function () {
  if (!allowedGenders.includes(genderInput.value)) {
    alert("Please select a valid option.");
    genderInput.value = "";
  }
});
const CompanyInput = document.getElementById("Company");
const allowedCompanys = ["Product", "Service"];

CompanyInput.addEventListener("change", function () {
  if (!allowedCompanys.includes(CompanyInput.value)) {
    alert("Please select a valid option.");
    CompanyInput.value = "";
  }
});
const WFHInput = document.getElementById("WFH");
const allowedWFH = ["Yes", "No"];

WFHInput.addEventListener("change", function () {
  if (!allowedWFH.includes(WFHInput.value)) {
    alert("Please select a valid option.");
    WFHInput.value = "";
  }
});

$(document).ready(function() {
  $('#myForm').on('submit', function(event) {
      event.preventDefault();

      var formData = $(this).serialize();
      console.log(formData);
      $.ajax({
          type: 'POST',
          url: 'http://127.0.0.1:5000/submit',
          data: formData,
          success: function(response) {
              $('#ans').html('<h2>Ans: ' + response + '%</h2>');
          },
          error: function(error) {
              console.error('Error:', error);
          }
      });
  });
});
