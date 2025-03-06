import requests
from openai import OpenAI
from flask import Flask, request, render_template_string, redirect, url_for

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = "Q1G2DLMT5THOX3OD"

# OpenAI API key
OPENAI_API_KEY = "YOUR API KEY"
# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# In-memory storage for search history
search_history = []

# Function to fetch stock price
def get_stock_price(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    # Check if the response contains the expected data
    if "Time Series (5min)" not in data:
        return None  # Handle invalid symbol or API error
    
    latest_time = list(data["Time Series (5min)"].keys())[0]
    latest_price = data["Time Series (5min)"][latest_time]["1. open"]
    return latest_price

# Function to get GPT-4 advice
def get_gpt4_advice(stock_symbol, stock_price):
    prompt = f"The current price of {stock_symbol} is {stock_price}. Should I invest in this stock? Provide a brief explanation."
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Home Page (Stock Search)
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        symbol = request.form["symbol"].upper()
        price = get_stock_price(symbol)
        
        if price is None:
            result = {"error": "Invalid stock symbol or API error. Please try again."}
        else:
            advice = get_gpt4_advice(symbol, price)
            # Save search history
            search_history.append({"symbol": symbol, "price": price, "advice": advice})
            result = {"symbol": symbol, "price": price, "advice": advice}

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Stock Advisor</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background-color: #f8f9fa;
                }
                .container {
                    margin-top: 50px;
                }
                .form-container {
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                .btn-primary {
                    background-color: #007bff;
                    border-color: #007bff;
                }
                .btn-primary:hover {
                    background-color: #0056b3;
                    border-color: #0056b3;
                }
                .result-container {
                    margin-top: 20px;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6 form-container">
                        <h1 class="text-center">Stock Advisor</h1>
                        <form method="POST">
                            <div class="mb-3">
                                <label for="symbol" class="form-label">Enter Stock Symbol:</label>
                                <input type="text" class="form-control" id="symbol" name="symbol" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Get Advice</button>
                        </form>
                        <a href="/history" class="btn btn-secondary w-100 mt-2">View Search History</a>
                    </div>
                </div>
                {% if result %}
                <div class="row justify-content-center mt-4">
                    <div class="col-md-6 result-container">
                        {% if result.error %}
                        <div class="alert alert-danger" role="alert">
                            {{ result.error }}
                        </div>
                        {% else %}
                        <h3>Advice for {{ result.symbol }}</h3>
                        <p><strong>Current Price:</strong> {{ result.price }}</p>
                        <p><strong>Advice:</strong> {{ result.advice }}</p>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
            </div>
        </body>
        </html>
    """, result=result)

# Search History Page
@app.route("/history")
def history():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Search History</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background-color: #f8f9fa;
                }
                .container {
                    margin-top: 50px;
                }
                .history-container {
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-8 history-container">
                        <h1 class="text-center">Search History</h1>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Price</th>
                                    <th>Advice</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for search in search_history %}
                                <tr>
                                    <td>{{ search.symbol }}</td>
                                    <td>{{ search.price }}</td>
                                    <td>{{ search.advice }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                        <a href="/" class="btn btn-primary w-100">Back to Home</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """, search_history=search_history)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
