# Metro station codes mapped to LED indices
# The LED indices should match the physical layout of your LED strip
# Reference: https://developer.wmata.com/docs/services/5763fa6ff91823096cac1057/operations/5763fa8ef91823096cac1058

STATION_TO_LED = {
    # Red Line (0-26)
    'A15': 37,   # Shady Grove
    'A14': 38,   # Rockville
    'A13': 39,   # Twinbrook
    'A12': 40,   # White Flint
    'A11': 41,   # Grosvenor-Strathmore
    'A10': 42,   # Medical Center
    'A09': 43,   # Bethesda
    'A08': 44,   # Friendship Heights
    'A07': 45,   # Tenleytown-AU
    'A06': 46,   # Van Ness-UDC
    'A05': 47,  # Cleveland Park
    'A04': 48,  # Woodley Park
    'A03': 49,  # Dupont Circle
    'A02': 50,  # Farragut North
    'A01': 13,  # Metro Center
    'B01': 52,  # Gallery Place
    'B02': 72,  # Judiciary Square
    'B03': 71,  # Union Station
    'B04': 70,  # NoMa-Gallaudet U
    'B05': 69,  # Rhode Island Ave
    'B06': 68,  # Brookland-CUA
    'B07': 67,  # Fort Totten
    'B08': 58,  # Takoma
    'B09': 59,  # Silver Spring
    'B10': 60,  # Forest Glen
    'B11': 61,  # Wheaton
    'B12': 62,  # Glenmont

    # Blue/Yellow/Green Line South (27-47)
    'C15': 0,  # Huntington
    'C14': 1,  # Eisenhower Avenue
    'C13': 2,  # King St-Old Town
    'C12': 3,  # Braddock Road
    'C11': 4,  # Potomac Yard
    'C10': 5,  # Ronald Reagan Airport
    'C09': 6,  # Crystal City
    'C08': 7,  # Pentagon City
    'C07': 8,  # Pentagon
    'C06': 36,  # Arlington Cemetery
    'C05': 17,  # Rosslyn
    'C04': 16,  # Foggy Bottom-GWU
    'C03': 15,  # Farragut West
    'C02': 14,  # McPherson Square
    'C01': 13,  # Metro Center
    'D01': 12,  # Federal Triangle
    'D02': 11,  # Smithsonian
    'D03': 10,  # L'Enfant Plaza
    'D04': 9,  # Federal Center SW
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
    'E01': 53,  # Mt Vernon Sq
    'E02': 54,  # Shaw-Howard U
    'E03': 55,  # U Street
    'E04': 56,  # Columbia Heights
    'E05': 57,  # Georgia Ave-Petworth
    'E06': 66,  # West Hyattsville
    'E07': 65,  # Prince George's Plaza
    'E08': 64,  # College Park-U of MD
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
    'K01': 18,  # Court House
    'K02': 19,  # Clarendon
    'K03': 20,  # Virginia Square-GMU
    'K04': 21,  # Ballston-MU
    'K05': 22,  # East Falls Church
    'K06': 25,  # West Falls Church
    'K07': 24,  # Dunn Loring
    'K08': 23,  # Vienna

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
