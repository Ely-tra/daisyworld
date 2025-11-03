# 2.5D Daisyworld: A Climate–Biosphere Feedback Simulation

**2.5D Daisyworld** is a scientific simulation designed to explore climate–biosphere feedback processes inspired by the **Gaia hypothesis** and the original **Daisyworld** conceptual model. It provides a configurable and visual framework to examine how organisms modify their environment to maintain habitability.

This project is implemented using Python and Pygame, with physically-motivated thermal and ecological parameterizations.

---

## How to Run

1. Extract distribution package (`DAYNIGHT_PACKED.zip`)
2. Launch the main Python script
3. Configure environmental conditions and observe system evolution  
---

## Scientific Overview

In Daisyworld systems:

- Surface albedo changes based on organism (daisy) coverage
- Temperature affects growth and mortality
- Biota-climate interactions form **stabilizing or destabilizing feedback loops** 
- Environmental equilibrium emerges from local interactions rather than external control

This version extends the classic model:

✔ 2.5D heat-field visualization  
✔ Day–night spatial progression  
✔ Adjustable solar forcing  
✔ Dynamic growth and mortality  
✔ Visual performance indicators (land cover, growth rate, temperature history)  


---

## Key Features

- **Interactive environmental manipulation**
- **Configurable physical and ecological settings**
- **Local heat diffusion with spatial heterogeneity**
- **Real-time diagnostics for model behavior**

Users can explore climate resilience, thermal sensitivity, ecological thresholds, and nonlinear tipping points.

---

## 🔧 Configurable Parameters

| Parameter | Category | Description |
|----------|----------|-------------|
| `map_width` | Display / Grid | World width in pixels; sets number of horizontal cells |
| `map_height` | Display / Grid | World height in pixels; sets number of vertical cells |
| `temp_thickness` | Visualization | Vertical exaggeration of temperature overlay bars |
| `overlay_shift_x`, `overlay_shift_y`, `overlay_shift_z` | Visualization | Pixel offsets for aligning and stacking heat overlay layers |
| `T_space` | Thermodynamics | Ambient reference temperature for cooling term |
| `INITIAL_TEMPERATURE` | Thermodynamics | Starting temperature for all non-water cells |
| `HEATING_RATE` | Thermodynamics | Rate of adjustment toward solar-heated equilibrium |
| `HEAT_DIFFUSION_COEFFICIENT` | Thermodynamics | Legacy parameter — not used in current version |
| `COOLING_COEFFICIENT` | Thermodynamics | Radiative cooling coefficient (Stefan–Boltzmann-style) |
| `SUN_SCREENING` | Radiation | Incoming solar flux (similar to solar constant) |
| `ALBEDO_BLACK` | Surface / Radiation | Reflectivity of black daisies — low albedo → heat absorption |
| `ALBEDO_WHITE` | Surface / Radiation | Reflectivity of white daisies — high albedo → cooling |
| `ALBEDO_BARE` | Surface / Radiation | Reflectivity of bare soil |
| `ALBEDO_WATER` | Surface / Radiation | Reflectivity of water tiles |
| `T_OPTIMAL` | Biology | Temperature maximizing daisy growth |
| `T_TOL_LOW`, `T_TOL_HIGH` | Biology | Growth drop-off when too cold / too hot |
| `SPREAD_CHANCE` | Biology | Colonization probability for empty adjacent cells |
| `DEATH_CHANCE` | Biology | Mortality probability per timestep |
| `INFLUENCE_LEVEL` | Interaction Scale | Neighborhood size for spread + heat diffusion (1 = 4-way, 2 = 8-way, >2 = circular) |
| `CUM_MOR_NET` | Diagnostics | History window for cumulative mortality graph |
| `DAY_BORDER_SPEED` | Diurnal Cycle | Speed of moving day-night boundary |
| `DAY_PERIOD` | Diurnal Cycle | Deprecated — replaced by `DAY_BORDER_SPEED` |
| `THRESHOLD` | Stability / Numerics | Prevents divide-by-zero / unrealistic gradients |
| `THRESHOLD_TMID` | Stability / Numerics | Convergence threshold for equilibrium temperature solver |
| `MAX_ITERS_TMID` | Stability / Numerics | Max iterations before solver aborts |

### 🔄 Parameters Adjustable During Simulation

- Solar irradiance (`SUN_SCREENING`)
- Maximum growth response (`T_OPTIMAL` and tolerance range)
- Simulation time-flow speed
- Screen position of temperature overlay (`overlay_shift_*`)


---

## System Requirements

- Python 3.x
- Pygame ≥ 2.6.1
- Anaconda recommended for environment management  
  (as used during development) 


---

## Author

**Minh Khanh Luong**  
Indiana University, Department of Earth & Atmospheric Science

---
