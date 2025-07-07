import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
# No need for matplotlib in the Django integration for actual recommendations
# import matplotlib.pyplot as plt

class PlantRecommendationFuzzySystem:
    """
    Mamdani Fuzzy Logic System for Plant Recommendation
    Based on pH, Temperature, and Humidity measurements
    """

    def __init__(self):
        # Plant database from Table 2.2 "Tanaman Pangan"
        self.plant_database = {
            'Padi': {'ph': (6.0, 7.0), 'temp': (24, 29), 'humidity': (60, 90)},
            'Jagung': {'ph': (5.8, 8.0), 'temp': (21, 34), 'humidity': (50, 80)},
            'Kedelai': {'ph': (6.0, 7.0), 'temp': (20, 25), 'humidity': (60, 80)},
            'Kacang_Tanah': {'ph': (5.8, 7.0), 'temp': (23, 33), 'humidity': (65, 75)},
            'Kacang_Hijau': {'ph': (6.0, 7.0), 'temp': (25, 35), 'humidity': (50, 80)},
            'Ubi_Kayu': {'ph': (4.5, 8.0), 'temp': (24, 30), 'humidity': (70, 85)},
            'Ubi_Jalar': {'ph': (5.5, 8.0), 'temp': (21, 27), 'humidity': (65, 80)}
        }

        self.setup_fuzzy_system()

    def setup_fuzzy_system(self):
        """Initialize the complete Mamdani fuzzy logic system"""

        # Define input variables with their universes
        self.ph = ctrl.Antecedent(np.arange(0, 14.1, 0.1), 'ph')
        self.temperature = ctrl.Antecedent(np.arange(0, 50.1, 0.1), 'temperature')
        self.humidity = ctrl.Antecedent(np.arange(0, 100.1, 0.1), 'humidity')

        # Define output variables for each plant
        self.plant_outputs = {}
        for plant in self.plant_database.keys():
            self.plant_outputs[plant] = ctrl.Consequent(np.arange(0, 1.01, 0.01), plant.lower())

        # Setup membership functions
        self._setup_input_membership_functions()
        self._setup_output_membership_functions()

        # Setup fuzzy rules
        self._setup_fuzzy_rules()

        # Create control systems for each plant
        self._create_control_systems()

    def _setup_input_membership_functions(self):
        """Define membership functions for input variables"""

        # pH membership functions
        self.ph['acidic'] = fuzz.trapmf(self.ph.universe, [0, 0, 4.5, 6.0])
        self.ph['neutral'] = fuzz.trimf(self.ph.universe, [5.0, 6.5, 8.0])
        self.ph['alkaline'] = fuzz.trapmf(self.ph.universe, [7.0, 8.5, 14, 14])

        # Temperature membership functions (°C)
        self.temperature['cold'] = fuzz.trapmf(self.temperature.universe, [0, 0, 18, 23])
        self.temperature['normal'] = fuzz.trimf(self.temperature.universe, [20, 27, 32])
        self.temperature['hot'] = fuzz.trapmf(self.temperature.universe, [30, 35, 50, 50])

        # Humidity membership functions (%)
        self.humidity['low'] = fuzz.trapmf(self.humidity.universe, [0, 0, 45, 60])
        self.humidity['medium'] = fuzz.trimf(self.humidity.universe, [50, 70, 85])
        self.humidity['high'] = fuzz.trapmf(self.humidity.universe, [80, 90, 100, 100])

    def _setup_output_membership_functions(self):
        """Define membership functions for output variables (plant suitability)"""

        for plant_name, plant_output in self.plant_outputs.items():
            plant_output['unsuitable'] = fuzz.trimf(plant_output.universe, [0, 0, 0.3])
            plant_output['moderate'] = fuzz.trimf(plant_output.universe, [0.2, 0.5, 0.8])
            plant_output['suitable'] = fuzz.trimf(plant_output.universe, [0.7, 1.0, 1.0])

    def _setup_fuzzy_rules(self):
        """Define fuzzy rules based on plant requirements from Table 2.2"""

        self.rule_sets = {}

        # Rules for Padi (pH: 6.0-7.0, Temp: 24-29°C, Humidity: 60-90%)
        self.rule_sets['Padi'] = [
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Padi']['suitable']),
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['high'],
                      self.plant_outputs['Padi']['suitable']),
            ctrl.Rule(self.ph['acidic'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Padi']['moderate']),
            ctrl.Rule(self.ph['alkaline'] | self.temperature['cold'] | self.humidity['low'],
                      self.plant_outputs['Padi']['unsuitable'])
        ]

        # Rules for Jagung (pH: 5.8-8.0, Temp: 21-34°C, Humidity: 50-80%)
        self.rule_sets['Jagung'] = [
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Jagung']['suitable']),
            ctrl.Rule(self.ph['neutral'] & self.temperature['hot'] & self.humidity['medium'],
                      self.plant_outputs['Jagung']['suitable']),
            ctrl.Rule(self.ph['alkaline'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Jagung']['moderate']),
            ctrl.Rule(self.ph['acidic'] & self.temperature['cold'] & self.humidity['low'],
                      self.plant_outputs['Jagung']['unsuitable'])
        ]

        # Rules for Kedelai (pH: 6.0-7.0, Temp: 20-25°C, Humidity: 60-80%)
        self.rule_sets['Kedelai'] = [
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Kedelai']['suitable']),
            ctrl.Rule(self.ph['neutral'] & self.temperature['cold'] & self.humidity['medium'],
                      self.plant_outputs['Kedelai']['moderate']),
            ctrl.Rule(self.ph['acidic'] | self.temperature['hot'] | self.humidity['low'],
                      self.plant_outputs['Kedelai']['unsuitable'])
        ]

        # Rules for Kacang Tanah (pH: 5.8-7.0, Temp: 23-33°C, Humidity: 65-75%)
        self.rule_sets['Kacang_Tanah'] = [
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Kacang_Tanah']['suitable']),
            ctrl.Rule(self.ph['neutral'] & self.temperature['hot'] & self.humidity['medium'],
                      self.plant_outputs['Kacang_Tanah']['suitable']),
            ctrl.Rule(self.ph['acidic'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Kacang_Tanah']['moderate']),
            ctrl.Rule(self.ph['alkaline'] | self.temperature['cold'] | self.humidity['high'],
                      self.plant_outputs['Kacang_Tanah']['unsuitable'])
        ]

        # Rules for Kacang Hijau (pH: 6.0-7.0, Temp: 25-35°C, Humidity: 50-80%)
        self.rule_sets['Kacang_Hijau'] = [
            ctrl.Rule(self.ph['neutral'] & self.temperature['hot'] & self.humidity['medium'],
                      self.plant_outputs['Kacang_Hijau']['suitable']),
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['low'],
                      self.plant_outputs['Kacang_Hijau']['moderate']),
            ctrl.Rule(self.ph['acidic'] | self.temperature['cold'] | self.humidity['high'],
                      self.plant_outputs['Kacang_Hijau']['unsuitable'])
        ]

        # Rules for Ubi Kayu (pH: 4.5-8.0, Temp: 24-30°C, Humidity: 70-85%)
        self.rule_sets['Ubi_Kayu'] = [
            ctrl.Rule(self.ph['acidic'] & self.temperature['normal'] & self.humidity['high'],
                      self.plant_outputs['Ubi_Kayu']['suitable']),
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Ubi_Kayu']['suitable']),
            ctrl.Rule(self.ph['alkaline'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Ubi_Kayu']['moderate']),
            ctrl.Rule(self.temperature['cold'] | self.humidity['low'],
                      self.plant_outputs['Ubi_Kayu']['unsuitable'])
        ]

        # Rules for Ubi Jalar (pH: 5.5-8.0, Temp: 21-27°C, Humidity: 65-80%)
        self.rule_sets['Ubi_Jalar'] = [
            ctrl.Rule(self.ph['neutral'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Ubi_Jalar']['suitable']),
            ctrl.Rule(self.ph['alkaline'] & self.temperature['normal'] & self.humidity['medium'],
                      self.plant_outputs['Ubi_Jalar']['moderate']),
            ctrl.Rule(self.ph['acidic'] | self.temperature['hot'] | self.humidity['low'],
                      self.plant_outputs['Ubi_Jalar']['unsuitable'])
        ]

    def _create_control_systems(self):
        """Create control systems for each plant"""
        self.control_systems = {}
        self.simulators = {}

        for plant_name, rules in self.rule_sets.items():
            self.control_systems[plant_name] = ctrl.ControlSystem(rules)
            self.simulators[plant_name] = ctrl.ControlSystemSimulation(self.control_systems[plant_name])

    def get_plant_recommendation(self, ph_value, temp_value, humidity_value):
        """
        Get plant recommendation based on sensor inputs

        Parameters:
        ph_value (float): pH value (0-14)
        temp_value (float): Temperature in Celsius
        humidity_value (float): Humidity percentage (0-100)

        Returns:
        dict: Contains recommended plants with confidence scores
        """

        # Validate inputs
        if not (0 <= ph_value <= 14):
            raise ValueError("pH value must be between 0 and 14")
        if not (0 <= temp_value <= 50):
            raise ValueError("Temperature must be between 0 and 50°C")
        if not (0 <= humidity_value <= 100):
            raise ValueError("Humidity must be between 0 and 100%")

        results = {}

        # Calculate suitability for each plant
        for plant_name, simulator in self.simulators.items():
            try:
                # Set input values
                simulator.input['ph'] = ph_value
                simulator.input['temperature'] = temp_value
                simulator.input['humidity'] = humidity_value

                # Compute the result
                simulator.compute()

                # Get the defuzzified output (suitability score)
                suitability_score = simulator.output[plant_name.lower()]
                results[plant_name] = round(suitability_score, 3)

            except Exception as e:
                # Handle cases where no rules fire
                results[plant_name] = 0.0

        # Sort results by suitability score
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

        return self._format_recommendation(sorted_results, ph_value, temp_value, humidity_value)

    def _format_recommendation(self, results, ph_value, temp_value, humidity_value):
        """Format the recommendation output with confidence levels"""

        # Determine confidence levels
        recommendations = []
        for plant, score in results.items():
            if score >= 0.7:
                confidence = "High"
                status = "Highly Suitable"
            elif score >= 0.4:
                confidence = "Medium"
                status = "Moderately Suitable"
            elif score >= 0.2:
                confidence = "Low"
                status = "Possibly Suitable"
            else:
                confidence = "Very Low"
                status = "Not Suitable"

            recommendations.append({
                'plant': plant,
                'suitability_score': score,
                'confidence': confidence,
                'status': status
            })

        # Get top recommendation
        top_plant = recommendations[0] if recommendations else None

        return {
            'input_conditions': {
                'ph': ph_value,
                'temperature': temp_value,
                'humidity': humidity_value
            },
            'top_recommendation': top_plant,
            'all_plants': recommendations,
            'recommendation_summary': self._generate_summary(top_plant, recommendations)
        }

    def _generate_summary(self, top_plant, all_recommendations):
        """Generate a human-readable summary of the recommendation"""

        if not top_plant or top_plant['suitability_score'] < 0.2:
            return "Current soil conditions are not optimal for any of the analyzed crops. Consider soil amendment or different crop selection."

        suitable_plants = [plant for plant in all_recommendations if plant['suitability_score'] >= 0.4]

        if len(suitable_plants) == 1:
            return f"{top_plant['plant']} is recommended with {top_plant['confidence'].lower()} confidence (score: {top_plant['suitability_score']})."
        elif len(suitable_plants) > 1:
            plant_names = [plant['plant'] for plant in suitable_plants[:3]]
            return f"Multiple suitable options: {', '.join(plant_names)}. {top_plant['plant']} has the highest suitability."
        else:
            return f"{top_plant['plant']} is the best option available, though conditions are not optimal."

    # def visualize_membership_functions(self, save_plots=False):
    #     """
    #     Visualize the membership functions for inputs.
    #     This method is typically not used in a deployed Django app,
    #     but kept for development/debugging purposes.
    #     """
    #     #import matplotlib.pyplot as plt # Import locally to avoid dependency if not needed
    #
    #     fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    #
    #     # pH membership functions
    #     self.ph.view(sim=axes[0])
    #     axes[0].set_title('pH Membership Functions')
    #     axes[0].set_xlabel('pH Value')
    #     axes[0].set_ylabel('Membership Degree')
    #
    #     # Temperature membership functions
    #     self.temperature.view(sim=axes[1])
    #     axes[1].set_title('Temperature Membership Functions')
    #     axes[1].set_xlabel('Temperature (°C)')
    #     axes[1].set_ylabel('Membership Degree')
    #
    #     # Humidity membership functions
    #     self.humidity.view(sim=axes[2])
    #     axes[2].set_title('Humidity Membership Functions')
    #     axes[2].set_xlabel('Humidity (%)')
    #     axes[2].set_ylabel('Membership Degree')
    #
    #     plt.tight_layout()
    #
    #     if save_plots:
    #         plt.savefig('membership_functions.png', dpi=300, bbox_inches='tight')
    #
    #     plt.show()

    def get_plant_optimal_conditions(self, plant_name):
        """Get the optimal conditions for a specific plant"""

        if plant_name in self.plant_database:
            return self.plant_database[plant_name]
        else:
            available_plants = list(self.plant_database.keys())
            raise ValueError(f"Plant '{plant_name}' not found. Available plants: {available_plants}")