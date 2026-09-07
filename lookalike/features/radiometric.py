import numpy as np
import cv2

def compute_radiometric_features(sar_image_patch: np.ndarray, mask: np.ndarray) -> dict:
    """
    Computes radiometric contrast and boundary gradient sharpness.
    :param sar_image_patch: 2D numpy array of SAR backscatter values (0-255 or decibels).
    :param mask: Binary mask (1 for candidate slick, 0 for surrounding sea).
    """
    slick_pixels = sar_image_patch[mask == 1]
    
    # Create background buffer (ring around the slick)
    kernel = np.ones((15, 15), np.uint8)
    dilated_mask = cv2.dilate(mask.astype(np.uint8), kernel, iterations=2)
    buffer_mask = dilated_mask - mask
    sea_pixels = sar_image_patch[buffer_mask == 1]

    mean_slick = np.mean(slick_pixels) if len(slick_pixels) > 0 else 1e-5
    mean_sea = np.mean(sea_pixels) if len(sea_pixels) > 0 else 1e-5
    
    # Contrast ratio (Ratio of background backscatter to slick backscatter)
    contrast_ratio = mean_sea / mean_slick if mean_slick > 0 else 1.0

    # Gradient Sharpness using Sobel Operator
    sobelx = cv2.Sobel(sar_image_patch, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(sar_image_patch, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    
    # Extract mean gradient along the slick boundary
    boundary_mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    edge_gradient = np.mean(gradient_magnitude[boundary_mask == 1]) if np.any(boundary_mask) else 0.0

    return {
        "mean_contrast_ratio": round(float(contrast_ratio), 3),
        "edge_gradient_sharpness": round(float(edge_gradient), 3),
        "mean_slick_intensity": round(float(mean_slick), 2),
        "mean_background_intensity": round(float(mean_sea), 2)
    }