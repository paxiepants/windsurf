"""
Dating Prediction Example

This script demonstrates how to use the Bayesian prediction engine for dating compatibility.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from dating_predictor import DatingPredictor

def train_dating_predictor():
    """Train a dating predictor with some example data."""
    # Initialize the predictor
    predictor = DatingPredictor()
    
    # Example training data: (feature, value, positive_outcomes, total_outcomes)
    training_data = [
        ('age', '20-25', 30, 100),  # 30% match rate for age 20-25
        ('age', '26-30', 45, 100),   # 45% match rate for age 26-30
        ('interests', 'sports', 40, 80),  # 50% match rate for sports interest
        ('interests', 'reading', 35, 70),  # 50% match rate for reading
        ('education', 'bachelors', 60, 100),  # 60% match rate for bachelor's degree
        ('smoking', 'no', 70, 100),  # 70% match rate for non-smokers
    ]
    
    # Train the model
    for feature, value, pos, total in training_data:
        predictor.update_model(feature, value, pos, total)
    
    return predictor

def main():
    """Main function to demonstrate the dating predictor."""
    print("Training dating predictor with example data...")
    predictor = train_dating_predictor()
    
    # Example profiles to evaluate
    profiles = [
        {
            'age': '20-25',
            'interests': 'sports',
            'education': 'bachelors',
            'smoking': 'no'
        },
        {
            'age': '26-30',
            'interests': 'reading',
            'education': 'masters',
            'smoking': 'yes'
        }
    ]
    
    # Make predictions
    print("\nMaking predictions...")
    for i, profile in enumerate(profiles, 1):
        probability = predictor.predict(profile)
        print(f"\nProfile {i} compatibility score: {probability*100:.1f}%")
        for feature, value in profile.items():
            print(f"  {feature}: {value}")
    
    print("\nExample complete!")

if __name__ == "__main__":
    main()
