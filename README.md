# 2.5D Daisyworld: A Climate–Biosphere Feedback Simulation

**2.5D Daisyworld** is a scientific simulation designed to explore climate–biosphere feedback processes inspired by the **Gaia hypothesis** and the original **Daisyworld** conceptual model. It provides a configurable and visual framework to examine how organisms modify their environment to maintain habitability.

This project is implemented using Python and Pygame, with physically-motivated thermal and ecological parameterizations. :contentReference[oaicite:0]{index=0}

---

## Scientific Overview

In Daisyworld systems:

- Surface albedo changes based on organism (daisy) coverage
- Temperature affects growth and mortality
- Biota-climate interactions form **stabilizing or destabilizing feedback loops** :contentReference[oaicite:1]{index=1}
- Environmental equilibrium emerges from local interactions rather than external control

This version extends the classic model:

✔ 2.5D heat-field visualization  
✔ Day–night spatial progression  
✔ Adjustable solar forcing  
✔ Dynamic growth and mortality  
✔ Visual performance indicators (land cover, growth rate, temperature history)  
:contentReference[oaicite:2]{index=2}

---

## Key Features

- **Interactive environmental manipulation**
- **Configurable physical and ecological settings**
- **Local heat diffusion with spatial heterogeneity**
- **Real-time diagnostics for model behavior**

Users can explore climate resilience, thermal sensitivity, ecological thresholds, and nonlinear tipping points.

---

## Model Parameters (Selected)

| Parameter | Category | Description |
|----------|----------|-------------|
| `SUN_SCREENING` | Radiation | Incoming solar flux |
| `ALBEDO_*` | Surface properties | Reflectivity of black/white daisies, soil, water |
| `T_OPTIMAL`, `T_TOL_LOW/HIGH` | Biology | Growth dependence on temperature |
| `HEATING_RATE` | Thermodynamics | Relaxation to solar-driven equilibrium |
| `SPREAD_CHANCE`, `DEATH_CHANCE` | Ecology | Colonization and mortality probabilities |
| `INFLUENCE_LEVEL` | Physics | Neighborhood radius for diffusion and spread |
| `DAY_BORDER_SPEED` | Diurnal cycle | Velocity of day–night terminator |  
:contentReference[oaicite:3]{index=3}

All parameters are documented within the project and many can be modified during simulation runtime via an interface. :contentReference[oaicite:4]{index=4}

---

## System Requirements

- Python 3.x
- Pygame ≥ 2.6.1
- Anaconda recommended for environment management  
  (as used during development) :contentReference[oaicite:5]{index=5}

---

## How to Run

1. Extract distribution package (`DAYNIGHT_PACKED.zip`)
2. Launch the main Python script
3. Configure environmental conditions and observe system evolution  
   :contentReference[oaicite:6]{index=6}

---

## Example Research Questions

- How do organisms stabilize global temperatures under reduced solar input?
- What happens when mortality slightly exceeds growth?
- How fast does the environment recover after a thermal perturbation?
- Under what parameter regimes does Daisyworld collapse?

This makes the model suitable for **climate science coursework**, **research demonstrations**, and **complex systems studies**.

---

## References

Key scientific foundations include:
- Lovelock & Margulis (1974) — The Gaia Hypothesis
- Lovelock & Watson (1983) — Biological homeostasis in Daisyworld
- Additional citations provided in the documentation  
  :contentReference[oaicite:7]{index=7}

---

## Project Status

> Active prototype designed for research and educational use.  
> Additional environmental cycles (e.g., hydrology) planned for future versions.  
> Current water representation is placeholder-only. :contentReference[oaicite:8]{index=8}

---

## Author

**Minh Khanh Luong**  
Department of Earth & Atmospheric Science

---

### Explore emergent climate regulation through interactive ecological physics.
