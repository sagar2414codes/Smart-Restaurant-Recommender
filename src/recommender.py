"""
Core recommendation engine for the Smart Restaurant Recommender system.

This module implements the recommendation algorithm that filters and ranks
restaurants based on user preferences for cuisine and budget.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RecommendationParams:
    """
    Parameters for restaurant recommendation.
    
    Attributes:
        selected_cuisines: List of cuisine types to filter by
        min_budget: Minimum budget constraint
        max_budget: Maximum budget constraint
        min_rating: Minimum rating threshold
        max_results: Maximum number of results to return
    """
    selected_cuisines: List[str]
    min_budget: float
    max_budget: float
    min_rating: float = 0.0
    max_results: int = 50


class RestaurantRecommender:
    """
    Main recommendation engine for suggesting restaurants.
    
    This engine applies multiple filtering and ranking strategies to
    provide personalized restaurant recommendations based on user preferences.
    
    Attributes:
        data: DataFrame containing restaurant information
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the recommender with restaurant data.
        
        Args:
            data: DataFrame containing restaurant information with
                  'Cuisine List', 'Average Cost for two', 'Aggregate rating' columns
        """
        self.data = data.copy()
        self._validate_data()
    
    def _validate_data(self) -> None:
        """Validate that the required columns are present in the data."""
        required_columns = ['Cuisine List', 'Average Cost for two', 'Aggregate rating']
        missing = [col for col in required_columns if col not in self.data.columns]
        
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    def get_recommendations(self, params: RecommendationParams) -> pd.DataFrame:
        """
        Get restaurant recommendations based on specified parameters.
        
        Args:
            params: RecommendationParams object containing filtering criteria
            
        Returns:
            DataFrame of recommended restaurants sorted by rating (descending)
        """
        # Step 1: Filter by cuisine
        cuisine_filtered = self._filter_by_cuisine(params.selected_cuisines)
        
        if len(cuisine_filtered) == 0:
            return pd.DataFrame()
        
        # Step 2: Filter by budget
        budget_filtered = self._filter_by_budget(
            cuisine_filtered,
            params.min_budget,
            params.max_budget
        )
        
        if len(budget_filtered) == 0:
            return pd.DataFrame()
        
        # Step 3: Filter by minimum rating
        rating_filtered = self._filter_by_rating(budget_filtered, params.min_rating)
        
        # Step 4: Rank results
        ranked = self._rank_recommendations(rating_filtered)
        
        # Step 5: Limit results
        return ranked.head(params.max_results).reset_index(drop=True)
    
    def _filter_by_cuisine(self, selected_cuisines: List[str]) -> pd.DataFrame:
        """
        Filter restaurants that offer at least one of the selected cuisines.
        
        Args:
            selected_cuisines: List of cuisines to filter by
            
        Returns:
            Filtered DataFrame
        """
        if not selected_cuisines:
            return self.data.copy()
        
        # Create a boolean mask for restaurants with matching cuisines
        mask = self.data['Cuisine List'].apply(
            lambda cuisine_list: self._has_matching_cuisine(
                cuisine_list,
                selected_cuisines
            )
        )
        
        return self.data[mask].copy()
    
    @staticmethod
    def _has_matching_cuisine(
        restaurant_cuisines: List[str],
        selected_cuisines: List[str]
    ) -> bool:
        """
        Check if a restaurant offers at least one of the selected cuisines.
        
        Args:
            restaurant_cuisines: List of cuisines offered by the restaurant
            selected_cuisines: List of selected cuisines to match
            
        Returns:
            True if there's at least one matching cuisine
        """
        if not restaurant_cuisines or not selected_cuisines:
            return False
        
        # Case-insensitive comparison
        restaurant_set = {c.lower() for c in restaurant_cuisines}
        selected_set = {c.lower() for c in selected_cuisines}
        
        return bool(restaurant_set & selected_set)
    
    @staticmethod
    def _filter_by_budget(
        data: pd.DataFrame,
        min_budget: float,
        max_budget: float
    ) -> pd.DataFrame:
        """
        Filter restaurants within the specified budget range.
        
        Args:
            data: Input DataFrame
            min_budget: Minimum budget
            max_budget: Maximum budget
            
        Returns:
            Filtered DataFrame
        """
        cost_column = data['Average Cost for two']
        
        # Handle cases where cost is 0 (missing data)
        mask = (cost_column >= min_budget) & (cost_column <= max_budget)
        
        return data[mask].copy()
    
    @staticmethod
    def _filter_by_rating(data: pd.DataFrame, min_rating: float) -> pd.DataFrame:
        """
        Filter restaurants with minimum rating threshold.
        
        Args:
            data: Input DataFrame
            min_rating: Minimum rating threshold
            
        Returns:
            Filtered DataFrame
        """
        # Include restaurants with no rating (0) if min_rating is 0
        if min_rating == 0:
            mask = data['Aggregate rating'] >= min_rating
        else:
            # Exclude unrated restaurants if min_rating > 0
            mask = (data['Aggregate rating'] >= min_rating) & (data['Aggregate rating'] > 0)
        
        return data[mask].copy()
    
    @staticmethod
    def _rank_recommendations(data: pd.DataFrame) -> pd.DataFrame:
        """
        Rank recommendations by rating and votes.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Sorted DataFrame
        """
        # Sort by: rating (descending), votes (descending), name (ascending)
        return data.sort_values(
            by=['Aggregate rating', 'Votes', 'Restaurant Name'],
            ascending=[False, False, True]
        )
    
    def get_quick_search(
        self,
        query: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Quick search restaurants by name or cuisine.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            DataFrame of matching restaurants
        """
        query_lower = query.lower()
        
        # Search in restaurant names
        name_match = self.data['Restaurant Name'].str.lower().str.contains(
            query_lower,
            na=False
        )
        
        # Search in cuisines
        cuisine_match = self.data['Cuisine List'].apply(
            lambda cuisines: any(query_lower in c.lower() for c in cuisines)
        )
        
        # Combine results
        results = self.data[name_match | cuisine_match]
        
        # Rank by rating
        results = results.sort_values('Aggregate rating', ascending=False)
        
        return results.head(limit).reset_index(drop=True)
    
    def get_top_rated(
        self,
        cuisine: Optional[str] = None,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Get top-rated restaurants, optionally filtered by cuisine.
        
        Args:
            cuisine: Optional cuisine filter
            limit: Maximum number of results
            
        Returns:
            DataFrame of top-rated restaurants
        """
        # Filter by cuisine if specified
        if cuisine:
            data = self.data[
                self.data['Cuisine List'].apply(
                    lambda c: any(cuisine.lower() in x.lower() for x in c)
                )
            ]
        else:
            data = self.data.copy()
        
        # Filter out unrated restaurants
        data = data[data['Aggregate rating'] > 0]
        
        # Sort by rating
        data = data.sort_values('Aggregate rating', ascending=False)
        
        return data.head(limit).reset_index(drop=True)
    
    def get_budget_friendly(
        self,
        cuisine: Optional[str] = None,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Get budget-friendly restaurants, optionally filtered by cuisine.
        
        Args:
            cuisine: Optional cuisine filter
            limit: Maximum number of results
            
        Returns:
            DataFrame of budget-friendly restaurants
        """
        # Filter by cuisine if specified
        if cuisine:
            data = self.data[
                self.data['Cuisine List'].apply(
                    lambda c: any(cuisine.lower() in x.lower() for x in c)
                )
            ]
        else:
            data = self.data.copy()
        
        # Filter out restaurants with no cost information
        data = data[data['Average Cost for two'] > 0]
        
        # Sort by cost (ascending)
        data = data.sort_values('Average Cost for two')
        
        return data.head(limit).reset_index(drop=True)
    
    def get_statistics(self, cuisine: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about restaurants, optionally for a specific cuisine.
        
        Args:
            cuisine: Optional cuisine filter
            
        Returns:
            Dictionary of statistics
        """
        # Filter by cuisine if specified
        if cuisine:
            data = self.data[
                self.data['Cuisine List'].apply(
                    lambda c: any(cuisine.lower() in x.lower() for x in c)
                )
            ]
        else:
            data = self.data.copy()
        
        rated_restaurants = data[data['Aggregate rating'] > 0]
        costs = data[data['Average Cost for two'] > 0]['Average Cost for two']
        
        return {
            'total_restaurants': len(data),
            'rated_restaurants': len(rated_restaurants),
            'avg_rating': float(rated_restaurants['Aggregate rating'].mean()) if len(rated_restaurants) > 0 else 0,
            'max_rating': float(rated_restaurants['Aggregate rating'].max()) if len(rated_restaurants) > 0 else 0,
            'min_rating': float(rated_restaurants['Aggregate rating'].min()) if len(rated_restaurants) > 0 else 0,
            'avg_cost': float(costs.mean()) if len(costs) > 0 else 0,
            'min_cost': float(costs.min()) if len(costs) > 0 else 0,
            'max_cost': float(costs.max()) if len(costs) > 0 else 0,
        }
