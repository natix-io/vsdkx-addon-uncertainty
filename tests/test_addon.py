import numpy as np
import unittest

from vsdkx.core.structs import AddonObject, Inference
from vsdkx.addon.uncertainty.processor import UncertaintyProcessor


class TestAddon(unittest.TestCase):
    addon_config = {
        "entropy_threshold": 0.67,
        "sensitivity_ratio": 0.10
    }

    model_config = {
        "filter_class_ids": [0]
    }

    def test_post_process(self):
        addon_processor = UncertaintyProcessor(self.addon_config, {}, self.model_config, {})

        frame = (np.random.rand(640, 640, 3) * 100).astype('uint8')
        inference = Inference()

        bb_1 = np.array([120, 150, 170, 200])
        score_1 = 0.51
        bb_2 = np.array([100, 130, 150, 180])
        score_2 = 0.81

        inference.boxes.append(bb_1)
        inference.scores.append(score_1)

        test_object = AddonObject(frame=frame, inference=inference, shared={})
        result = addon_processor.post_process(test_object)

        self.assertNotIn('uncertainty', result.inference.extra)

        inference.boxes.append(bb_2)
        inference.scores.append(score_2)

        test_object = AddonObject(frame=frame, inference=inference, shared={})
        result = addon_processor.post_process(test_object)

        self.assertIn('uncertainty', result.inference.extra)
        self.assertEqual(result.inference.extra['uncertainty']['uncertain_prediction'], True)


if __name__ == '__main__':
    unittest.main()
