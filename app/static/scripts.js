var selected = 'Dashboard';
    // Function that loads the appropriate event when selected and updates the UI to reflect it
function select(pane) {
    $("#nav" + selected).removeClass('selected'); // "De-select" the row of the previously selected event
    $("#nav" + selected).find(".nav-item-icon").attr('src', '../static/img/' + selected.toLowerCase() + '-24px.png');
    selected = pane; // Set the selected event to the event that was clicked
    $("#nav" + pane).addClass('selected'); // "Select" the row of the clicked event
    $("#nav" + selected).find(".nav-item-icon").attr('src', '../static/img/selected-' + selected.toLowerCase() + '-24px.png');
    // Load the event data into the page
    loadPane('pan' + pane);
}

function loadPane(paneId) {
    $(".pane").hide();
    $("#" + paneId).show();
    if (paneId == 'panDashboard') {
        
    }
}
function popOrdersTable(orders) {
    console.log(orders[0]['order_id']);
    var orderTable = document.getElementById('orders').getElementsByTagName('tbody')[0];
    for (var i = 0; i<orders.length; i++) {
        var row = orderTable.insertRow(i);
        var cell_no = 0;
        var order_id = row.insertCell(cell_no++);
        order_id.innerHTML = orders[i]['id'];
        var buyer_id = row.insertCell(cell_no++);
        buyer_id.innerHTML = orders[i]['user'];
        var order_date = row.insertCell(cell_no++);
        order_date.innerHTML = moment(orders[i]['created']).format('DD/MM/YYYY HH:MM:SS');
        var last_update_date = row.insertCell(cell_no++);
        last_update_date.innerHTML = moment(orders[i]['last_update']).format('DD/MM/YYYY HH:MM:SS');
        var last_updated_by = row.insertCell(cell_no++);
        last_updated_by.innerHTML = orders[i]['last_updated_by'];
        var status = row.insertCell(cell_no++);
        status.innerHTML = orders[i]['status'];
    }
}
function popOrderDetailsTable(orderActions) {
    console.log(orderActions[0]['employee_id']);
    var orderDetailsTable = document.getElementById('orderDetails').getElementsByTagName('tbody')[0];
    for (var i = 0; i<orderActions.length; i++) {
        var row = orderDetailsTable.insertRow(i);
        var cell_no = 0;
        var employee_id = row.insertCell(cell_no++);
        employee_id.innerHTML = orderActions[i]['id'];
        var timestamp = row.insertCell(cell_no++);
        timestamp.innerHTML = orderActions[i]['action'];
        var updated_by = row.insertCell(cell_no++);
        updated_by.innerHTML = moment(orderActions[i]['datetime']).format('DD/MM/YYYY HH:MM:SS');
        var action = row.insertCell(cell_no++);
        action.innerHTML = orderActions[i]['actor'];
    }
}
// function popEmployeeTable(employees) {
// 	console.log(employees[0]['order_id']);
// 	var employeeTable = document.getElementById('employees').getElementsByTagName('tbody')[0];
// 	for (var i = 0; i<employees.length; i++) {
// 		console.log(employees[i]);
// 		var row = employeeTable.insertRow(i);
// 		var cell_no = 0;
// 		var order_id = row.insertCell(cell_no++);
// 		order_id.innerHTML = employees[i]['order_id'];
// 		var buyer_id = row.insertCell(cell_no++);
// 		buyer_id.innerHTML = employees[i]['buyer_id'];
// 		var order_date = row.insertCell(cell_no++);
// 		order_date.innerHTML = employees[i]['order_date'];
// 		var last_update_date = row.insertCell(cell_no++);
// 		last_update_date.innerHTML = employees[i]['last_update_date'];
// 		var last_updated_by = row.insertCell(cell_no++);
// 		last_updated_by.innerHTML = employees[i]['last_updated_by'];
// 		var status = row.insertCell(cell_no++);
// 		status.innerHTML = employees[i]['status'];
// 	}
// }
// Set up event listener for when the DOM is fully loaded
$(document).ready(function() {
    // Select the provided event, or the first event as appropriate
    select(selected);
    
    $(".side-nav-item").click(function(e) {
        select($(this).attr('id').substring(3));
    });
    // call endpoint for list of orders
    // var employees = []
    var orders = JSON.parse({{orders|tojson}});
    // popEmployeeTable(employees);
    popOrdersTable(orders);
    // popOrderDetailsTable(orderActions);
    var ordersTable = $('#orders').DataTable();
    var employeesTable = $('#employees').DataTable();
    var orderDetails = $('#orderDetails').DataTable({searching: false, paging: false, info: false});

    $('#orders tbody').on('click', 'tr', function () {
        var data = ordersTable.row(this).data();
        var detailsModal = $('#detailsModal');
        
        //detailsModal.find('.modal-body').text(data[0]);
        detailsModal.modal('show');
        $.getJSON('/transactions/'+data[0], function(result){
            if (result) {
                popOrderDetailsTable(result);
                $('.odd').hide();
            }
        })
        //alert( 'You clicked on '+data[0]+'\'s row' );
    });	
});
