from flask import Flask, render_template, request, url_for, redirect, jsonify
from functools import wraps
import requests
import pymongo
from razorpay import Client as RazorpayClient

app = Flask(__name__)

app.secret_key = "b'\x04S\x08\xbc\x07\xb8\xa9Y\x82T\xbfx\xcb\x97o^'"

client = pymongo.MongoClient('localhost', 27017)
db = client.medins

# API endpoint for GET request
@app.route('/api/example', methods=['GET'])
def get_example():
    # Define the logic for your API function
    data = {
        'message': 'This is a GET request example!'
    }
    # Return the data as JSON response
    return jsonify(data)

output = []  # Assuming output is defined somewhere in your code

@app.route('/result', methods=["POST"])
def result():
    if request.method == "POST":
        user_message = request.json['message']

        try:
            rasa_response = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"message": user_message})
            rasa_response_data = rasa_response.json()[0]

            # Print the entire response for debugging
            print('Rasa Response Data:', rasa_response_data)

            bot_message = rasa_response_data.get('text', '')
            buttons = rasa_response_data.get('buttons', [])

            # Append user message, bot response, and buttons to output
            output.extend([("user", user_message), ("bot", bot_message)])

            # Check if 'buttons' key is present in the response data
            if 'buttons' in rasa_response_data:
                output.append(("buttons", buttons))

            # Return bot response and buttons to the client
            return jsonify({'bot_response': bot_message, 'buttons': buttons})
        except Exception as e:
            print(f"Error: {e}")
            output.extend([("user", user_message), ("bot", "We are unable to process your request at the moment. Please try again...")])

        print(output)
        return jsonify({'bot_response': "Sorry I dont understand.."})

@app.route('/')
def home():
    return render_template("chat.html", result=output)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")


# Initialize Razorpay client with your API key and secret
razorpay_client = RazorpayClient(auth=("rzp_test_mscBObbyZL9Nw3", "2orY51UhB4137gcUhKY3u9F3"))
@app.route("/create_order", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        amount = data.get('amount')

        # Create order using Razorpay
        order_data = {
            'amount': 7378,
            'currency': "INR",
            'receipt': "receipt_001",
            'payment_capture': 1  # Automatically capture payment
        }
        order = razorpay_client.order.create(data=order_data)

        return jsonify(order)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
