import os
from PIL import Image
import numpy as np
from pillow_heif import register_heif_opener

# Register HEIF opener
register_heif_opener()

# Create a simple test image (gradient pattern)
width, height = 400, 300
image_array = np.zeros((height, width, 3), dtype=np.uint8)

# Create a gradient pattern
for y in range(height):
    for x in range(width):
        image_array[y, x] = [
            int(255 * x / width),  # Red channel
            int(255 * y / height),  # Green channel
            128  # Blue channel (constant)
        ]

# Create PIL Image
img = Image.fromarray(image_array, 'RGB')

# Save as HEIC without EXIF data
output_path = "test_no_exif.heic"
img.save(output_path, "HEIF", quality=90)

print(f"Created test HEIC image: {output_path}")
print(f"Image size: {width}x{height}")
print("This image has no EXIF data.")

# Verify no EXIF data
test_img = Image.open(output_path)
exif = test_img.getexif()
if exif:
    print(f"Warning: Image has EXIF data: {dict(exif)}")
else:
    print("Confirmed: No EXIF data in the image.") 