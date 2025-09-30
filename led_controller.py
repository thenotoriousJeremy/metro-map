from rpi_ws281x import PixelStrip, Color
import platform

class LEDController:
    def __init__(self, led_count=30, pin=18, freq_hz=800000, dma=10, brightness=255, channel=0, invert=False):
        """Initialize LED controller with default settings for WS281x LEDs.
        
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
        
        # Only initialize the strip on Linux (Raspberry Pi)
        if platform.system() == "Linux":
            try:
                self.strip = PixelStrip(
                    num=self.LED_COUNT,
                    pin=self.PIN,
                    freq_hz=self.FREQ_HZ,
                    dma=self.DMA,
                    invert=self.INVERT,
                    brightness=self.BRIGHTNESS,
                    channel=self.CHANNEL
                )
                self.strip.begin()
            except Exception as e:
                import logging
                logging.warning(f"LED initialization failed: {e}. Running in dummy mode.")
                self.strip = None  # Run in dummy mode if initialization fails
    
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
