    function fetchData() {
        $.get('/fetch_data', function() {
            // When the data is fetched, hide the loading message and display the table
            $.get('/create_table', function(html_table) {
                // When the table is created, display it in the main div
                $('#main').html(html_table);
                console.log(html_table);
            });
            $('#loading-message').hide();
            $('#index-page').show();
        });
    }
    // Call the fetchData function when the page is loaded
    $(document).ready(function() {
        fetchData();
    })
    function sortTable(column) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("myTable");
    switching = true;
    dir = "asc";
    while (switching) {
      switching = false;
      rows = table.getElementsByTagName("tr");
      for (i = 1; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("td")[column];
        y = rows[i + 1].getElementsByTagName("td")[column];
        if (isNaN(x.innerHTML)) {
          if (dir == "asc") {
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
              shouldSwitch= true;
              break;
            }
          } else if (dir == "desc") {
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
              shouldSwitch = true;
              break;
            }
          }
        } else {
          if (dir == "asc") {
            if (Number(x.innerHTML) > Number(y.innerHTML)) {
              shouldSwitch= true;
              break;
            }
          } else if (dir == "desc") {
            if (Number(x.innerHTML) < Number(y.innerHTML)) {
              shouldSwitch = true;
              break;
            }
          }
        }
      }
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;
      } else {
        if (switchcount == 0 && dir == "asc") {
          dir = "desc";
          switching = true;
        }
      }
    }
  }