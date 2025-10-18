🪐 Gravitational Slingshot Simulator 🪐

This project models the **gravitational slingshot (gravity assist)** maneuver — the process through which a spacecraft gains energy by passing near a moving planet.  
The simulation investigates how entry velocity, deflection angle, and planetary motion influence the resulting exit velocity of a spacecraft. It compares the modeled relationships with real orbital data from NASA’s Voyager missions, offering an accessible visualization of momentum exchange in spaceflight.

---

Overview

Using **Python** and **Matplotlib**, the simulation visualizes how:
- **Entry velocity** (`v₁`)
- **Deflection angle** (`θ`)
- **Planet orbital speed** (`U`)

influence the **exit velocity** (`v₂`) of a spacecraft after the slingshot interaction.

The program implements a 2D vector-based approach derived from the theoretical conservation of energy and momentum in the Sun–planet–probe system.

---

 Core Equation The simulator computes the heliocentric exit velocity based on vector addition of velocities:

v₂ = √(v₁² + U² + 2·U·v₁·cos(θ)) 
where  
- `v₁` = entry velocity of the spacecraft  
- `U` = planet’s orbital velocity  
- `θ` = approach angle relative to the planet’s direction of motion  
- `v₂` = heliocentric exit velocity

This represents the heliocentric exit velocity as a function of the probe’s entry velocity, planet orbital velocity, and deflection angle.

---

Run the Simulation

```bash
pip install -r requirements.txt
python main.py

🪐🪐🪐🪐
