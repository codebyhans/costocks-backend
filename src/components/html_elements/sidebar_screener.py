from flask import current_app


class sidebarScreener:
    def __init__(self, settings):
        tickers = (
            [ticker[0] for ticker in settings.tickers]
            if settings.tickers is not None
            else []
        )
        benchmark = (
            [ticker[0] for ticker in settings.benchmarks]
            if settings.benchmarks is not None
            else []
        )
        self.html = f"<div id='sidebardiv'><form method='GET' action='/insight' id='sidebarform'>"
        self.html += f"""
        <label for="tickers">Select ticker symbols:</label><br>
        <input type="text" name="tickers" id="tickers" value='{', '.join(tickers)}' />
        <button type='add' id='button1' class="btn btn-primary">C20</button>
        <button type='add' id='button2' class="btn btn-primary">DOW</button>
        <button type='clear' id='button0' class="btn btn-secondary">Clear</button><br><br>
        <label for="benchmarks">Select benchmark tickers:</label><br>
        <input type="text" name="benchmarks" id="benchmarks" value='{', '.join(benchmark)}' /><br><br>
        <label for='lookback'>The past number of trading days for the analysis</label><br>
            <input type='number' name='lookback' id='lookback' placeholder='Enter number of days' value='{settings.lookback}'/><br><br>
            <label for='extrapolate'>Extrapolate results by the following number of days</label><br>
            <input type='number' name='extrapolate' id='extrapolate' placeholder='Enter number of days' value='{settings.extrapolate}'/><br><br>
            <label for='rfr'>Risk free rate</label><br>
            <input type='number' name='rfr' id='rfr' placeholder='Enter the risk free rate' value='{settings.rfr}' min='0' max='1' step ='0.01'/><br><br>
            <!-- Add an input field for the datepicker -->
            <!--<label for="datepicker">Date of last rebalance</label><br>-->
            <!--<input type="text" id="datepicker" name="rebalance">-->
            <div id='error-msg'></div>
            <button type='submit' id='submit-btn' class='btn btn-primary'>Submit</button>
        </form></div>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@yaireo/tagify/dist/tagify.min.js"></script>
      <script>
        // Initialize Tagify
        var input = document.querySelector('input[name="tickers"]');
        var whitelist = {current_app.available_tickers_json};
        var tickers = new Tagify(input, {{
            enforceWhitelist : true,
            whitelist: whitelist,
            blacklist: [""],
            duplicates: false,
            dropdown: {{
                enabled: 1,
                showOnEmpty: true,
                autocomplete: {{
                  firstFocus: true
                }}
            }}
        }});

          // Initialize Tagify
        var input = document.querySelector('input[name="benchmarks"]');
        var whitelist = {current_app.available_tickers_json};
        var benchmarks = new Tagify(input, {{
            enforceWhitelist : true,
            whitelist: whitelist,
            blacklist: [""],
            duplicates: false,
            dropdown: {{
                enabled: 1,
                showOnEmpty: true,
                autocomplete: {{
                  firstFocus: true
                }}
            }}
        }});
    
        // add an event listener for form submission
        var form = document.getElementById('sidebarform');
        var submitBtn = document.getElementById('submit-btn');
        submitBtn.addEventListener('click', function(event) {{
            // check the number of tags
            if (tickers.value.length < 2) {{
                // prevent the default form submission behavior
                event.preventDefault();
    
                // show an error message
                var errorDiv = document.getElementById('error-msg');
                errorDiv.innerText = 'Please select at least two ticker symbols.';
            }}
    
            // check if lookback is a non-negative integer
            var lookbackInput = document.getElementById('lookback');
            var lookbackValue = parseInt(lookbackInput.value);
            if (isNaN(lookbackValue) || lookbackValue < 1) {{
                event.preventDefault();
                var errorDiv = document.getElementById('error-msg');
                errorDiv.innerText = 'Please enter a non-negative integer for the number of days.';
            }}
    
            // check if extrapolate is a non-negative integer
            var extrapolateInput = document.getElementById('extrapolate');
            var extrapolateValue = parseInt(extrapolateInput.value);
            if (isNaN(extrapolateValue) || extrapolateValue < 1) {{
                event.preventDefault();
                var errorDiv = document.getElementById('error-msg');
                errorDiv.innerText = 'Please enter a non-negative integer for the extrapolation.';
            }}

            // check if extrapolate is a non-negative integer
            var rfrInput = document.getElementById('rfr');
            var rfrValue = parseInt(rfrInput.value);
            if (isNaN(rfrValue) || rfrValue < 0 || rfrValue > 1) {{
                event.preventDefault();
                var errorDiv = document.getElementById('error-msg');
                errorDiv.innerText = 'The risk-free-rate should be between 0 and 1.';
            }}

            }});
    </script>

    
<script>
// Get the input element
const inputElement = document.getElementById("tickers");
console.log(inputElement);

// Add event listeners to the two buttons
const button0 = document.getElementById("button0");
const button1 = document.getElementById("button1");
const button2 = document.getElementById("button2");

button0.addEventListener("click", function(event) {{
  event.preventDefault(); // prevent default form submit behavior
  inputElement.value = [];
}});

button1.addEventListener("click", function(event) {{
  event.preventDefault(); // prevent default form submit behavior
  const list1 = inputElement.value ? JSON.parse(inputElement.value) : []; // parse the JSON string if it's not empty, otherwise use an empty array
  const list1Values = list1.map(item => item.value); // extract the value property of each object
  const list2 = {current_app.tickers_c20}; // assuming this is an array of tickers
  const resultValue = list1Values.concat(list2).join(", "); // join the two lists
  inputElement.value = resultValue;
}});

button2.addEventListener("click", function(event) {{
  event.preventDefault(); // prevent default form submit behavior
  const list1 = inputElement.value ? JSON.parse(inputElement.value) : []; // parse the JSON string if it's not empty, otherwise use an empty array
  const list1Values = list1.map(item => item.value); // extract the value property of each object
  const list2 = {current_app.tickers_dji}; // assuming this is an array of tickers
  const resultValue = list1Values.concat(list2).join(", "); // join the two lists
  inputElement.value = resultValue;
}});
</script>
    """
