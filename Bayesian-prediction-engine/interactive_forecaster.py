from bayesian_core import SimpleBayesianForecaster

def get_user_scenarios():
    """Let user input their own scenarios"""
    print("What situation do you want to forecast? (e.g., 'How will my job interview go?')")
    situation = input("Situation: ")
    print()
    
    scenarios = []
    probabilities = []
    
    print("Enter 3 possible outcomes:")
    for i in range(3):
        scenario = input(f"Scenario {i+1}: ")
        prob = float(input(f"How likely is this? (0.0 to 1.0): "))
        scenarios.append(scenario)
        probabilities.append(prob)
    
    # Normalize probabilities to sum to 1
    total = sum(probabilities)
    probabilities = [p/total for p in probabilities]
    
    return scenarios, probabilities

def get_evidence_update(scenarios):
    """Get new evidence and likelihood scores"""
    print("\n" + "="*50)
    evidence = input("What new evidence do you have? ")
    
    print(f"\nFor each scenario, how likely is this evidence?")
    print("(1.0 = evidence strongly supports this scenario)")
    print("(0.0 = evidence contradicts this scenario)")
    
    likelihoods = []
    for i, scenario in enumerate(scenarios):
        likelihood = float(input(f"Evidence likelihood for '{scenario}': "))
        likelihoods.append(likelihood)
    
    return evidence, likelihoods

def main():
    forecaster = SimpleBayesianForecaster()
    
    # Get initial scenarios from user
    scenarios, probs = get_user_scenarios()
    forecaster.add_scenarios(scenarios, probs)
    
    # Keep updating with evidence
    while True:
        print("\nOptions:")
        print("1. Add new evidence")
        print("2. See current probabilities") 
        print("3. Quit")
        
        choice = input("Choice: ")
        
        if choice == "1":
            evidence, likelihoods = get_evidence_update(scenarios)
            forecaster.update_with_evidence(evidence, likelihoods)
            
        elif choice == "2":
            best, confidence = forecaster.get_most_likely_scenario()
            print(f"\nMost likely: {best} ({confidence:.1%})")
            
        elif choice == "3":
            break

if __name__ == "__main__":
    main()