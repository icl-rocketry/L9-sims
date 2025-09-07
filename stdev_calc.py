import json
import numpy as np
from collections import defaultdict

def calculate_std_dev(input_file_path):
    """
    Calculates the standard deviation of each field from a file of JSON objects.

    Each line in the input file is expected to be a self-contained JSON object,
    and each value in the object is expected to be numerical.

    Args:
        input_file_path (str): The path to the input file containing flight data.
    """
    # Use a defaultdict to easily append to lists
    data_points = defaultdict(list)

    try:
        with open(input_file_path, 'r') as infile:
            for line in infile:
                # Ignore empty lines
                if not line.strip():
                    continue
                
                try:
                    # Each line is a JSON object
                    data = json.loads(line)
                    
                    # Append each value to the corresponding key's list
                    for key, value in data.items():
                        if isinstance(value, (int, float)):
                            data_points[key].append(value)
                        else:
                            # Handle cases where a value might not be a number
                            print(f"Warning: Non-numeric value found for key '{key}' and will be ignored: {value}")

                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from line: {line.strip()}")

        if not data_points:
            print("No data was processed. The input file might be empty or in the wrong format.")
            return

        print("--- Standard Deviation for Each Field ---")
        
        # Calculate and print the standard deviation for each field
        for field, values in data_points.items():
            if len(values) > 1:
                std_dev = np.std(values)
                print(f"{field}: {std_dev:.4f}")
            else:
                print(f"{field}: Not enough data points to calculate standard deviation (found {len(values)}).")
        
        print("-----------------------------------------")


    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # --- Configuration ---
    # Make sure the input file is in the same directory as this script,
    # or provide the full path to it.
    input_filename = 'pluto_full_flight.outputs.txt'
    
    # --- Execution ---
    calculate_std_dev(input_filename)
