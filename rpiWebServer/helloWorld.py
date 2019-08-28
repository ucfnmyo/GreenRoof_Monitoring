from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'
    

@app.route('/postmethod', methods = ['POST'])
def post_javascript_data():
    jsdata = request.form['canvas_data']
    unique_id = create_csv(jsdata)
    params = { 'uuid' : unique_id }
    return jsonify(params)

if __name__ == '__main__':
    app.run(debug=True, port=81, host='192.168.0.40')
