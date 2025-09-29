"""
Universal Predictor - A flexible Bayesian prediction engine.

This module provides a general-purpose Bayesian prediction system that can be adapted
to various domains beyond just dating predictions.
"""

from typing import Dict, Any, Optional
import numpy as np

class UniversalPredictor:
    def __init__(self, prior: float = 0.5):
        """
        Initialize the universal predictor.
        
        Args:
            prior: The prior probability of the positive class (default: 0.5)
        """
        self.prior = prior
        self.feature_likelihoods: Dict[str, Dict[Any, float]] = {}
        self.feature_counts: Dict[str, Dict[Any, int]] = {}
    
    def update(self, feature: str, value: Any, positive_count: int, total_count: int) -> None:
        """
        Update the model with new feature likelihoods.
        
        Args:
            feature: The name of the feature
            value: The specific value of the feature
            positive_count: Number of positive outcomes for this feature value
            total_count: Total number of observations for this feature value
        """
        if total_count <= 0:
            raise ValueError("Total count must be positive")
            
        if positive_count > total_count:
            raise ValueError("Positive count cannot exceed total count")
            
        if feature not in self.feature_likelihoods:
            self.feature_likelihoods[feature] = {}
            self.feature_counts[feature] = {}
            
        self.feature_likelihoods[feature][value] = positive_count / total_count
        self.feature_counts[feature][value] = total_count
    
    def predict(self, features: Dict[str, Any], explain: bool = False) -> Dict:
        """
        Predict the probability of the positive class.
        
        Args:
            features: Dictionary of feature names to values
            explain: Whether to print detailed explanation of the prediction
            
        Returns:
            dict: Contains probability, confidence, and explanation
        """
        if explain:
            print(f"\nPredicting for features: {features}")
            print(f"Starting with prior probability: {self.prior:.1%}")
        
        # Start with the prior probability
        posterior = self.prior
        used_features = []
        ignored_features = []
        
        # Apply each feature's likelihood
        for feature, value in features.items():
            if feature in self.feature_likelihoods and value in self.feature_likelihoods[feature]:
                likelihood = self.feature_likelihoods[feature][value]
                old_posterior = posterior
                # Apply Bayes' theorem incrementally
                posterior = (likelihood * posterior) / (likelihood * posterior + (1 - likelihood) * (1 - posterior))
                used_features.append((feature, value, likelihood))
                
                if explain:
                    print(f"  {feature}[{value}]: likelihood={likelihood:.1%} -> {old_posterior:.1%} -> {posterior:.1%}")
            else:
                ignored_features.append((feature, value))
                if explain:
                    print(f"  {feature}[{value}]: No data available (ignored)")
        
        # Calculate confidence based on how many features were used
        total_features = len(features)
        used_count = len(used_features)
        confidence = used_count / total_features if total_features > 0 else 0.0
        
        result = {
            'probability': posterior,
            'confidence': confidence,
            'used_features': used_features,
            'ignored_features': ignored_features
        }
        
        if explain:
            print(f"\nFinal prediction: {posterior:.1%} probability")
            print(f"Confidence level: {confidence:.1%}")
        
        return result
    
    def get_feature_importance(self, feature: str) -> Dict[Any, float]:
        """
        Get the importance of each value for a given feature.
        
        Args:
            feature: The name of the feature
            
        Returns:
            Dictionary mapping feature values to their likelihood ratios
        """
        if feature not in self.feature_likelihoods:
            return {}
            
        return {
            value: (likelihood - self.prior) * count
            for value, (likelihood, count) in zip(
                self.feature_likelihoods[feature].keys(),
                zip(
                    self.feature_likelihoods[feature].values(),
                    self.feature_counts[feature].values()
                )
            )
        }
