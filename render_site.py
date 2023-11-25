# Import necessary libraries
from flask import Flask, render_template, request
import sqlite3

# Initialize Flask app
app = Flask(__name__)


# Function to query the database for videos containing specified keywords
def query_videos(keywords):
    conn = sqlite3.connect('video_data.db')
    cursor = conn.cursor()
    query = "SELECT * FROM video_data WHERE title LIKE ?"
    cursor.execute(query, ('%' + keywords + '%',))
    results = cursor.fetchall()
    conn.close()
    return results


# Function to get video duration by category
def get_video_duration_by_category():
    conn = sqlite3.connect('video_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category_name, SUM(duration_seconds) FROM video_data GROUP BY category_name')
    data = cursor.fetchall()
    conn.close()
    return data

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to display videos with specific keywords
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        # Handle form submission, perform search, and redirect to results
        keywords = request.form.get('keywords', '')
        return query_db_and_redirect(keywords)
    return render_template('search.html')

# Route to display videos with specific keywords
@app.route('/search_results', methods=['GET'])
def search_results():
    keywords = request.args.get('keywords', '')
    if not keywords:
        return render_template('search_results.html', keywords=keywords, results=[])
    results = query_videos(keywords)
    return render_template('search_results.html', keywords=keywords, results=results)



# Route to display video duration by category
@app.route('/duration_by_category')
def duration_by_category():
    data = get_video_duration_by_category()
    return render_template('duration_by_category.html', data=data)


# Helper function to handle search and redirection
def query_db_and_redirect(keywords):
    results = query_videos(keywords)
    return render_template('search_results.html', keywords=keywords, results=results)


if __name__ == '__main__':
    app.run(debug=True)
