import platform
import logging
from typing import List, Tuple

# Try to import LED library, but don't fail if not available
try:
    from rpi_ws281x import PixelStrip, Color
    LED_LIBRARY_AVAILABLE = True
except ImportError:
    LED_LIBRARY_AVAILABLE = False
    logging.info("rpi_ws281x library not available, running in simulation mode")

class SimulatedLED:
    """Simulated LED strip for development and testing."""
    def __init__(self, led_count: int):
        self.led_count = led_count
        self.leds: List[Tuple[int, int, int]] = [(0, 0, 0)] * led_count
    
    def setPixelColor(self, index: int, color: int) -> None:
        if 0 <= index < self.led_count:
            # Extract RGB from the color integer
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            self.leds[index] = (r, g, b)
            logging.debug(f"Set LED {index} to RGB({r}, {g}, {b})")
    
    def begin(self) -> None:
        logging.info("Initialized simulated LED strip with %d LEDs", self.led_count)
    
    def show(self) -> None:
        # Log the first few active LEDs for debugging
        active_leds = [(i, color) for i, color in enumerate(self.leds) if color != (0, 0, 0)]
        if active_leds:
            sample = active_leds[:3]  # Show first 3 active LEDs
            logging.info("Active LEDs: %s %s", 
                      ", ".join(f"LED {i}: RGB{color}" for i, color in sample),
                      "..." if len(active_leds) > 3 else "")

def Color(red: int, green: int, blue: int) -> int:
    """Convert the provided red, green, blue color to a 24-bit color value."""
    return (red << 16) | (green << 8) | blue

class LEDController:
    def __init__(self, led_count=30, pin=18, freq_hz=800000, dma=10, brightness=255, channel=0, invert=False):
        """Initialize LED controller with default settings for WS281x LEDs.
        Attempts to initialize real LED hardware first, falls back to simulation if unsuccessful.
        
        Args:
            led_count (int): Number of LED pixels
            pin (int): GPIO pin connected to the pixels (must support PWM)
            freq_hz (int): LED signal frequency in Hz (usually 800kHz)
            dma (int): DMA channel to use for generating signal
            brightness (int): Set to 0 for darkest and 255 for brightest
            channel (int): PWM channel to use
            invert (bool): True to invert the signal
        """
        self.LED_COUNT = led_count
        self.PIN = pin
        self.FREQ_HZ = freq_hz
        self.DMA = dma
        self.BRIGHTNESS = brightness
        self.CHANNEL = channel
        self.INVERT = invert
        self.strip = None
        self.simulated = True  # Default to True, will be set to False on successful hardware init
        
        # Try to initialize real LED strip first
        if platform.system() == "Linux" and LED_LIBRARY_AVAILABLE:
            try:
                logging.info("Attempting to initialize real LED hardware...")
                self.strip = PixelStrip(
                    num=self.LED_COUNT,
                    pin=self.PIN,
                    freq_hz=self.FREQ_HZ,
                    dma=self.DMA,
                    invert=self.INVERT,
                    brightness=self.BRIGHTNESS,
                    channel=self.CHANNEL
                )
                # This is where the mailbox device error occurs
                try:
                    self.strip.begin()
                    logging.info("Successfully initialized real LED strip!")
                    self.simulated = False
                    return
                except RuntimeError as e:
                    if "Failed to create mailbox device" in str(e):
                        logging.warning("Failed to access mailbox device - insufficient permissions")
                        self.strip = None
                    else:
                        raise
            except Exception as e:
                logging.warning(f"LED initialization failed: {e}")
                self.strip = None
        else:
            logging.info("Not on Linux or LED library not available")

        # If we get here, either hardware init failed or we're not on Linux
        logging.info("Using simulation mode...")
        self.strip = SimulatedLED(led_count)
        self.simulated = True
        logging.info("Running in simulation mode - LED states will be logged")
    
    def is_initialized(self):
        """Check if LED strip is initialized."""
        return self.strip is not None

    def set_pixel(self, index, r, g, b, brightness=1.0):
        """Set color of a specific pixel with brightness.
        
        Args:
            index (int): LED index
            r (int): Red value (0-255)
            g (int): Green value (0-255)
            b (int): Blue value (0-255)
            brightness (float): Brightness factor (0.0-1.0)
        """
        if not self.strip:
            # In dummy mode, just log the operation
            import logging
            logging.debug(f"LED {index} would be set to RGB({r},{g},{b}) at {brightness} brightness")
            return
            
        if 0 <= index < self.LED_COUNT:
            r = int(r * brightness)
            g = int(g * brightness)
            b = int(b * brightness)
            try:
                self.strip.setPixelColor(index, Color(r, g, b))
            except Exception as e:
                import logging
                logging.warning(f"Failed to set LED {index}: {e}")

    def set_comet(self, index, r, g, b, direction="right", trail_length=3):
        """Set a comet effect with trailing lights.
        
        Args:
            index (int): Center LED index
            r (int): Red value (0-255)
            g (int): Green value (0-255)
            b (int): Blue value (0-255)
            direction (str): "right" or "left" for trail direction
            trail_length (int): Number of LEDs in the trail
        """
        if not self.strip:
            return
            
        # Set the main LED at full brightness
        self.set_pixel(index, r, g, b)
        
        # Calculate the range for the trail based on direction
        if direction == "right":
            trail_range = range(index + 1, min(index + trail_length + 1, self.LED_COUNT))
        else:  # left
            trail_range = range(index - 1, max(index - trail_length - 1, -1), -1)
        
        # Set trailing LEDs with decreasing brightness
        for i, trail_index in enumerate(trail_range, 1):
            brightness = 1.0 - (i / (trail_length + 1))
            self.set_pixel(trail_index, r, g, b, brightness)

    def clear(self):
        """Turn off all LEDs."""
        if self.strip:
            for i in range(self.LED_COUNT):
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.show()

    def show(self):
        """Update the LED strip with all changes."""
        if not self.strip:
            # In dummy mode, just log the operation
            import logging
            logging.debug("LED strip would update now")
            return
            
        try:
            self.strip.show()
        except Exception as e:
            import logging
            logging.warning(f"Failed to update LED strip: {e}")
