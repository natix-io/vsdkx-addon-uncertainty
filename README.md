# vsdkx-addon-uncertainty

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