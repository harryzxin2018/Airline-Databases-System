var customerForm = document.getElementById("customerForm");
var agentForm = document.getElementById("agentForm");
var staffForm = document.getElementById("staffForm");

if (sessionStorage.getItem("Page2Visited")) {
    sessionStorage.removeItem("Page2Visited");
    window.location.reload(true); // force refresh page1
}

function changeRole(){
    var x = document.getElementById("mySelect").value;
    if(x == "customer"){
        customerForm.style.display = "block";
        agentForm.style.display = "none";
        staffForm.style.display = "none";
    }else if(x == "agent"){
        agentForm.style.display = "block";
        customerForm.style.display = "none";
        staffForm.style.display = "none";
    }else{
        staffForm.style.display = "block";
        agentForm.style.display = "none";
        customerForm.style.display = "none";
    }
}

function checkForm(){
    var inputs = document.getElementsByTagName("input");
    var p, q;
    if(document.getElementById("mySelect").value == "customer"){
        p = 0;
        q = 3;
    }else if(document.getElementById("mySelect").value == "agent"){
        p = 3;
        q = 6;
    }else{
        p = 6;
        q = inputs.length;
    }
	for(var i = p; i < q; i++){
        if(inputs[i].name=="email"){
            var regex = /\w+@\w+\.\w+/;
            if (!regex.test(inputs[i].value)) {
                alert ("Make sure to input a valid email format.")
                inputs[i].focus();
                inputs[i].select();
                inputs[i].style.backgroundColor="#f88";
                return false;
            }
        }
        if(inputs[i].name=="password"){
            if(inputs[i].value == "" || inputs[i].value.length < 4){
               alert ("Make sure to provide a password longer than 4 characters.");
               inputs[i].focus();
               inputs[i].select();
               inputs[i].style.backgroundColor="#f88";
               return false;
            }
        }
        if ((inputs[i].value == "") || (inputs[i].value == null)){
          inputs[i].focus();
          inputs[i].select();
          inputs[i].style.backgroundColor="#f88";
          alert ("You need to fill in the " + inputs[i].placeholder + " field.");
          return false;
        }
    }
    return true;
}