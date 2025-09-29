# Metro station codes mapped to LED indices
# The LED indices should match the physical layout of your LED strip
# Reference: https://developer.wmata.com/docs/services/5763fa6ff91823096cac1057/operations/5763fa8ef91823096cac1058

STATION_TO_LED = {
    # Red Line
    'A15': 0,  # Shady Grove
    'A14': 1,  # Rockville
    'A13': 2,  # Twinbrook
    'A12': 3,  # White Flint
    'A11': 4,  # Grosvenor-Strathmore
    'A10': 5,  # Medical Center
    'A09': 6,  # Bethesda
    'A08': 7,  # Friendship Heights
    'A07': 8,  # Tenleytown-AU
    'A06': 9,  # Van Ness-UDC
    'A05': 10, # Cleveland Park
    'A04': 11, # Woodley Park
    'A03': 12, # Dupont Circle
    'A02': 13, # Farragut North
    'A01': 14, # Metro Center
    'B01': 15, # Gallery Place
    'B02': 16, # Judiciary Square
    'B03': 17, # Union Station
    'B04': 18, # NoMa-Gallaudet U
    'B05': 19, # Rhode Island Ave
    'B06': 20, # Brookland-CUA
    'B07': 21, # Fort Totten
    'B08': 22, # Takoma
    'B09': 23, # Silver Spring
    'B10': 24, # Forest Glen
    'B11': 25, # Wheaton
    'B12': 26, # Glenmont
}

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
