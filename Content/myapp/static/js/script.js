var return_date = document.getElementById("return_date");
var oneWayButton = document.getElementById("oneWayButton");
var roundTripButton = document.getElementById("roundTripButton");
var searchButton = document.getElementById("searchButton");
var checkButton = document.getElementById("checkButton");

var searchBlock = document.getElementById("searchBlock");
var checkBlock = document.getElementById("checkBlock");

sessionStorage.setItem("Page2Visited", "True");

function oneWay(){
    return_date.style.display = "none";
    oneWayButton.className += " active";
    roundTripButton.className = "smallButton";
    
}

function roundTrip(){
    return_date.style.display = "flex";
    roundTripButton.className += " active";
    oneWayButton.className = "smallButton";
}

function checkForm(){
    if(roundTripButton.className.includes("active")){
        var inputs = document.getElementsByTagName("input");
        var i = 0;
        for(i=0; i< 4 ; i++){
            if ((inputs[i].value == "") || (inputs[i].value == null)){
                console.log("here");
                inputs[i].focus();
                inputs[i].select();
                inputs[i].style.backgroundColor="#f88";
                alert ("You need to fill in the return date field.");
                return false;
            }
        }
    }
    return true;
}

function validate(){
    var input1 = document.getElementById("dept_date");
    var input2 = document.getElementById("arr_date");
    console.log(input1.value);
    if((input1.value == "" || input1.value == null) && (input2.value == "" || input2.value == null)){
        alert ("You need to fill in at least one of the dates.");
        return false;
    }
    return true;
}

function search(){
    checkBlock.style.display = "none";
    searchBlock.style.display = "block";
    searchButton.className += " chosen";
    checkButton.className = "bigButton";
}

function check(){
    searchBlock.style.display = "none";
    checkBlock.style.display = "block";
    checkButton.className += " chosen";
    searchButton.className = "bigButton";
}