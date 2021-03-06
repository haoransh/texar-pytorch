"""
Unit tests for conv encoders.
"""
import unittest

import torch
from torch import nn

import texar as tx
from texar.modules.encoders.conv_encoders import Conv1DEncoder


class Conv1DEncoderTest(unittest.TestCase):
    """Tests :class:`~texar.modules.Conv1DEncoder` class.
    """

    def test_encode(self):
        """Tests encode.
        """
        inputs_1 = torch.ones([128, 32, 300])
        encoder_1 = Conv1DEncoder(in_channels=inputs_1.shape[1],
                                  in_features=inputs_1.shape[2])
        self.assertEqual(len(encoder_1.layers), 4)
        self.assertTrue(isinstance(encoder_1.layer_by_name("MergeLayer"),
                                   tx.core.MergeLayer))
        for layer in encoder_1.layers[0].layers:
            self.assertTrue(isinstance(layer, nn.Sequential))

        outputs_1 = encoder_1(inputs_1)
        self.assertEqual(outputs_1.shape, torch.Size([128, 256]))

        inputs_2 = torch.ones([128, 64, 300])
        hparams = {
            # Conv layers
            "num_conv_layers": 2,
            "out_channels": 128,
            "kernel_size": [[3, 4, 5], 4],
            "other_conv_kwargs": {"padding": 0},
            # Pooling layers
            "pooling": "AvgPool1d",
            "pool_size": 2,
            "pool_stride": 1,
            # Dense layers
            "num_dense_layers": 3,
            "out_features": [128, 128, 10],
            "dense_activation": "ReLU",
            "other_dense_kwargs": None,
            # Dropout
            "dropout_conv": [0, 1, 2],
            "dropout_dense": 2
        }
        network_2 = Conv1DEncoder(in_channels=inputs_2.shape[1],
                                  in_features=inputs_2.shape[2],
                                  hparams=hparams)
        # dropout-merge-dropout-conv-avgpool-dropout-flatten-
        # (Sequential(Linear,ReLU))-(Sequential(Linear,ReLU))-dropout-linear
        self.assertEqual(len(network_2.layers), 1 + 1 + 1 + 3 + 4 + 1)
        self.assertTrue(isinstance(network_2.layer_by_name("MergeLayer"),
                                   tx.core.MergeLayer))
        for layer in network_2.layers[1].layers:
            self.assertTrue(isinstance(layer, nn.Sequential))

        outputs_2 = network_2(inputs_2)
        self.assertEqual(outputs_2.shape, torch.Size([128, 10]))


if __name__ == "__main__":
    unittest.main()
