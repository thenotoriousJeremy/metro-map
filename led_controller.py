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
    
    def is_initialized(self):
        """Check if LED strip is initialized."""
        return self.strip is not None

    def set_pixel(self, index, r, g, b):
        """Set color of a specific pixel.
        
        Args:
            index (int): LED index
            r (int): Red value (0-255)
            g (int): Green value (0-255)
            b (int): Blue value (0-255)
        """
        if self.strip and 0 <= index < self.LED_COUNT:
            self.strip.setPixelColor(index, Color(r, g, b))

    def set_pixels(self, indices, r, g, b):
        """Set multiple LEDs to the same color.
        
        Args:
            indices (list): List of LED indices to set
            r (int): Red value (0-255)
            g (int): Green value (0-255)
            b (int): Blue value (0-255)
        """
        for index in indices:
            self.set_pixel(index, r, g, b)

    def clear(self):
        """Turn off all LEDs."""
        if self.strip:
            for i in range(self.LED_COUNT):
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.show()

    def show(self):
        """Update the LED strip with all changes."""
        if self.strip:
            self.strip.show()
