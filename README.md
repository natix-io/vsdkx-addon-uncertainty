# Modeling Uncertainty
This addon determines how uncertain was the model's detections in this image by calculating the per sample entropy. Given the entropy threshold (e.g. entropy on confidences 0.5 (person) - 0.5 (not a person) = 0.61) we divide the samples on high uncertainty and low uncertainty. We then check if the percentage of samples with high uncertainty exceeds the sensitivity threshold and return True as uncertain prediction, otherwise we consider that the model had high confidence in its predictions and we return False.

### Addon Config
```yaml
  uncertainty:
    class: vsdkx.addon.uncertainty.processor.UncertaintyProcessor
    entropy_threshold: 0.67
    sensitivity_ratio: 0.10
```
where:
- `entropy_threshold` (`float`): It accepts values between 0 - 1, and it defaults to `0.67` as described in section [Uncertainty measurement](#uncertainty-measurement)
- `sensitivity_ratio` (`float`): It accepts values between 0 - 1, and it can be considered as a percentage of sensitivity. E.g. `0.10` ration would translate to 10% of bounding boxes predicted with a low confidence score.

## Debug
Example of object initialization and `post_process`:
```python
from vsdkx.addon.uncertainty.processor import UncertaintyProcessor

add_on_config = {
  'entropy_threshold': 0.67, 
  'sensitivity_ratio': 0.1, 
  'class': 'vsdkx.addon.uncertainty.processor.UncertaintyProcessor'
  }
model_config = {
    'classes_len': 1, 
    'filter_class_ids': [0], 
    'input_shape': [640, 640], 
    'model_path': 'vsdkx/weights/ppl_detection_retrain_training_2.pt'
    }
    
model_settings = {
    'conf_thresh': 0.5, 
    'device': 'cpu', 
    'iou_thresh': 0.4
    }  
  
uncertainty = UncertaintyProcessor(addon_on_config, model_settings, model_config)

addon_object = AddonObject(
    frame=np.array(), dtype=uint8), 
    inference=Inference(
        boxes=[array([2007,  608, 3322, 2140]), array([ 348,  348, 2190, 2145])], 
        classes=[array([0], dtype=object), array([0], dtype=object)], 
        scores=[array([0.799637496471405], dtype=object), array([0.6711544394493103], dtype=object)], 
        extra={
          'tracked_objects': 0, 
          'zoning': {'zone_0': {'Person': [], 'Person_count': 0, 'objects_entered': {'Person': [], 'Person_count': 0},
          'objects_exited': {'Person': [], 'Person_count': 0}}, 'rest': {'Person': [], 'Person_count': 0}}, 
          'current_speed': {}, 
          'current_action': {}}), 
    shared={
      'trackable_objects': {}, 
      'trackable_objects_history': {0: {'object_id': 0}, 1: {'object_id': 1}}})

addon_object = uncertainty.post_process(addon_object)
```

The `post_process()` calculates the uncertainty in the frame's predictions, and it receives and returns the following:

- **Input**: (`Dict`) - `addon_object.inference` with main interest on the `list` of `addon_object.inference.scores`
- **Output**: (`Dict`) - `addon_object` where the uncertainty result is a a `boolean` that is appended to the `addon_object` dictionary as `addon_object.inference.extra['uncertainty']` .

## Uncertainty measurement

For every detected object, we calculate the `entropy` on two classes (`person`, `not a person`) based on the detected object's confidence score. Since people detection is trained only on one class (`person`), we calculate the `not a person` class by `1 - object's confidence score`. This results to two probabilities per detected object, and one entropy result. Thus, the uncertainty is given by: 

```
entropy([confidence, 1-confidence])
```

Given the observation that:

```markdown
entropy([0.50, 0.50]) -->  0.69
entropy([0.55, 0.45]) -->  0.68
entropy([0.65, 0.35]) -->  0.64
entropy([0.70, 0.30]) -->  0.61
entropy([0.80, 0.20]) -->  0.50
entropy([0.90, 0.10]) -->  0.32
```

This add-on accepts two configurable properties:
- `entropy_threshold` -  Defaults to `0.67`
- `sensitivity_ratio` - Defaults to `0.10`  

The `entropy_threshold` threshold considers all detections that have a confidence score lower than `0.60`. **To include low confidence predictions, we recommend when using this add-on to reduce the model's `conf_threshold` in `settings.yaml` from `0.70` to `0.50`.**

In every image detection, we store in a list every sample we've encountered with a higher entropy than the `entropy_threshold`. We then calculate the percentage of the high entropy samples observed in the detections of this image. A `sensitivity_ratio` (configurable in `settings.yaml`, currently defaults to 0.10 - aka 10% of the detected objects per image which is **very sensitive**) determines if the high entropy samples are higher than the `sensitivity_ratio`, and returns if high uncertainty was detected as `True|False`. 
