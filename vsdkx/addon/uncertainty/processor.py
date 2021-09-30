from scipy.stats import entropy
from vsdkx.core.interfaces import Addon, AddonObject


class UncertaintyProcessor(Addon):
    """
    Determines how uncertain was the model's detections in this image by
    calculating the per sample entropy. Given the entropy threshold
    (E.g. entropy on confidences 0.5 (person) - 0.5 (not a person) = 0.61)
    we divide the samples on high uncertainty and low uncertainty. We then
    check if the percentage of samples with high uncertainty exceeds the
    sensitivity threshold and return True as uncertain prediction,
    otherwise we consider that the model had high confidence in its
    predictions and we return False.
    """

    def __init__(self,
                 addon_config: dict, model_settings: dict,
                 model_config: dict, drawing_config: dict):
        super().__init__(addon_config, model_settings, model_config,
                         drawing_config)
        self._entropy_threshold = addon_config['entropy_threshold']
        self._sensitivity_ratio = addon_config['sensitivity_ratio']

    def post_process(self,
                     addon_object: AddonObject) -> AddonObject:
        """
        Calculates the uncertainty in the frame's predictions

        Args:
            addon_object (AddonObject): addon object containing information
            about frame and/or other addons shared data

        Returns:
            (AddonObject): addon object has updated information for frame,
            inference, result and/or shared information
        """
        inference = addon_object.inference

        high_entropy_samples = []

        # Calculate the per sample entropy on
        # (confidence_scores, 1 - confidence_scores)
        # and keep track of all samples with high entropy
        for sample in inference.scores:
            uncertainty = entropy([sample, 1 - sample])
            if uncertainty >= self._entropy_threshold:
                high_entropy_samples.append(uncertainty)

        # Get the percentage of the high entropy samples
        percentage_of_uncertainty = len(high_entropy_samples) / \
                                    len(inference.scores)
        # Verify if the prediction was uncertain
        uncertain_prediction = True \
            if percentage_of_uncertainty >= self._sensitivity_ratio else False

        print(f'Uncertainty percentage {percentage_of_uncertainty:.2f}% '
              f'Uncertain prediction {uncertain_prediction}')

        uncertainty_metadata_dict = {
            'uncertain_prediction': uncertain_prediction,
            'percentage_of_uncertainty': percentage_of_uncertainty,
            'amount_of_predictions': len(inference.scores),
            'sensitivity_ratio': self._sensitivity_ratio,
            'entropy_threshold': self._entropy_threshold
        }

        inference.extra['uncertainty'] = uncertainty_metadata_dict
        addon_object.inference = inference

        return addon_object
