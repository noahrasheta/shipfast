#!/usr/bin/env python3
"""
Generate images using the Nano Banana Pro (Gemini 3 Pro) API.

Usage:
    python generate-image.py --prompt "A detailed scene..." --output "output.png"
    python generate-image.py --prompt "..." --output "output.png" --aspect-ratio "16:9" --resolution "2K"
    python generate-image.py --prompt "..." --output "output.png" --reference-images "ref1.png,ref2.png"

Requirements:
    pip install google-genai Pillow python-dotenv

Environment:
    GEMINI_API_KEY must be set in environment or .env file
"""

import argparse
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from google import genai
from google.genai import types
from PIL import Image


def generate_image(prompt, output_path, aspect_ratio="16:9", resolution="2K", reference_images=None):
    """Generate an image using the Gemini 3 Pro Image API."""

    # Load environment variables from .env if available
    if load_dotenv:
        load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set. Add it to your .env file or set it in your environment.", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build contents list
    contents = []

    # Add reference images first if provided
    if reference_images:
        for ref_path in reference_images:
            ref_path = ref_path.strip()
            if os.path.exists(ref_path):
                contents.append(Image.open(ref_path))
                print(f"  Reference image loaded: {ref_path}")
            else:
                print(f"  WARNING: Reference image not found, skipping: {ref_path}", file=sys.stderr)

    # Add the text prompt
    contents.append(prompt)

    # If no reference images were added, pass prompt as plain string
    if len(contents) == 1:
        contents = prompt

    # Configure generation
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=resolution,
        ),
    )

    # Generate
    print(f"  Model: gemini-3-pro-image-preview")
    print(f"  Aspect ratio: {aspect_ratio} | Resolution: {resolution}")
    print(f"  Generating...")

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=config,
    )

    # Process response
    image_saved = False
    for part in response.parts:
        if hasattr(part, "thought") and part.thought:
            # Skip thinking/interim parts
            continue
        if part.text is not None:
            print(f"  Model note: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()

            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            image.save(output_path)
            print(f"  SUCCESS: Image saved to {output_path}")
            image_saved = True

    if not image_saved:
        print("ERROR: No image was generated. The prompt may have triggered a safety filter or the API returned no image data.", file=sys.stderr)
        sys.exit(1)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate images with Nano Banana Pro (Gemini 3 Pro) API")
    parser.add_argument("--prompt", required=True, help="Narrative prompt describing the image to generate")
    parser.add_argument("--output", required=True, help="Output file path (e.g., outputs/concept-v1-faithful.png)")
    parser.add_argument("--aspect-ratio", default="16:9",
                        help="Aspect ratio: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 (default: 16:9)")
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"],
                        help="Resolution: 1K, 2K, or 4K — MUST be uppercase (default: 2K)")
    parser.add_argument("--reference-images", default=None,
                        help="Comma-separated paths to reference images (up to 14 for Gemini 3 Pro)")

    args = parser.parse_args()

    # Parse reference images
    ref_images = None
    if args.reference_images:
        ref_images = [p.strip() for p in args.reference_images.split(",") if p.strip()]

    generate_image(
        prompt=args.prompt,
        output_path=args.output,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        reference_images=ref_images,
    )


if __name__ == "__main__":
    main()
