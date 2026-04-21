"""
Smart Restaurant Recommender - Flask Web Application
Modern web-based frontend with beautiful UI
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_loader import RestaurantDataLoader
from src.recommender import RestaurantRecommender, RecommendationParams

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load data
try:
    data_path = Path(__file__).parent / "data" / "restaurants.csv"
    loader = RestaurantDataLoader(str(data_path))
    data = loader.get_data()
    recommender = RestaurantRecommender(data)
    all_cuisines = loader.get_unique_cuisines()
    min_budget, max_budget, _, _ = loader.get_budget_statistics()
    dataset_summary = loader.get_data_summary()
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/cuisines', methods=['GET'])
def get_cuisines():
    """Get list of all available cuisines."""
    return jsonify({
        'cuisines': all_cuisines
    })


@app.route('/api/budget-range', methods=['GET'])
def get_budget_range():
    """Get budget range statistics."""
    return jsonify({
        'min': float(min_budget),
        'max': float(max_budget)
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dataset statistics."""
    return jsonify(dataset_summary)


@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """Get restaurant recommendations based on filters."""
    try:
        request_data = request.json
        
        selected_cuisines = request_data.get('cuisines', [])
        min_budget_filter = float(request_data.get('minBudget', 0))
        max_budget_filter = float(request_data.get('maxBudget', max_budget))
        min_rating = float(request_data.get('minRating', 0))
        max_results = int(request_data.get('maxResults', 20))
        
        # Validate inputs
        if not selected_cuisines:
            return jsonify({
                'error': 'Please select at least one cuisine',
                'restaurants': []
            }), 400
        
        # Get recommendations
        params = RecommendationParams(
            selected_cuisines=selected_cuisines,
            min_budget=min_budget_filter,
            max_budget=max_budget_filter,
            min_rating=min_rating,
            max_results=max_results
        )
        
        recommendations = recommender.get_recommendations(params)
        
        # Format results
        restaurants = []
        for idx, (_, rest) in enumerate(recommendations.iterrows(), 1):
            restaurant = {
                'id': idx,
                'name': rest['Restaurant Name'],
                'city': rest['City'],
                'address': rest.get('Address', 'N/A'),
                'cuisines': rest['Cuisine List'],
                'rating': float(rest['Aggregate rating']) if rest['Aggregate rating'] > 0 else 0,
                'cost': float(rest['Average Cost for two']) if rest['Average Cost for two'] > 0 else 0,
                'currency': rest.get('Currency', ''),
                'votes': int(rest.get('Votes', 0)),
                'tableBooking': rest.get('Has Table booking', 'No') == 'Yes',
                'onlineDelivery': rest.get('Has Online delivery', 'No') == 'Yes',
            }
            restaurants.append(restaurant)
        
        return jsonify({
            'success': True,
            'count': len(restaurants),
            'restaurants': restaurants
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'restaurants': []
        }), 500


@app.route('/api/search', methods=['POST'])
def search_restaurants():
    """Quick search for restaurants by name or cuisine."""
    try:
        query = request.json.get('query', '')
        limit = request.json.get('limit', 10)
        
        if not query or len(query) < 2:
            return jsonify({'restaurants': []})
        
        results = recommender.get_quick_search(query, limit)
        
        restaurants = []
        for idx, (_, rest) in enumerate(results.iterrows(), 1):
            restaurant = {
                'id': idx,
                'name': rest['Restaurant Name'],
                'city': rest['City'],
                'cuisines': rest['Cuisine List'],
                'rating': float(rest['Aggregate rating']) if rest['Aggregate rating'] > 0 else 0,
                'cost': float(rest['Average Cost for two']) if rest['Average Cost for two'] > 0 else 0,
            }
            restaurants.append(restaurant)
        
        return jsonify({'restaurants': restaurants})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export_data():
    """Export recommendations as CSV."""
    try:
        request_data = request.json
        restaurants = request_data.get('restaurants', [])
        
        if not restaurants:
            return jsonify({'error': 'No restaurants to export'}), 400
        
        # Create CSV content
        csv_content = "Restaurant Name,City,Address,Cuisines,Rating,Cost,Currency\n"
        
        for rest in restaurants:
            cuisines = ', '.join(rest['cuisines'])
            csv_content += f'"{rest["name"]}","{rest["city"]}","{rest["address"]}","{cuisines}",{rest["rating"]},{rest["cost"]},"{rest["currency"]}"\n'
        
        return jsonify({
            'success': True,
            'csv': csv_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🍽️  Smart Restaurant Recommender")
    print("="*60)
    print("\n✅ Application starting...")
    print("🌐 Open your browser at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, port=5000, use_reloader=False)
