"""
Data loading and preprocessing module for the Smart Restaurant Recommender.

This module handles loading restaurant data from CSV files and performing
necessary data cleaning and transformations.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
from pathlib import Path
from .utils import parse_cuisines


class RestaurantDataLoader:
    """
    Handles loading and preprocessing of restaurant data from CSV files.
    
    Attributes:
        data: DataFrame containing restaurant information
        filepath: Path to the data file
    """
    
    def __init__(self, filepath: str):
        """
        Initialize the data loader.
        
        Args:
            filepath: Path to the CSV file containing restaurant data
        """
        self.filepath = filepath
        self.data: Optional[pd.DataFrame] = None
        self._load_and_preprocess()
    
    def _load_and_preprocess(self) -> None:
        """Load and preprocess the restaurant data."""
        try:
            # Load the CSV file
            self.data = pd.read_csv(self.filepath)
            
            # Verify required columns exist
            required_columns = [
                'Restaurant Name', 'Cuisines', 'Average Cost for two',
                'Aggregate rating', 'City', 'Address'
            ]
            
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Data cleaning
            self._clean_data()
            
            # Data enrichment
            self._enrich_data()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset not found at {self.filepath}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def _clean_data(self) -> None:
        """Perform data cleaning operations."""
        # Remove duplicates based on restaurant name and city
        self.data = self.data.drop_duplicates(
            subset=['Restaurant Name', 'City'],
            keep='first'
        )
        
        # Handle missing values in rating
        self.data['Aggregate rating'] = self.data['Aggregate rating'].fillna(0)
        
        # Ensure numeric columns are properly typed
        self.data['Average Cost for two'] = pd.to_numeric(
            self.data['Average Cost for two'],
            errors='coerce'
        ).fillna(0)
        
        self.data['Votes'] = pd.to_numeric(
            self.data['Votes'],
            errors='coerce'
        ).fillna(0)
    
    def _enrich_data(self) -> None:
        """Perform data enrichment operations."""
        # Parse cuisines into a list for each restaurant
        self.data['Cuisine List'] = self.data['Cuisines'].apply(parse_cuisines)
        
        # Extract currency code
        self.data['Currency Code'] = self.data['Currency'].apply(
            lambda x: self._extract_currency_code(x)
        )
        
        # Add a unique restaurant ID if not present
        if 'Restaurant ID' not in self.data.columns:
            self.data['Restaurant ID'] = range(1, len(self.data) + 1)
    
    @staticmethod
    def _extract_currency_code(currency_string: str) -> str:
        """Extract currency code from currency string."""
        if pd.isna(currency_string):
            return ""
        
        currency_str = str(currency_string)
        
        # Try to extract text between parentheses
        if "(" in currency_str and ")" in currency_str:
            start = currency_str.find("(") + 1
            end = currency_str.find(")")
            return currency_str[start:end]
        
        return currency_str
    
    def get_data(self) -> pd.DataFrame:
        """
        Get the preprocessed restaurant data.
        
        Returns:
            DataFrame containing restaurant information
        """
        return self.data.copy()
    
    def get_unique_cuisines(self) -> list:
        """
        Get a sorted list of all unique cuisines in the dataset.
        
        Returns:
            Sorted list of unique cuisine names
        """
        all_cuisines = set()
        
        for cuisine_list in self.data['Cuisine List']:
            all_cuisines.update(cuisine_list)
        
        return sorted(list(all_cuisines))
    
    def get_budget_statistics(self) -> Tuple[float, float, float, float]:
        """
        Get budget statistics from the dataset.
        
        Returns:
            Tuple of (min_budget, max_budget, mean_budget, median_budget)
        """
        costs = self.data['Average Cost for two']
        costs = costs[costs > 0]  # Exclude zero values
        
        return (
            float(costs.min()),
            float(costs.max()),
            float(costs.mean()),
            float(costs.median())
        )
    
    def get_cities(self) -> list:
        """
        Get a sorted list of all unique cities.
        
        Returns:
            Sorted list of city names
        """
        return sorted(self.data['City'].unique().tolist())
    
    def get_data_summary(self) -> dict:
        """
        Get a summary of the dataset statistics.
        
        Returns:
            Dictionary containing dataset statistics
        """
        return {
            'total_restaurants': len(self.data),
            'unique_cuisines': len(self.get_unique_cuisines()),
            'unique_cities': len(self.get_cities()),
            'avg_rating': float(self.data['Aggregate rating'].mean()),
            'avg_cost': float(self.data['Average Cost for two'].mean()),
            'restaurants_with_rating': int((self.data['Aggregate rating'] > 0).sum())
        }
