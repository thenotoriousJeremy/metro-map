# Metro station codes mapped to LED indices
# The LED indices should match the physical layout of your LED strip
# Reference: https://developer.wmata.com/docs/services/5763fa6ff91823096cac1057/operations/5763fa8ef91823096cac1058

STATION_TO_LED = {
    # Red Line (0-26)
    'A15': 0,   # Shady Grove
    'A14': 1,   # Rockville
    'A13': 2,   # Twinbrook
    'A12': 3,   # White Flint
    'A11': 4,   # Grosvenor-Strathmore
    'A10': 5,   # Medical Center
    'A09': 6,   # Bethesda
    'A08': 7,   # Friendship Heights
    'A07': 8,   # Tenleytown-AU
    'A06': 9,   # Van Ness-UDC
    'A05': 10,  # Cleveland Park
    'A04': 11,  # Woodley Park
    'A03': 12,  # Dupont Circle
    'A02': 13,  # Farragut North
    'A01': 14,  # Metro Center
    'B01': 15,  # Gallery Place
    'B02': 16,  # Judiciary Square
    'B03': 17,  # Union Station
    'B04': 18,  # NoMa-Gallaudet U
    'B05': 19,  # Rhode Island Ave
    'B06': 20,  # Brookland-CUA
    'B07': 21,  # Fort Totten
    'B08': 22,  # Takoma
    'B09': 23,  # Silver Spring
    'B10': 24,  # Forest Glen
    'B11': 25,  # Wheaton
    'B12': 26,  # Glenmont

    # Blue/Yellow/Green Line South (27-47)
    'C15': 27,  # Huntington
    'C14': 28,  # Eisenhower Avenue
    'C13': 29,  # King St-Old Town
    'C12': 30,  # Braddock Road
    'C11': 31,  # Potomac Yard
    'C10': 32,  # Ronald Reagan Airport
    'C09': 33,  # Crystal City
    'C08': 34,  # Pentagon City
    'C07': 35,  # Pentagon
    'C06': 36,  # Arlington Cemetery
    'C05': 37,  # Rosslyn
    'C04': 38,  # Foggy Bottom-GWU
    'C03': 39,  # Farragut West
    'C02': 40,  # McPherson Square
    'C01': 41,  # Metro Center
    'D01': 42,  # Federal Triangle
    'D02': 43,  # Smithsonian
    'D03': 44,  # L'Enfant Plaza
    'D04': 45,  # Federal Center SW
    'D05': 46,  # Capitol South
    'D06': 47,  # Eastern Market

    # Orange/Silver Line East (48-52)
    'D07': 48,  # Potomac Ave
    'D08': 49,  # Stadium-Armory
    'D09': 50,  # Minnesota Ave
    'D10': 51,  # Deanwood
    'D11': 52,  # Cheverly
    'D12': 53,  # Landover
    'D13': 54,  # New Carrollton

    # Green Line North (55-63)
    'E01': 55,  # Mt Vernon Sq
    'E02': 56,  # Shaw-Howard U
    'E03': 57,  # U Street
    'E04': 58,  # Columbia Heights
    'E05': 59,  # Georgia Ave-Petworth
    'E06': 60,  # West Hyattsville
    'E07': 61,  # Prince George's Plaza
    'E08': 62,  # College Park-U of MD
    'E09': 63,  # Greenbelt

    # Green Line South (64-74)
    'F01': 64,  # Gallery Place
    'F02': 65,  # Archives
    'F03': 66,  # L'Enfant Plaza
    'F04': 67,  # Waterfront
    'F05': 68,  # Navy Yard-Ballpark
    'F06': 69,  # Anacostia
    'F07': 70,  # Congress Heights
    'F08': 71,  # Southern Avenue
    'F09': 72,  # Naylor Road
    'F10': 73,  # Suitland
    'F11': 74,  # Branch Ave

    # Blue/Silver Line East (75-79)
    'G01': 75,  # Benning Road
    'G02': 76,  # Capitol Heights
    'G03': 77,  # Addison Road
    'G04': 78,  # Morgan Boulevard
    'G05': 79,  # Largo Town Center

    # Orange Line West (80-87)
    'K01': 80,  # Court House
    'K02': 81,  # Clarendon
    'K03': 82,  # Virginia Square-GMU
    'K04': 83,  # Ballston-MU
    'K05': 84,  # East Falls Church
    'K06': 85,  # West Falls Church
    'K07': 86,  # Dunn Loring
    'K08': 87,  # Vienna

    # Silver Line West (88-98)
    'N01': 88,  # McLean
    'N02': 89,  # Tysons
    'N03': 90,  # Greensboro
    'N04': 91,  # Spring Hill
    'N06': 92,  # Wiehle-Reston East
    'N07': 93,  # Reston Town Center
    'N08': 94,  # Herndon
    'N09': 95,  # Innovation Center
    'N10': 96,  # Dulles Airport
    'N11': 97,  # Loudoun Gateway
    'N12': 98,  # Ashburn
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
LED_COUNT = max(STATION_TO_LED.values()) + 1  # 99 LEDs total
