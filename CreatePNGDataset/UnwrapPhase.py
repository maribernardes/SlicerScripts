import os
import numpy as np
import imageio.v2 as iio
from skimage.restoration import unwrap_phase
import json

# === Configuration ===
#input_folder = '/home/mrthermometry/Datasets/MWALiver/phase_2D'
#output_folder = '/home/mrthermometry/Datasets/MWALiver/unwrapped_phase_2D'

input_folder = "/home/mrthermometry/Devel/phase-generative-inpainting/examples/LiverMWA"
output_folder = "/home/mrthermometry/Devel/phase-generative-inpainting/examples/LiverMWA"
metadata_path = os.path.join(output_folder, 'unwrapped_metadata.json')

os.makedirs(output_folder, exist_ok=True)

# === Metadata dictionary ===
metadata = {}

# === Processing Loop ===
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".png"):
        input_path = os.path.join(input_folder, filename)
        print(f"Processing: {filename}")

        # Load 16-bit image
        image = iio.imread(input_path).astype(np.float64)

        # Normalize to [-pi, pi]
        image_norm = (image / 65535.0) * 2 * np.pi - np.pi

        # Unwrap the phase
        unwrapped = unwrap_phase(image_norm)

        # Save unwrapped min/max for this image
        unwrapped_min = float(np.min(unwrapped))
        unwrapped_max = float(np.max(unwrapped))
        metadata[filename] = {
            "unwrapped_min": unwrapped_min,
            "unwrapped_max": unwrapped_max
        }

        # Normalize unwrapped for saving
        unwrapped_scaled = (unwrapped - unwrapped_min) / (unwrapped_max - unwrapped_min)
        unwrapped_16bit = (unwrapped_scaled * 65535).astype(np.uint16)

        # Save image
        output_path = os.path.join(output_folder, f"unwrapped_{filename}")
        iio.imwrite(output_path, unwrapped_16bit)

# === Save metadata JSON ===
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)

print(f"All images processed and saved with metadata at: {metadata_path}")

