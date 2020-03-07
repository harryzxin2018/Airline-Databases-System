var airline_name = '';
var flight_num = '';
var dept_time = '';
var airline_name2 = '';
var flight_num2 = '';
var dept_time2 = '';
var value1 = 0;
var value2 = 0;

$(document).ready(function(){
    $(".radio").click(function(){
        var tds = $(".dept_flight");
        var i = 10* parseInt($(this).val());
        airline_name = tds.eq(i).text();
        flight_num = tds.eq(i+1).text();
        dept_time = tds.eq(i+2).text();
        value1 = parseFloat(tds.eq(i+8).text());
        var currentValue = value1 + value2;
        $("#total").text(currentValue);
    });

    $(".radio2").click(function(){
        var tds = $(".return_flight");
        var i = 10* parseInt($(this).val());
        airline_name2 = tds.eq(i).text();
        flight_num2 = tds.eq(i+1).text();
        dept_time2 = tds.eq(i+2).text();
        value2 = parseFloat(tds.eq(i+8).text());
        var currentValue = value1 + value2;
        $("#total").text(currentValue);
    });

    $("#purchase").click(function(){
        if(airline_name == ''){
            alert("please pick a flight.");
            return;
        }else if($(".return_flight").length != 0){
            if(airline_name2 == ''){
                alert("please pick a return flight.");
                return;
            }
        }
        $.ajax({
            type: "POST",
            data : {
                'airline_name':airline_name, 
                'flight_num': flight_num, 
                'dept_time': dept_time, 
                'price':value1, 
                'airline_name2':airline_name2, 
                'flight_num2': flight_num2, 
                'dept_time2': dept_time2, 
                'price2': value2
            },
            url : "/purchaseTickets",
            success:function(response){
                $("html").html(response);
           }
        })
    });
  });

function checkOut(){
    var cust_email = null;
    if($('#cust_email') != null){
        cust_email = $('#cust_email').val();
    }
    $.ajax({
        type: "POST",
        data : {
            'airline_name':$('#dept_airline').text(), 
            'flight_num': $('#dept_num').text(), 
            'dept_time': $('#dept_time').text(), 
            'price': parseFloat($('#dept_price').text()), 
            'airline_name2':$('#return_airline').text(), 
            'flight_num2': $('#return_num').text(), 
            'dept_time2': $('#return_time').text(), 
            'price2': parseFloat($('#return_price').text()),
            'card_type': $("input[name='Card type']:checked").val(),
            'card_num': $('#cardnum').val(),
            'name_on_card': $('#name').val(),
            'expr_date': $('#expr').val(),
            'cust_email': cust_email,
        },
        url : "/purchaseDetails",
        success:function(data){
            if(data == "Success"){
                alert("Purchased successfully.");
                if(cust_email == null){
                    window.location.replace("/customerHome");
                }else{
                    window.location.replace("/agentHome");
                }
            }else if(data == "Failure"){
                alert("This customer does not exist.");
                window.location.replace("/agentHome");
            }else if(data == "Purchased"){
                alert("Already purchased the flight before.");
                if(cust_email == null){
                    window.location.replace("/customerHome");
                }else{
                    window.location.replace("/agentHome");
                }
            }
        }
    })
}