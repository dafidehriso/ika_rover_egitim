# Module 11: Balance & Physics Corrections

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Status: PARTIALLY COMPLETE
Front caster balance stabilization has been fully implemented and verified. The mathematical geometry of the incline ramp was calculated and embedded into the world file; however, smooth physical traversal across the ramp transition lip remains to be empirically verified in an upcoming session.

---

## Issue 1: Pitching Forward During Acceleration & Camera Pointing Down

### Root Cause
In the initial baseline robot design ([Module 2](../02-kendi-robotunuzu-tasarlayin/README_EN.md)), a single passive caster wheel (`caster_wheel`) was located **exclusively at the rear** ($x = -0.2\text{ m}$).
The sensor payload (5 cameras + LiDAR) was mounted at the extreme front of the chassis ($x = +0.3\text{ m}$). With zero ground support beneath the front overhang, the front acted as an unconstrained cantilever beam. When the robot accelerated forward or turned, motor torque caused the chassis to pitch down, driving the camera optical axes into the ground and degrading visual mapping.

### Trade-Off Evaluation
- **Transitioning to 4WD / Skid-Steer:** Rejected. Four independently driven wheels introduce distinct kinematics, complex skid-slip friction in Gazebo, and higher turning resistance, sacrificing the simplicity of differential drive.

### Implemented Solution: 5-Point Planar Stability
Retaining the differential-drive architecture (2 active drive wheels), two new passive balance caster spheres were added beneath the front camera platform:
- `front_caster_left`: pose `(0.35, 0.15, 0.05)`
- `front_caster_right`: pose `(0.35, -0.15, 0.05)`

The rover now maintains **5 points of ground contact**: 2 active drive wheels + 1 rear caster + 2 front casters. Pitch oscillation during acceleration and braking is eliminated.

---

## Issue 2: Ramp Acting as an "Invisible Wall"

### Root Cause: Gazebo Box Rotation Geometry
In Gazebo, `<box>` primitive geometries rotate about their **geometric center of mass (origin)**.
When an inclined ramp box is rotated by pitch angle $\theta$, its two ends displace in opposite vertical directions.
- In the initial attempt, the ramp's entry edge floated approximately **30 cm above the ground floor**. As the robot approached, its wheels crashed into the vertical face of the box as if hitting a stone wall.
- Inverting the pitch sign merely flipped which end was airborne.

### Mathematical Analysis & Geometric Formulation
Formulas for the upper surface endpoints of an inclined box ([`rampa_hesapla.py`](./rampa_hesapla.py)):

$$z_{\text{entry\_top}} = z_{\text{center}} - \frac{L}{2} \sin(-\theta) + \frac{t}{2} \cos(\theta)$$
$$z_{\text{exit\_top}} = z_{\text{center}} + \frac{L}{2} \sin(-\theta) + \frac{t}{2} \cos(\theta)$$

Configured Parameters:
- Length: $L = 2.0\text{ m}$, Thickness: $t = 0.06\text{ m}$
- Pitch angle: $\theta = -0.06\text{ rad} \approx -3.44^\circ$
- Center origin: $x = 2.5\text{ m}$, $z = 0.03\text{ m}$

Calculated Values:
- **Entry Lip Upper Edge:** $z \approx 0.00\text{ cm}$ (The entry edge sits flush with the ground floor, eliminating any step barrier).
- **Exit Lip Upper Edge:** $z \approx 11.99\text{ cm}$.

```bash
# Run the geometric verification script:
python3 11-denge-ve-fizik-duzeltmeleri/rampa_hesapla.py
```

### ⚠️ Scope of Verification & Pending Empirical Testing
Achieving a flush entry threshold at $Z=0$ is mathematically verified. However, whether the rover cleanly surmounts the $12\text{ cm}$ exit elevation depends on dynamic factors beyond wheel radius ($10\text{ cm}$):
- Chassis belly ground clearance
- Passive caster clearance over the break-over edge
- Motor torque margins and reverse descent behavior

While this model is baked into [`ika_rover.world`](./ika_rover.world), **empirical driving verification across the ramp threshold remains to be conducted**.

---

## Module Files
- [`model.sdf`](./model.sdf): Final 5-point ground contact rover model.
- [`ika_rover.world`](./ika_rover.world): Complete circuit with enclosed corridors, flush ramp, and color targets.
- [`rampa_hesapla.py`](./rampa_hesapla.py): Verification script calculating geometric endpoint elevations.

---

## Next Up
Module 12: Autonomous Exploration and Navigation (Nav2 + `explore_lite`)
