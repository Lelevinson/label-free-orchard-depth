import torch
import torch.nn as nn
import torch.nn.functional as F


class _ConvBlock(nn.Module):
    """Conv + BatchNorm + ELU."""

    def __init__(self, in_ch, out_ch, stride=1):
        super(_ConvBlock, self).__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size=3, stride=stride, padding=1)
        self.norm = nn.BatchNorm2d(out_ch)
        self.act = nn.ELU(inplace=True)

    def forward(self, x):
        return self.act(self.norm(self.conv(x)))


class FeatureNet(nn.Module):
    """Small self-supervised image autoencoder for the feature-metric loss.

    Training-only helper (FeatDepth-style). It is NOT used at inference: depth
    inference still runs only the Lite-Mono encoder/depth decoder on a single RGB
    image. Given an image it returns ``(feature_map, reconstruction)`` where
    ``feature_map`` has ``num_ch`` channels at full input resolution and
    ``reconstruction`` is a 3-channel image used by the autoencoder reconstruction
    loss. The feature map is shaped (outside this module) by reconstruction +
    first-order discriminative + second-order convergent regularizers so that the
    feature-metric matching landscape has proper single-basin minima instead of the
    flat plateaus that raw photometric matching suffers in low-texture vegetation.
    """

    def __init__(self, num_ch=16):
        super(FeatureNet, self).__init__()
        self.enc1 = _ConvBlock(3, 16, stride=1)
        self.enc2 = _ConvBlock(16, 32, stride=2)
        self.enc3 = _ConvBlock(32, 32, stride=1)
        self.dec1 = _ConvBlock(32 + 16, 16, stride=1)
        self.feature_head = nn.Conv2d(16, num_ch, kernel_size=3, padding=1)
        self.recon_head = nn.Sequential(
            nn.Conv2d(num_ch, 16, kernel_size=3, padding=1),
            nn.ELU(inplace=True),
            nn.Conv2d(16, 3, kernel_size=3, padding=1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        e1 = self.enc1(x)            # full resolution, 16
        e2 = self.enc2(e1)           # 1/2 resolution, 32
        e3 = self.enc3(e2)           # 1/2 resolution, 32
        up = F.interpolate(
            e3, size=e1.shape[-2:], mode="bilinear", align_corners=False)
        dec = self.dec1(torch.cat([up, e1], dim=1))  # full resolution, 16
        feature = self.feature_head(dec)             # full resolution, num_ch
        recon = self.recon_head(feature)             # full resolution, 3
        return feature, recon
