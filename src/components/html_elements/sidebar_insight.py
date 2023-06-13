from flask import current_app


class sidebarInsights:
    def __init__(self, settings):
        self.html = f"<div id='sidebardiv'><form method='GET' action='/insight' id='sidebarform'>"
        self.html += f"<label for='tickers'>Tickers</label><br><span class='ticker'>Ticker</span><span class='weight'>Weight</span><br>"
        for i, ticker in enumerate(settings.tickers):
            self.html += f"<input type='text' id='tickers{str(i)}' name='tickers' class='ticker' value='{ticker[0]}' readonly><input type='number' step='0.01' min='0.0' max='1.0' class='weight' id='weight{str(i)}' value='{ticker[1]}'><br>"
        self.html += f"<label for='benchmarks'>Benchmarks</label><br><span class='ticker'>Ticker</span><span class='weight'>Weight</span><br>" if settings.benchmarks is not None else ""
        if settings.benchmarks is not None:
            for i, benchmark in enumerate(settings.benchmarks):
                self.html += f"<input type='text' id='benchmarks{str(i)}' name='benchmarks' class='ticker' value='{benchmark[0]}' readonly><input type='number' step='0.01' min='0.0' max='1.0' class='weight' id='benchweight{str(i)}' value='{benchmark[1]}'><br>"
        self.html += f"""<br><label for='lookback'>The past number of trading days for the analysis</label><br>
            <input type='number' name='lookback' id='lookback' placeholder='Enter number of days' value='{settings.lookback}'/><br><br>
            <label for='extrapolate'>Extrapolate results by the following number of days</label><br>
            <input type='number' name='extrapolate' id='extrapolate' placeholder='Enter number of days' value='{settings.extrapolate}'/><br><br>
            <label for='rfr'>Risk free rate</label><br>
            <input type='number' name='rfr' id='rfr' placeholder='Enter the risk free rate' value='{settings.rfr}' min='0' max='1' step ='0.01'/><br><br>
            <label for='capacity'>Maximum Portfolio value</label><br>
            <input type='number' name='capacity' id='capacity' placeholder='Amount of funds to invest' value='{settings.capacity}' min='0'/><br><br>
            <!-- Add an input field for the datepicker -->
            <!--<label for="datepicker">Date of last rebalance</label><br>-->
            <!--<input type="text" id="datepicker" name="rebalance">-->
            <div id='error-msg'></div>
            <button type='submit' id='submit-btn'>Submit</button>
        </form></div>"""
        self.html += f"""<script>
            const form = document.querySelector('#sidebarform');
            const tickersInput = document.querySelector('#tickers0');
            const benchmarksInput = document.querySelector('#benchmarks0');"""
        for i, ticker in enumerate(settings.tickers):
            self.html += f"""const weight{str(i)}Input = document.querySelector('#weight{str(i)}');
            """
        if settings.benchmarks is not None:
            for i, ticker in enumerate(settings.benchmarks):
                self.html += f"""const benchweight{str(i)}Input = document.querySelector('#benchweight{str(i)}');
                """
        self.html += f"""form.addEventListener('submit', (event) => {{
            event.preventDefault();
                // Update tickers input value with weights
        const tickers = ["""
        for i, ticker in enumerate(settings.tickers):
            self.html += (
                f"{{ value: '{ticker[0]}', weight: weight{str(i)}Input.value }},"
            )
        self.html += f"]"

        if settings.benchmarks is not None:
            self.html+=f"const benchmarks = ["
            for i, benchmark in enumerate(settings.benchmarks):
                self.html += (
                    f"{{ value: '{benchmark[0]}', weight: benchweight{str(i)}Input.value }},"
                )
            self.html += f"]"

        benchmarks = f"&benchmarks=${{encodeURIComponent(benchmarksInput.value)}}" if settings.benchmarks is not None else ""
        self.html += f"""
        tickersInput.value = JSON.stringify(tickers);
        {f"benchmarksInput.value = JSON.stringify(benchmarks)" if settings.benchmarks is not None else ""};
            // Update form action URL
        const lookbackInput = document.querySelector('#lookback');
        const capacityInput = document.querySelector('#capacity');
        const extrapolateInput = document.querySelector('#extrapolate');
        const rfrInput = document.querySelector('#rfr');
        const url = `/insight?tickers=${{encodeURIComponent(tickersInput.value)}}{benchmarks}&lookback=${{lookbackInput.value}}&extrapolate=${{extrapolateInput.value}}&rfr=${{rfrInput.value}}&rfr=${{capacityInput.value}}`;
        console.log(url);
        form.action = url;

        // Submit the form
        form.submit();
    }});
    </script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
    

    """
