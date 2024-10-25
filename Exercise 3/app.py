import pymongo
from flask import Flask, render_template, jsonify
import logging
from filter_views import create_views_with_filters
from aggregation_views import create_aggregation_views


app = Flask(__name__)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["myanimelist_db"]
# Create filter and aggregation views
create_views_with_filters(db)
# Krijo agregimet (views) me pipeline përkatëse
create_aggregation_views(db)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anime/<view_name>')
def get_anime_data(view_name):
    try:
        anime_list = list(db[view_name].find({}, {'_id': 0}))  # Exclude the _id field from the result
        return jsonify(anime_list)
    except Exception as e:
        logging.error(f"Error fetching data for view '{view_name}': {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/view/<view_name>')
def render_table_view(view_name):
    # Mapping view names to their corresponding template files and human-readable titles
    view_map = {
        'high_score_anime': 'high_score_anime.html',
        'action_anime': 'action_anime.html',
        'long_series': 'long_series.html',
        'recent_anime': 'recent_anime.html',
        'popular_anime': 'popular_anime.html',
        'average_score_anime': 'average_score_anime.html',
        'average_score_per_genre': 'average_score_per_genre.html',
        'total_anime_per_studio': 'total_anime_per_studio.html',
        'top_10_highest_rated_anime': 'top_10_highest_rated_anime.html',
        'total_episodes_per_studio': 'total_episodes_per_studio.html',
        'top_10_most_popular_anime': 'top_10_most_popular_anime.html',
        'count_anime_by_type': 'count_anime_by_type.html'
    }

    # Get the template file name and title for the given view name
    template_file = view_map.get(view_name)
    view_title = {
        'high_score_anime': 'High Score Anime',
        'action_anime': 'Action Anime',
        'long_series': 'Long Series Anime',
        'recent_anime': 'Recent Anime',
        'popular_anime': 'Popular Anime',
        'average_score_anime': 'Average Score Anime',
        'average_score_per_genre': 'Average Score per Genre',
        'total_anime_per_studio': 'Total Anime per Studio',
        'top_10_highest_rated_anime': 'Top 10 Highest Rated Anime',
        'total_episodes_per_studio': 'Total Episodes per Studio',
        'top_10_most_popular_anime': 'Top 10 Most Popular Anime',
        'count_anime_by_type': 'Total number for each type'
    }.get(view_name, "Anime View")

    if template_file:
        return render_template(template_file, view_name=view_name, view_title=view_title)
    else:
        return "View not found", 404  # Return a 404 error if the view doesn't exist
    
if __name__ == '__main__':
    app.run(debug=True)
