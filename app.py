"""
Streamlit application for the Smart Restaurant Recommender system.

This module provides an interactive web-based user interface for discovering
and getting personalized restaurant recommendations based on cuisine preferences
and budget constraints.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_loader import RestaurantDataLoader
from src.recommender import RestaurantRecommender, RecommendationParams
from src.utils import (
    format_currency,
    get_rating_emoji,
    get_rating_text,
    extract_currency_code
)


# Page configuration
st.set_page_config(
    page_title="Smart Restaurant Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .restaurant-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
        background-color: #f8f9fa;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    
    .restaurant-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .rating-badge {
        background-color: #FFD93D;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    
    .cuisine-badge {
        background-color: #6BCB77;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.85em;
        margin-right: 5px;
        display: inline-block;
    }
    
    .cost-badge {
        background-color: #4D96FF;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.85em;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_data():
    """Load and cache restaurant data."""
    data_path = Path(__file__).parent / "data" / "restaurants.csv"
    
    if not data_path.exists():
        st.error(f"❌ Dataset not found at {data_path}")
        st.info("📝 Please copy 'Dataset .csv' to the 'data' folder")
        st.stop()
    
    try:
        loader = RestaurantDataLoader(str(data_path))
        return loader.get_data(), loader
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()


def display_restaurant_card(restaurant: pd.Series, index: int) -> None:
    """
    Display a restaurant as a styled card.
    
    Args:
        restaurant: Restaurant data (pandas Series)
        index: Index for unique key
    """
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### {index + 1}. {restaurant['Restaurant Name']}")
        st.markdown(f"📍 **Location:** {restaurant['City']}")
        if pd.notna(restaurant['Address']) and restaurant['Address']:
            st.markdown(f"🏘️ **Address:** {restaurant['Address']}")
    
    with col2:
        if restaurant['Aggregate rating'] > 0:
            rating = restaurant['Aggregate rating']
            st.markdown(f"<div class='rating-badge'>{rating:.1f}/5.0</div>", unsafe_allow_html=True)
            st.caption(f"{get_rating_emoji(rating)}")
            st.caption(f"{get_rating_text(rating)}")
        else:
            st.caption("⚪ Not yet rated")
    
    with col3:
        cost = restaurant['Average Cost for two']
        currency = restaurant.get('Currency', 'N/A')
        if cost > 0:
            st.markdown(f"<div class='cost-badge'>{format_currency(cost, currency)}</div>", unsafe_allow_html=True)
        else:
            st.caption("💰 Price not available")
    
    # Cuisines
    st.markdown("**Cuisines:**")
    cuisines_html = " ".join([
        f"<span class='cuisine-badge'>{cuisine}</span>"
        for cuisine in restaurant['Cuisine List']
    ])
    st.markdown(cuisines_html, unsafe_allow_html=True)
    
    # Additional info
    col_a, col_b = st.columns(2)
    with col_a:
        if 'Votes' in restaurant and restaurant['Votes'] > 0:
            st.caption(f"👥 {int(restaurant['Votes'])} reviews")
    
    with col_b:
        features = []
        if pd.notna(restaurant.get('Has Table booking')) and restaurant.get('Has Table booking') == 'Yes':
            features.append("📕 Table Booking")
        if pd.notna(restaurant.get('Has Online delivery')) and restaurant.get('Has Online delivery') == 'Yes':
            features.append("🛵 Online Delivery")
        
        if features:
            st.caption(" | ".join(features))
    
    st.divider()


def main():
    """Main Streamlit application."""
    # Header
    st.title("🍽️ Smart Restaurant Recommender")
    st.markdown("Find the perfect restaurant based on your cuisine preferences and budget!")
    
    # Load data
    data, loader = load_data()
    recommender = RestaurantRecommender(data)
    
    # Sidebar - Filters
    with st.sidebar:
        st.header("⚙️ Preferences")
        
        # Get available cuisines
        available_cuisines = loader.get_unique_cuisines()
        
        # Cuisine selection
        selected_cuisines = st.multiselect(
            "🍜 Select Cuisines",
            available_cuisines,
            help="Choose one or more cuisine types"
        )
        
        # Budget range
        min_budget, max_budget, _, _ = loader.get_budget_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            min_budget_filter = st.number_input(
                "💰 Min Budget",
                min_value=0.0,
                value=min_budget,
                step=100.0
            )
        
        with col2:
            max_budget_filter = st.number_input(
                "💰 Max Budget",
                min_value=0.0,
                value=max_budget * 0.5,
                step=100.0
            )
        
        # Rating filter
        min_rating = st.slider(
            "⭐ Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5,
            help="Filter restaurants by minimum rating"
        )
        
        # Max results
        max_results = st.slider(
            "📊 Show up to",
            min_value=1,
            max_value=50,
            value=10
        )
        
        st.divider()
        st.subheader("📈 Dataset Info")
        summary = loader.get_data_summary()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Restaurants", f"{summary['total_restaurants']:,}")
            st.metric("Cuisines", f"{summary['unique_cuisines']}")
        with col2:
            st.metric("Cities", f"{summary['unique_cities']}")
            st.metric("Avg Rating", f"{summary['avg_rating']:.1f}/5")
    
    # Main content area
    if not selected_cuisines:
        st.info("👈 Please select at least one cuisine from the sidebar to get started!")
        
        # Show some insights
        st.divider()
        st.subheader("🌟 Popular Cuisines")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Top Rated")
            top_rated = recommender.get_top_rated(limit=5)
            for i, rest in top_rated.iterrows():
                st.markdown(f"**{rest['Restaurant Name']}** ⭐ {rest['Aggregate rating']:.1f}")
        
        with col2:
            st.subheader("Budget Friendly")
            budget_friendly = recommender.get_budget_friendly(limit=5)
            for i, rest in budget_friendly.iterrows():
                st.markdown(f"**{rest['Restaurant Name']}** 💰 {format_currency(rest['Average Cost for two'], rest['Currency'])}")
        
        with col3:
            st.subheader("Most Reviewed")
            most_reviewed = data.nlargest(5, 'Votes')
            for i, rest in most_reviewed.iterrows():
                st.markdown(f"**{rest['Restaurant Name']}** 👥 {int(rest['Votes'])} reviews")
    
    else:
        # Get recommendations
        params = RecommendationParams(
            selected_cuisines=selected_cuisines,
            min_budget=min_budget_filter,
            max_budget=max_budget_filter,
            min_rating=min_rating,
            max_results=max_results
        )
        
        recommendations = recommender.get_recommendations(params)
        
        # Display results
        if len(recommendations) == 0:
            st.warning("❌ No restaurants found matching your criteria. Try adjusting your filters!")
            
            # Suggest alternatives
            st.info("💡 Try expanding your budget range or selecting different cuisines")
        
        else:
            # Header with result count
            st.success(f"✅ Found {len(recommendations)} restaurant(s) matching your preferences!")
            
            # Display statistics
            with st.expander("📊 See Stats for Selected Cuisines"):
                stats = recommender.get_statistics(None)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    filtered_data = data[
                        data['Cuisine List'].apply(
                            lambda c: any(
                                any(sc.lower() in x.lower() for x in c) 
                                for sc in selected_cuisines
                            )
                        )
                    ]
                    st.metric("Matching Restaurants", len(filtered_data))
                
                with col2:
                    avg_rating = filtered_data[filtered_data['Aggregate rating'] > 0]['Aggregate rating'].mean()
                    st.metric("Avg Rating", f"{avg_rating:.1f}/5" if not pd.isna(avg_rating) else "N/A")
                
                with col3:
                    avg_cost = filtered_data[filtered_data['Average Cost for two'] > 0]['Average Cost for two'].mean()
                    st.metric("Avg Cost", f"₽{avg_cost:,.0f}" if not pd.isna(avg_cost) else "N/A")
                
                with col4:
                    total_votes = filtered_data['Votes'].sum()
                    st.metric("Total Reviews", f"{int(total_votes):,}")
            
            st.divider()
            
            # Display restaurant cards
            st.subheader(f"🏆 Top Recommendations")
            
            for idx, (_, restaurant) in enumerate(recommendations.iterrows()):
                display_restaurant_card(restaurant, idx)
            
            # Export option
            st.divider()
            
            if st.button("📥 Export Results as CSV"):
                csv = recommendations[[
                    'Restaurant Name', 'City', 'Address', 'Cuisines',
                    'Average Cost for two', 'Aggregate rating', 'Currency'
                ]].to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="recommendations.csv",
                    mime="text/csv"
                )


if __name__ == "__main__":
    main()
