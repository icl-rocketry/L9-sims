import json

def filter_flight_data(input_file_path, output_file_path, apogee_threshold=4400):
    """
    Filters flight data from an input file based on an apogee threshold.

    Each line in the input file is expected to be a self-contained JSON object.

    Args:
        input_file_path (str): The path to the input file containing flight data.
        output_file_path (str): The path where the filtered data will be saved.
        apogee_threshold (float): The minimum apogee value to keep.
    """
    try:
        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
            kept_entries = 0
            total_entries = 0
            for line in infile:
                # Ignore empty lines
                if not line.strip():
                    continue
                
                total_entries += 1
                try:
                    # Each line is a JSON object
                    data = json.loads(line)
                    
                    # Check if the 'apogee' key exists and meets the threshold
                    if 'apogee' in data and data['apogee'] >= apogee_threshold:
                        # Write the original JSON line to the output file
                        outfile.write(line)
                        kept_entries += 1
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from line: {line.strip()}")
                except KeyError:
                    print(f"Warning: 'apogee' key not found in line: {line.strip()}")

        print("Filtering complete.")
        print(f"Total entries processed: {total_entries}")
        print(f"Entries with apogee >= {apogee_threshold}m: {kept_entries}")
        print(f"Filtered data saved to '{output_file_path}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # --- Configuration ---
    # Make sure the input file is in the same directory as this script,
    # or provide the full path to it.
    input_filename = 'pluto_full_flight.outputs.txt'
    output_filename = 'pluto_filtered_flight.outputs.txt'
    
    # --- Execution ---
    filter_flight_data(input_filename, output_filename)
