# Research Questions

## Primary
RQ1. How do CPU-friendly classical ML regressors compare for estimating manual crack width (MANwidth) from 501-point brightness profiles under group-aware evaluation?

RQ2. How sensitive are the models to controlled brightness, contrast, noise, and smoothing perturbations applied to held-out profiles?

## Conditional follow-up
RQ3. If performance or feature distributions vary across Series, can a small target-domain calibration/fine-tuning budget improve generalization to unseen groups?

## Hypotheses (to be refined after data audit)
H1. At least one nonlinear model will outperform a simple linear/dummy baseline on held-out groups.
H2. Synthetic profile perturbations will degrade performance to varying degrees across model families.
H3. If measurable inter-Series shift exists, limited target-domain adaptation may improve target-Series performance.

Do not treat these hypotheses as results. Report null/negative findings honestly.
