# Image generation prompt

The project asset was generated with the built-in OpenAI image generation tool. The user-provided image was used only as a visual reference and is not included in this repository.

```text
Use case: stylized-concept
Asset type: Codex Desktop pet pose board and sprite anchor
Primary request: Create an original fan-made chibi mascot named “菲比啾比”, using Image 1 only as a visual reference for the broad character traits and cute rounded proportions. Do not copy the source drawing pixel-for-pixel and do not include any exact insignia or trademark.
Input images: Image 1: visual reference only, not an edit target
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for local background removal
Subject: the same single chibi girl consistently shown in exactly nine full-body poses. She has very long pale-blonde hair, large violet eyes, a soft navy-and-white sailor-style beret, one small blue hair clip, a bright blue scarf, and a simplified black-and-white coder-priest outfit with original details.
Pose layout: a clean 3 by 3 pose board, read left to right and top to bottom: idle breathing; running right; running left; waving hello; joyful jump; failed or flustered; waiting for user input; actively coding at a tiny dark laptop; presenting finished work for review.
Style/medium: polished flat-color chibi game sprite illustration, bold dark outline, soft cel shading, crisp silhouette, readable at 192×208 pixels
Composition/framing: square canvas; exactly nine characters arranged evenly in a 3×3 layout without visible panel borders; each pose fully contained in its own equal area; generous separation and padding; consistent character scale and outfit
Color palette: pale blonde, violet, deep navy, white, black, one bright blue accent
Constraints: background must be one perfectly uniform #00ff00 color with no shadows, gradients, texture, reflections, floor plane, or lighting variation; no cast shadow; no contact shadow; no green inside the character; no text; no letters; no numbers; no captions; no watermark; no logos; no grid lines; no extra characters; no cropped limbs; no overlapping poses; preserve the same face, hair, outfit, palette, and proportions across all nine poses
```

The chroma-key source was converted locally with the image-generation skill's installed `remove_chroma_key.py` helper. `scripts/build_assets.py` then crops the nine poses, creates the official animation rows, and packs the lossless WebP atlas.
