import unittest

import time
import numpy as np
from tensorpack.dataflow.common import TestDataSpeed

from data_feeder import CellImageData, get_default_dataflow, master_dir_train, get_default_dataflow_batch


class DataFeederTest(unittest.TestCase):
    def test_image_data(self):
        # 256, 320, 3, mask=15
        t = time.time()
        d = CellImageData('a6515d73077866808ad4cb837ecdac33612527b8a1041e82135e40fce2bb9380', path=master_dir_train)
        dt = time.time() - t
        # print(dt)

        # image test
        self.assertListEqual(
            list(d.image(is_gray=False).shape),
            [256, 320, 3]
        )
        self.assertListEqual(
            list(d.image(is_gray=True).shape),
            [256, 320, 1]
        )
        self.assertEqual(d.img.dtype, np.uint8)
        self.assertEqual(d.masks[0].dtype, np.uint8)

        # multi mask
        self.assertListEqual(
            list(d.multi_masks().shape),
            [256, 320, 15]
        )

        self.assertListEqual(
            list(d.multi_masks_batch().shape),
            [256, 320, 1]
        )
        self.assertEqual(np.max(d.multi_masks_batch()), 15)

        # single mask
        self.assertListEqual(
            list(d.single_mask().shape),
            [256, 320, 1]
        )
        self.assertEqual(np.max(d.single_mask()), 1)

        origin_masks = CellImageData.batch_to_multi_masks(d.multi_masks_batch())
        self.assertTrue(d.multi_masks().dtype == origin_masks.dtype)
        self.assertEqual(d.multi_masks().shape, origin_masks.shape)
        self.assertTrue(np.array_equal(d.multi_masks(), origin_masks))

        # multi mask with one mask
        d.masks = [d.masks[0]]
        self.assertListEqual(
            list(d.multi_masks().shape),
            [256, 320, 1]
        )
        self.assertEqual(np.max(d.multi_masks()), 1)

    def test_default_ds(self):
        ds = get_default_dataflow()

        t = time.time()
        for idx, dp in enumerate(ds.get_data()):
            self.assertListEqual(
                list(dp[0].image(is_gray=False).shape),
                [224, 224, 3]
            )
            if idx > 100:
                break

        t = time.time()
        TestDataSpeed(ds, size=100).start()
        dt = time.time() - t
        self.assertLessEqual(dt, 2.0)

    def test_default_ds_batch(self):
        ds_batch = get_default_dataflow_batch(batchsize=16)
        for idx, dp in enumerate(ds_batch.get_data()):
            input_batch, mask_batch, multi_masks = dp
            self.assertListEqual(
                list(input_batch.shape),
                [16, 224, 224, 1]
            )
            self.assertListEqual(
                list(multi_masks.shape),
                [16, 224, 224, 1]
            )
            self.assertLessEqual(np.max(input_batch), 1.0)
            self.assertGreaterEqual(np.max(input_batch), 0.0)
            if idx > 10:
                break

        t = time.time()
        TestDataSpeed(ds_batch, size=10).start()
        dt = time.time() - t
        self.assertLessEqual(dt, 10.0)

