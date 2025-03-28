import os
import numpy as np
import imageio.v3 as iio
import json

# === Input and Output ===
input_path = "/home/mrthermometry/Devel/phase-generative-inpainting/examples/output_unwrap.png"
output_path = "/home/mrthermometry/Devel/phase-generative-inpainting/examples/output_unwrap_phase.png"
metadata_path = "/home/mrthermometry/Devel/phase-generative-inpainting/examples/unwrapped_metadata.json"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# === Load metadata JSON ===
with open(metadata_path, 'r') as f:
    metadata = json.load(f)

# Get filename only (no path) to match key in metadata
filename = os.path.basename(input_path)
if filename not in metadata:
    raise KeyError(f"{filename} not found in metadata JSON")

unwrapped_min = metadata[filename]["unwrapped_min"]
unwrapped_max = metadata[filename]["unwrapped_max"]
print(f"[INFO] Loaded metadata: min={unwrapped_min:.4f}, max={unwrapped_max:.4f}")

# === Load the image ===
image_16bit = iio.imread(input_path).astype(np.float64)

# If image is RGB, convert to grayscale
if image_16bit.ndim == 3 and image_16bit.shape[2] == 3:
    print("Converting RGB to grayscale...")
    image_16bit = image_16bit[:, :, 0]

print(f"[INFO] Loaded image shape: {image_16bit.shape}")
print(f"[INFO] Raw 16-bit range: min={image_16bit.min()}, max={image_16bit.max()}")

# Normalize to [0, 1]
image_scaled = image_16bit / 65535.0
print(f"[INFO] Image scaled to [0,1] range: min={image_scaled.min():.4f}, max={image_scaled.max():.4f}")

# Rescale to original unwrapped range
unwrapped = image_scaled * (unwrapped_max - unwrapped_min) + unwrapped_min
print(f"[INFO] Unwrapped range: min={unwrapped.min():.4f}, max={unwrapped.max():.4f}")

# === Wrap phase to [-π, π]
wrapped = (unwrapped + np.pi) % (2 * np.pi) - np.pi
print(f"[INFO] Wrapped range: min={wrapped.min():.4f}, max={wrapped.max():.4f}")

# Normalize to [0,1] and convert to 16-bit
wrapped_scaled = (wrapped + np.pi) / (2 * np.pi)
wrapped_16bit = (wrapped_scaled * 65535).astype(np.uint16)

# Ensure 2D before saving
wrapped_16bit = np.squeeze(wrapped_16bit)
if wrapped_16bit.ndim != 2:
    raise ValueError(f"Expected 2D grayscale image, got shape: {wrapped_16bit.shape}")

# === Save result
iio.imwrite(output_path, wrapped_16bit)
print(f"Wrapped image saved to: {output_path}")

