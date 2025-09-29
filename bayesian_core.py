import numpy as np

class SimpleBayesianForecaster:
    def __init__(self):
        self.scenarios = []
        self.probabilities = []
    
    def add_scenarios(self, scenario_list, probability_list):
        """Add scenarios with their initial probabilities"""
        self.scenarios = scenario_list
        self.probabilities = np.array(probability_list)
        
        print("=== INITIAL SCENARIOS ===")
        for i, (scenario, prob) in enumerate(zip(self.scenarios, self.probabilities)):
            print(f"{i+1}. {scenario}: {prob:.1%}")
        print()
    
    def update_with_evidence(self, evidence_description, likelihood_scores):
        """Update probabilities based on new evidence"""
        print(f"=== NEW EVIDENCE: {evidence_description} ===")
        
        # This is Bayes' theorem in action!
        # New probability = (likelihood × old probability) / total
        likelihoods = np.array(likelihood_scores)
        
        # Multiply each probability by how likely the evidence is under that scenario
        updated_probs = likelihoods * self.probabilities
        
        # Normalize so they add up to 100%
        self.probabilities = updated_probs / updated_probs.sum()
        
        print("Updated probabilities:")
        for scenario, prob in zip(self.scenarios, self.probabilities):
            print(f"  {scenario}: {prob:.1%}")
        print()
    
    def get_most_likely_scenario(self):
        """Return the scenario with highest probability"""
        max_index = np.argmax(self.probabilities)
        return self.scenarios[max_index], self.probabilities[max_index]

# Test it right now!
if __name__ == "__main__":
    forecaster = SimpleBayesianForecaster()
    
    # Example: Predicting weather tomorrow
    scenarios = [
        "Sunny day",
        "Rainy day", 
        "Cloudy day"
    ]
    initial_probs = [0.4, 0.3, 0.3]  # Must add up to 1.0
    
    forecaster.add_scenarios(scenarios, initial_probs)
    
    # New evidence: "Weather app shows 80% chance of precipitation"
    # How likely is this evidence under each scenario?
    likelihood_scores = [
        0.1,  # If it's sunny, weather app saying rain is unlikely
        0.9,  # If it's rainy, weather app saying rain is very likely  
        0.5   # If it's cloudy, weather app saying rain is moderately likely
    ]
    
    forecaster.update_with_evidence("Weather app shows 80% chance of rain", likelihood_scores)
    
    best_scenario, confidence = forecaster.get_most_likely_scenario()
    print(f"Most likely outcome: {best_scenario} ({confidence:.1%} confidence)")
    