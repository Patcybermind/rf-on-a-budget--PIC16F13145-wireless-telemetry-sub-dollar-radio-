def remove_isolated_ones(binary_string):
    """
    Remove isolated 1s (1s that have fewer than 1 adjacent 1).
    A 1 is considered isolated if it doesn't have at least one adjacent 1.
    """
    chars = list(binary_string)
    length = len(chars)
    
    # Create a copy to mark positions for removal
    to_remove = [False] * length
    
    for i in range(length):
        if chars[i] == '1':
            # Check if this 1 has at least one adjacent 1
            has_adjacent_one = False
            
            # Check left neighbor
            if i > 0 and chars[i-1] == '1':
                has_adjacent_one = True
            
            # Check right neighbor
            if i < length - 1 and chars[i+1] == '1':
                has_adjacent_one = True
            
            # If no adjacent 1s, mark for removal
            if not has_adjacent_one:
                to_remove[i] = True
    
    # Replace isolated 1s with 0s
    for i in range(length):
        if to_remove[i]:
            chars[i] = '0'
    
    return ''.join(chars)

def process_file(filename):
    """
    Read the file, process each line to remove isolated 1s,
    and write the corrected version back to the file.
    """
    try:
        # Read the file
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        # Process each line
        corrected_lines = []
        for line in lines:
            line = line.strip()  # Remove newline characters
            if line:  # Skip empty lines
                # Split the line at the colon to separate prefix from binary data
                if ':' in line:
                    prefix, binary_data = line.split(':', 1)
                    binary_data = binary_data.strip()
                    
                    # Remove isolated 1s from the binary data
                    corrected_binary = remove_isolated_ones(binary_data)
                    
                    # Reconstruct the line
                    corrected_line = f"{prefix}: {corrected_binary}"
                    corrected_lines.append(corrected_line)
                else:
                    # If no colon, treat the whole line as binary data
                    corrected_binary = remove_isolated_ones(line)
                    corrected_lines.append(corrected_binary)
        
        # Write the corrected version back to the file
        with open(filename, 'w') as file:
            for line in corrected_lines:
                file.write(line + '\n')
        
        print(f"Successfully processed {filename}")
        print(f"Processed {len(corrected_lines)} lines")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error processing file: {e}")

# Main execution
if __name__ == "__main__":
    filename = "test.txt"
    process_file(filename)