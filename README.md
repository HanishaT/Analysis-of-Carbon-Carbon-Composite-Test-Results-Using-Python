# Tensile Test Data Analysis of a Carbon-Carbon Composite (Python)

During my MSc I tested carbon-carbon composites (CCC), and my thesis reports tensile results for three specimens. I wanted to go back to those numbers and look at them properly: how much do the specimens vary, how much of that could just be measurement error, and how close does my own 1D finite-element model come to the experiment?

This repository is my Python answer to those questions. It is a small, honest project, and I have tried to say clearly where it is limited.

Related project: [Finite-Element-Analysis-of-Carbon-Carbon-Composite-Tensile-Behaviour](https://github.com/HanishaT/Finite-Element-Analysis-of-Carbon-Carbon-Composite-Tensile-Behaviour)

## The data

`data/tensile_specimens.csv` is Table 1 from my thesis: the gauge width, thickness, area, ultimate load and tensile strength of three room-temperature specimens (T1, T2, T3). My thesis also has one hot-tensile result (108 MPa at 250 °C). I show it on the plot for comparison only, since it is a single specimen.

## What the script does

1. Recalculates the cross-section area (width x thickness) and the ultimate tensile strength (load / area), then compares them with the values in my thesis.
2. Works out the mean, the standard deviation and a 95 % confidence interval for the three specimens.
3. Estimates the measurement uncertainty with a Monte Carlo simulation, using assumed accuracies for the caliper and the load cell.
4. Compares my 1D finite-element prediction (90.65 MPa) with the experimental mean.
5. Draws one plot with everything on it.

## Results

| Quantity | Value |
| --- | --- |
| Mean tensile strength (3 specimens) | 90.99 MPa |
| Standard deviation | 6.29 MPa (about 6.9 %) |
| 95 % confidence interval of the mean | 75.4 to 106.6 MPa |
| Measurement uncertainty per specimen (assumed inputs) | about 0.9 MPa |
| 1D FEM prediction | 90.65 MPa, which is 0.38 % below the experimental mean |

The most useful thing I learned is that the differences between specimens (about 6 MPa) are roughly seven times larger than the measurement error I would expect (about 1 MPa). So the scatter comes mainly from the material itself and not from how I measured it.

![Result plot](results/tensile_uncertainty.png)

## Things to keep in mind

- **Only three specimens.** The confidence interval is wide because of that. I used the t-distribution on purpose, and I did not use a bootstrap, because with three values it would look more precise than it really is.
- **The measurement accuracies are assumptions.** I used 0.01 mm for the width and thickness and 1 % for the load. These are typical values, not the specifications of the machine I used. They are the first two settings at the top of the script, so they are easy to change.
- **The FEM comparison is not a full validation.** My model is a one-dimensional bar, so it is a check of my implementation more than a test of the physics.
- **No stress-strain curve.** My thesis only reports the final values, so I did not fit a modulus.
- **T1 area.** The thesis gives 200.38 mm2, but width times thickness is 200.86 mm2. I used width times thickness. It changes the strength by about 0.3 MPa.

## How to run it

```bash
pip install numpy pandas scipy matplotlib
python ccc_tensile_uncertainty.py
```

The plot and a table of the recalculated values are saved in the `results` folder.

## What I would like to do next

- Fit stress-strain curves and report the uncertainty of the modulus, if I can get the raw load-displacement data.
- Add a Weibull analysis once more specimens are tested.

Hanisha Thanikatchalam
