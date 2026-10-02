"""
Tolerant screenshot comparison.

Exact pixel equality breaks across platforms (shaders, drivers, anti-aliasing), so screenshots are compared
with SSIM at two levels:
- Global: the mean SSIM over the image must stay high.
- Local: no connected region of low-SSIM pixels may be large, so a small missing or wrong object is still caught
  even though it barely moves the mean.
SSIM is computed per colour channel and the worst channel is used per pixel, so colour-only changes are caught.
"""

from dataclasses import dataclass

import numpy as np
from scipy import ndimage
from skimage.metrics import structural_similarity

# Thresholds calibrated against two Windows baselines: comparing the same item across these gives a mean SSIM
# of at least 0.997 and bad regions of at most 35 px, while the closest pair of different items (LightBlock vs
# HeavyBlock) has a bad region of 130 px. The mean is only a backstop for whole-scene changes: different items can
# still score 0.9995, so the local check does the real work.
MIN_MEAN_SSIM = 0.99
LOCAL_SSIM_CUTOFF = 0.7  # A pixel is "bad" if its local SSIM is below this
MAX_BAD_REGION_PIXELS = 64  # The largest connected region of bad pixels allowed (an 8x8 patch)


@dataclass
class ScreenshotComparison:
    mean_ssim: float
    largest_bad_region: int
    ssim_map: np.ndarray  # (H, W), worst channel per pixel

    @property
    def passed(self) -> bool:
        return (
            self.mean_ssim >= MIN_MEAN_SSIM
            and self.largest_bad_region <= MAX_BAD_REGION_PIXELS
        )

    def __str__(self) -> str:
        return (
            f"mean SSIM {self.mean_ssim:.4f} (min {MIN_MEAN_SSIM}), "
            f"largest bad region {self.largest_bad_region} px (max {MAX_BAD_REGION_PIXELS})"
        )


def compare_screenshots(expected: np.ndarray, observed: np.ndarray) -> ScreenshotComparison:
    """Compare two (H, W, C) float images with values in [0, 1]."""
    if expected.shape != observed.shape:
        raise ValueError(f"Screenshot shapes differ: expected {expected.shape}, observed {observed.shape}")
    # Fixed data_range: the camera output is always in [0, 1], whatever is in the frame
    _, ssim_map = structural_similarity(
        expected, observed, channel_axis=2, data_range=1.0, full=True
    )
    worst_channel_map = ssim_map.min(axis=2)
    labels, region_count = ndimage.label(worst_channel_map < LOCAL_SSIM_CUTOFF)
    largest_bad_region = (
        int(np.bincount(labels.ravel())[1:].max()) if region_count > 0 else 0
    )
    return ScreenshotComparison(
        mean_ssim=float(worst_channel_map.mean()),
        largest_bad_region=largest_bad_region,
        ssim_map=worst_channel_map,
    )
