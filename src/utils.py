"""
Utility functions for the Smart Restaurant Recommender system.

This module contains helper functions for data validation, formatting,
and other utility operations used throughout the application.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd


def parse_cuisines(cuisine_string: str) -> List[str]:
    """
    Parse a comma-separated cuisine string into a list of individual cuisines.
    
    Args:
        cuisine_string: Comma-separated string of cuisines (e.g., "Japanese, Italian")
        
    Returns:
        List of cleaned cuisine names
        
    Example:
        >>> parse_cuisines("Japanese, Italian, Sushi")
        ['Japanese', 'Italian', 'Sushi']
    """
    if not cuisine_string or pd.isna(cuisine_string):
        return []
    
    cuisines = [c.strip() for c in str(cuisine_string).split(',')]
    return [c for c in cuisines if c]  # Filter out empty strings


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format a monetary amount in Indian Rupees.
    
    Args:
        amount: Numeric amount
        currency: Currency string (default: "INR")
        
    Returns:
        Formatted currency string in Indian Rupees
        
    Example:
        >>> format_currency(1500)
        "₹1,500"
    """
    if pd.isna(amount):
        return "N/A"
    
    try:
        return f"₹{amount:,.0f}"
    except (ValueError, TypeError):
        return "N/A"


def get_rating_emoji(rating: float) -> str:
    """
    Return an emoji representation based on restaurant rating.
    
    Args:
        rating: Rating value (typically 0-5)
        
    Returns:
        Emoji string representing the rating
        
    Example:
        >>> get_rating_emoji(4.8)
        "⭐⭐⭐⭐⭐"
    """
    if pd.isna(rating) or rating == 0:
        return "No rating"
    
    if rating >= 4.7:
        return "⭐⭐⭐⭐⭐"
    elif rating >= 4.3:
        return "⭐⭐⭐⭐"
    elif rating >= 3.7:
        return "⭐⭐⭐"
    elif rating >= 3.0:
        return "⭐⭐"
    else:
        return "⭐"


def get_rating_text(rating: float) -> str:
    """
    Get descriptive text for a rating value.
    
    Args:
        rating: Rating value (typically 0-5)
        
    Returns:
        Descriptive text for the rating
        
    Example:
        >>> get_rating_text(4.8)
        "Excellent"
    """
    if pd.isna(rating) or rating == 0:
        return "Not rated"
    
    if rating >= 4.7:
        return "Excellent"
    elif rating >= 4.0:
        return "Very Good"
    elif rating >= 3.3:
        return "Good"
    elif rating >= 2.7:
        return "Average"
    else:
        return "Poor"


def extract_currency_code(currency_string: str) -> str:
    """
    Extract the currency code from a currency string.
    
    Args:
        currency_string: Currency string (e.g., "Botswana Pula(P)")
        
    Returns:
        Currency code (e.g., "P")
        
    Example:
        >>> extract_currency_code("Botswana Pula(P)")
        "P"
    """
    if pd.isna(currency_string):
        return ""
    
    currency_str = str(currency_string)
    
    # Try to extract text between parentheses
    if "(" in currency_str and ")" in currency_str:
        start = currency_str.find("(") + 1
        end = currency_str.find(")")
        return currency_str[start:end]
    
    return currency_str


def validate_budget_range(min_budget: float, max_budget: float) -> Tuple[bool, str]:
    """
    Validate a budget range for logical correctness.
    
    Args:
        min_budget: Minimum budget value
        max_budget: Maximum budget value
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        >>> validate_budget_range(1000, 500)
        (False, "Minimum budget must be less than or equal to maximum budget")
    """
    if min_budget < 0 or max_budget < 0:
        return False, "Budget values cannot be negative"
    
    if min_budget > max_budget:
        return False, "Minimum budget must be less than or equal to maximum budget"
    
    return True, ""


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default value on division by zero.
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Default value if denominator is zero
        
    Returns:
        Result of division or default value
        
    Example:
        >>> safe_divide(100, 0, 0.0)
        0.0
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ValueError, TypeError):
        return default
