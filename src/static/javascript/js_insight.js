
    // Function to modify the classes of the HTML elements
    function modifyClasses() {
        // Get all the tab links and content divs
        const tablinks = $(".tabitem");
        const tabcontent = $(".tabcontent");


        // Set the width of all tab content divs to match the main content area
        tabcontent.width($(".main").width());

        // Add click event listener to each tab link
        tablinks.click(function() {

            // Hide all tab content divs and show the one corresponding to the clicked tab
            tabcontent.removeClass("active");
            const tabid = $(this).attr("data-tabid");
            $("#" + tabid).addClass("active");

            // Set the clicked tab to active and deactivate all others
            tablinks.removeClass("active");
            $(this).addClass("active");

        });

        // Resize event listener to adjust the width of tab content divs when the window is resized
        $(window).resize(function() {
            tabcontent.width($(".main").width());
        });
    }

    // Call the createElements function when the page is loaded
    $(document).ready(function() {
        createElements();
    });
