import torch.nn as nn
import torch.nn.functional as F
from layers import Conv3x3


class MixtureHead(nn.Module):
    """Training-only mixture head for the TSOB-style boundary-uncertainty loss.

    Takes the decoder's scale-0 feature map and produces the parameters for a
    K=2 depth mixture: a depth offset (delta between the two hypotheses), two
    log-uncertainties, and a mixing logit. Not used at inference.
    """

    def __init__(self, num_ch_in):
        super(MixtureHead, self).__init__()
        mid = max(num_ch_in // 2, 16)
        self.conv1 = Conv3x3(num_ch_in, mid)
        self.act = nn.ELU(inplace=True)
        # 4 output channels: mu_delta, log_sigma_0, log_sigma_1, alpha_logit
        self.conv2 = Conv3x3(mid, 4)

    def forward(self, feat):
        return self.conv2(self.act(self.conv1(feat)))
