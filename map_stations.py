"""Tool to help map physical LEDs to Metro stations."""
import json
import time
from led_controller import LEDController
from config import LED_COUNT

def load_station_names():
    """Load station names from JSON file."""
    with open('station_names.json', 'r') as f:
        return json.load(f)

def save_mapping(mapping):
    """Save LED to station mapping to config file."""
    # Create the new config content
    config_content = """# Metro station codes mapped to LED indices
# The LED indices should match the physical layout of your LED strip
# Reference: https://developer.wmata.com/docs/services/5763fa6ff91823096cac1057/operations/5763fa8ef91823096cac1058

STATION_TO_LED = {
"""
    # Add each station mapping with a comment showing the station name
    station_names = load_station_names()
    for station_code, led_index in sorted(mapping.items()):
        station_name = station_names.get(station_code, station_code)
        config_content += f"    '{station_code}': {led_index},  # {station_name}\n"

    # Add the rest of the config file
    config_content += """}

# Color codes for different train lines
LINE_COLORS = {
    'RD': (255, 0, 0),     # Red Line
    'BL': (0, 0, 255),     # Blue Line
    'YL': (255, 255, 0),   # Yellow Line
    'OR': (255, 165, 0),   # Orange Line
    'GR': (0, 255, 0),     # Green Line
    'SV': (192, 192, 192), # Silver Line
}

# Total number of LEDs needed for the setup
LED_COUNT = max(STATION_TO_LED.values()) + 1
"""
    
    # Write the new config
    with open('config.py', 'w') as f:
        f.write(config_content)

def main():
    # Initialize LED controller
    led = LEDController(led_count=LED_COUNT)
    if not led.is_initialized():
        print("Error: LED controller not initialized")
        return

    # Load station names
    station_names = load_station_names()
    
    # Create a new mapping
    mapping = {}
    used_leds = set()
    
    # Group stations by line for easier mapping
    lines = {
        'Red Line': [code for code in station_names if code.startswith(('A', 'B'))],
        'Blue/Orange/Silver': [code for code in station_names if code.startswith(('C', 'D', 'K', 'N'))],
        'Green/Yellow': [code for code in station_names if code.startswith(('E', 'F'))],
    }

    print("\nWelcome to the Metro Station LED Mapping Tool!")
    print("\nThis tool will help you map each physical LED to a Metro station.")
    print("For each station, the corresponding LED will light up in white.")
    print("You can then accept the current LED or move to the next/previous LED.")
    
    try:
        for line_name, station_codes in lines.items():
            print(f"\n=== Mapping {line_name} ===")
            
            for station_code in station_codes:
                station_name = station_names[station_code]
                current_led = 0
                
                while True:
                    # Clear all LEDs
                    led.clear()
                    
                    # Light up the current LED in white
                    led.set_pixel(current_led, 255, 255, 255)
                    led.show()
                    
                    print(f"\nStation: {station_name} ({station_code})")
                    print(f"Currently showing LED: {current_led}")
                    print("\nCommands:")
                    print("  [Enter] = Accept this LED")
                    print("  n = Next LED")
                    print("  p = Previous LED")
                    print("  s = Skip this station")
                    print("  q = Save and quit")
                    
                    choice = input("\nChoice: ").lower().strip()
                    
                    if choice == '':  # Accept current LED
                        if current_led in used_leds:
                            print("\nError: This LED is already assigned to another station!")
                            continue
                        mapping[station_code] = current_led
                        used_leds.add(current_led)
                        break
                    elif choice == 'n':  # Next LED
                        current_led = (current_led + 1) % LED_COUNT
                    elif choice == 'p':  # Previous LED
                        current_led = (current_led - 1) % LED_COUNT
                    elif choice == 's':  # Skip station
                        break
                    elif choice == 'q':  # Save and quit
                        raise KeyboardInterrupt
                    
                    # Clear screen for next iteration
                    print("\n" * 2)
        
    except KeyboardInterrupt:
        print("\n\nSaving mapping...")
    
    # Save the mapping
    if mapping:
        save_mapping(mapping)
        print(f"\nMapping saved! {len(mapping)} stations mapped.")
        
        # Show a test pattern
        print("\nShowing test pattern (will run for 10 seconds)...")
        for _ in range(10):
            # Clear all LEDs
            led.clear()
            
            # Light up each mapped LED with a different color based on position
            for i, led_index in enumerate(sorted(used_leds)):
                r = (i * 50) % 255
                g = (i * 85) % 255
                b = (i * 120) % 255
                led.set_pixel(led_index, r, g, b)
            
            led.show()
            time.sleep(1)
            
        # Clear LEDs when done
        led.clear()
        led.show()
    
    print("\nDone! You can now run the main application.")

if __name__ == '__main__':
    main()
