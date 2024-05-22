from flask import Flask, render_template, request
from rest_apis import get_book_info_rest
from soap_apis import get_book_info_soap

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    search_type = request.form.get('search_type')
    
    rest_results = get_book_info_rest(query, search_type)
    soap_results = get_book_info_soap(query, search_type)
    
    results = {
        'REST': rest_results,
        'SOAP': soap_results
    }
    
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
