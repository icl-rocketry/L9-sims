import os
import sys
import io
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# modules
from rocketpy import Environment, Flight, MonteCarlo, GenericMotor
from rocketpy.stochastic import (
    StochasticEnvironment,
    StochasticRocket,
    StochasticFlight,
    StochasticNoseCone,
    StochasticTail,
    StochasticTrapezoidalFins,
    StochasticParachute,
)
import numpy as np
import matplotlib.pyplot as plt

# Import Pluto rocket definition and components from Pluto.py
from Pluto import Pluto, nose_cone, fins, boattail, drogue_trigger, main_trigger

# --------------------------------------------------------------------------------------
# Environment setup
# The environment is kept deterministic for the initial flight object,
# but the stochastic environment will handle wind variability during the Monte Carlo runs.
env = Environment(latitude=39.4751, longitude=-8.3764, elevation=78)
envtime = datetime.date.today()
env.set_date((envtime.year, envtime.month, envtime.day, 12))
env.set_atmospheric_model(
    type="custom_atmosphere",
        pressure=None,
        temperature=None,
        # break down 6m/s in a 150 degree angle for average wind in the area
        wind_u=[(0, 3.0), (10000, -3.0)],
        wind_v=[(0, -5.2), (10000, 5.2)],    
)

# Stochastic environment (wind variability)
stochastic_env = StochasticEnvironment(
    environment=env,
    wind_velocity_x_factor=(1, 0.2),  # 10% variability in wind x component
    wind_velocity_y_factor=(1, 0.2),  # 10% variability in wind y component
)

# --------------------------------------------------------------------------------------
# Define the nominal flight for the Monte Carlo simulation
nominal_flight = Flight(
    rocket=Pluto,
    environment=env,
    rail_length=12,
    inclination=84,
    heading=133,
    terminate_on_apogee=False,
    name="Pluto_Full_Flight",
)

# --------------------------------------------------------------------------------------
# Stochastic Rockets
stochastic_Pluto = StochasticRocket(
    rocket=Pluto,
    radius=0.095 / 2000,
    mass=(56.842, 1, "normal"),
    inertia_11=(71.5, 1.26, "normal"),
    inertia_22=0.01,
    inertia_33=0.01,
)

# Add stochastic surfaces (nose, fins, tail)
stochastic_nose_cone = StochasticNoseCone(
    nosecone=nose_cone,
    length=0.001,
)

stochastic_fins = StochasticTrapezoidalFins(
    trapezoidal_fins=fins,
    root_chord=0.0005,
    tip_chord=0.0005,
    span=0.0005,
)

stochastic_tail = StochasticTail(
    tail=boattail,
    top_radius=0.001,
    bottom_radius=0.001,
    length=0.001,
)

# Convert Kerberos motor to GenericMotor for compatibility
GenericKerberos = GenericMotor(
    thrust_source="Kerberos_TC.eng",
    burn_time=9.1,
    chamber_radius=0.185 / 2,
    chamber_height=0.840 + 0.404,
    chamber_position=1,
    propellant_initial_mass=16.06 + 5.35,
    nozzle_radius=0.025,
    dry_mass=0.01,  # to avoid numerical issues
    center_of_dry_mass_position=1.0824,
    dry_inertia=(0.001, 0.001, 0.001),  # Updated to very small non-zero values
    nozzle_position=0,
    reshape_thrust_curve=False,
    interpolation_method="linear",
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)

# Add components to stochastic rocket
stochastic_Pluto.add_motor(GenericKerberos, position=0.001)
stochastic_Pluto.add_nose(stochastic_nose_cone, position=(4.51, 0.001))
stochastic_Pluto.add_trapezoidal_fins(stochastic_fins, position=0.72)
stochastic_Pluto.add_tail(stochastic_tail)

# Add parachutes to the stochastic rocket
main_parachute = nominal_flight.rocket.add_parachute(
    name="main",
    cd_s=29.128,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise=(0, 0, 0),
)
drogue_parachute = nominal_flight.rocket.add_parachute(
    name="drogue",
    cd_s=1.05,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=2,
    noise=(0, 0, 0),
)

stochastic_main_parachute = StochasticParachute(
    parachute=main_parachute,
    cd_s=(29.128, 2.9128),  # 10% standard deviation
)
stochastic_drogue_parachute = StochasticParachute(
    parachute=drogue_parachute,
    cd_s=(1.05, 0.105),  # 10% standard deviation
)

stochastic_Pluto.add_parachute(stochastic_main_parachute)
stochastic_Pluto.add_parachute(stochastic_drogue_parachute)

# --------------------------------------------------------------------------------------
# Stochastic flights
stochastic_flight = StochasticFlight(
    flight=nominal_flight,
    inclination=(84, 0.5),
    heading=(133, 1),
)

# --------------------------------------------------------------------------------------
# Monte Carlo Simulations
numberOfSims = 90 # run in batches of 10 until we have enough data

test_dispersion = MonteCarlo(
    filename="pluto_full_flight",
    environment=stochastic_env,
    rocket=stochastic_Pluto,
    flight=stochastic_flight,
)
test_dispersion.simulate(number_of_simulations=numberOfSims, append=True)

# --------------------------------------------------------------------------------------
# Post-processing Monte Carlo
dispersion_results = test_dispersion.results
N = len(dispersion_results.get("apogee_time", []))
print(f"Number of simulations processed: {N}")

# --------------------------------------------------------------------------------------
# Dispersion Results
print("\nOut of Rail Time")
print(
    f"Out of Rail Time -         Mean Value: {np.mean(dispersion_results['out_of_rail_time']):0.3f} s")
print(
    f"Out of Rail Time - Standard Deviation: {np.std(dispersion_results['out_of_rail_time']):0.3f} s")
plt.figure()
plt.hist(dispersion_results["out_of_rail_time"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Out of Rail Time")
plt.xlabel("Time (s)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nOut of Rail Velocity")
print(
    f"Out of Rail Velocity -         Mean Value: {np.mean(dispersion_results['out_of_rail_velocity']):0.3f} m/s")
print(
    f"Out of Rail Velocity - Standard Deviation: {np.std(dispersion_results['out_of_rail_velocity']):0.3f} m/s")
plt.figure()
plt.hist(dispersion_results["out_of_rail_velocity"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Out of Rail Velocity")
plt.xlabel("Velocity (m/s)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nApogee Time")
print(
    f"Apogee Time -         Mean Value: {np.mean(dispersion_results['apogee_time']):0.3f} s")
print(
    f"Apogee Time - Standard Deviation: {np.std(dispersion_results['apogee_time']):0.3f} s")
plt.figure()
plt.hist(dispersion_results["apogee_time"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Apogee Time")
plt.xlabel("Time (s)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nApogee Altitude")

print(
    f"Apogee Altitude -         Mean Value: {np.mean(dispersion_results['apogee']):0.3f} m")
print(
    f"Apogee Altitude - Standard Deviation: {np.std(dispersion_results['apogee']):0.3f} m")
plt.figure()
plt.hist(dispersion_results["apogee"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Apogee Altitude")
plt.xlabel("Altitude (m)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nApogee X Position")
print(
    f"Apogee X Position -         Mean Value: {np.mean(dispersion_results['apogee_x']):0.3f} m")
print(
    f"Apogee X Position - Standard Deviation: {np.std(dispersion_results['apogee_x']):0.3f} m")
plt.figure()
plt.hist(dispersion_results["apogee_x"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Apogee X Position")
plt.xlabel("Apogee X Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nApogee Y Position")
print(
    f"Apogee Y Position -         Mean Value: {np.mean(dispersion_results['apogee_y']):0.3f} m")
print(
    f"Apogee Y Position - Standard Deviation: {np.std(dispersion_results['apogee_y']):0.3f} m")
plt.figure()
plt.hist(dispersion_results["apogee_y"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Apogee Y Position")
plt.xlabel("Apogee Y Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

# NOTE: The key for impact time, 't_final', might be more accurate if available. 'impact_time' is not in the list.
# Let's assume t_final is the impact time.
print("\nImpact Time")
print(
    f"Impact Time -         Mean Value: {np.mean(dispersion_results['t_final']):0.3f} s")
print(
    f"Impact Time - Standard Deviation: {np.std(dispersion_results['t_final']):0.3f} s")
plt.figure()
plt.hist(dispersion_results["t_final"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Impact Time")
plt.xlabel("Time (s)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nImpact X Position")
# CORRECTED KEY: 'impact_x' -> 'x_impact'
print(
    f"Impact X Position -         Mean Value: {np.mean(dispersion_results['x_impact']):0.3f} m")
print(
    f"Impact X Position - Standard Deviation: {np.std(dispersion_results['x_impact']):0.3f} m")
plt.figure()
plt.hist(dispersion_results["x_impact"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Impact X Position")
plt.xlabel("Impact X Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nImpact Y Position")
print(
    f"Impact Y Position -         Mean Value: {np.mean(dispersion_results['y_impact']):0.3f} m")
print(
    f"Impact Y Position - Standard Deviation: {np.std(dispersion_results['y_impact']):0.3f} m")
plt.figure()
plt.hist(dispersion_results["y_impact"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Impact Y Position")
plt.xlabel("Impact Y Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

print("\nImpact Velocity")
print(
    f"Impact Velocity -         Mean Value: {np.mean(dispersion_results['impact_velocity']):0.3f} m/s")
print(
    f"Impact Velocity - Standard Deviation: {np.std(dispersion_results['impact_velocity']):0.3f} m/s")
plt.figure()
plt.hist(dispersion_results["impact_velocity"], bins=int(N**0.5) if N > 0 else 1)
plt.title("Impact Velocity")

plt.xlabel("Velocity (m/s)")
plt.ylabel("Number of Occurences")
plt.show()

# --------------------------------------------------------------------------------------
# Error Ellipses
from matplotlib.patches import Ellipse

def eigsorted(cov):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    return vals[order], vecs[:, order]

# Create plot figure
plt.figure(num=None, figsize=(8, 6), dpi=150, facecolor="w", edgecolor="k")
ax = plt.subplot(111)

# Retrieve dispersion data por apogee and impact XY position
apogee_x = np.array(dispersion_results["apogee_x"])
apogee_y = np.array(dispersion_results["apogee_y"])
# CORRECTED KEYS for impact x and y
impact_x = np.array(dispersion_results["x_impact"])
impact_y = np.array(dispersion_results["y_impact"])

# Calculate error ellipses for impact
impactCov = np.cov(impact_x, impact_y)
impactVals, impactVecs = eigsorted(impactCov)
impactTheta = np.degrees(np.arctan2(*impactVecs[:, 0][::-1]))
impactW, impactH = 2 * np.sqrt(impactVals)

# Draw error ellipses for impact
impact_ellipses = []
for j in [1, 2, 3]:
    impactEll = Ellipse(
        xy=(np.mean(impact_x), np.mean(impact_y)),
        width=impactW * j,
        height=impactH * j,
        angle=impactTheta,
        color="black",
    )
    impactEll.set_facecolor((0, 0, 1, 0.2))
    impact_ellipses.append(impactEll)
    ax.add_artist(impactEll)

# Calculate error ellipses for apogee
apogeeCov = np.cov(apogee_x, apogee_y)
apogeeVals, apogeeVecs = eigsorted(apogeeCov)
apogeeTheta = np.degrees(np.arctan2(*apogeeVecs[:, 0][::-1]))
apogeeW, apogeeH = 2 * np.sqrt(apogeeVals)

# Draw error ellipses for apogee
for j in [1, 2, 3]:
    apogeeEll = Ellipse(
        xy=(np.mean(apogee_x), np.mean(apogee_y)),
        width=apogeeW * j,
        height=apogeeH * j,
        angle=apogeeTheta,
        color="black",
    )
    apogeeEll.set_facecolor((0, 1, 0, 0.2))
    ax.add_artist(apogeeEll)

# Draw launch point
plt.scatter(0, 0, s=30, marker="*", color="black", label="Launch Point")

# Draw apogee points
plt.scatter(
    apogee_x, apogee_y, s=5, marker="^", color="green", label="Simulated Apogee")

# Draw impact points
plt.scatter(
    impact_x, impact_y, s=5, marker="v", color="blue", label="Simulated Landing Point")

plt.legend()

# Add title and labels to plot
ax.set_title(
    "1$\sigma$, 2$\sigma$ and 3$\sigma$ Dispersion Ellipses: Apogee and Lading Points")
ax.set_ylabel("North (m)")
ax.set_xlabel("East (m)")

plt.axhline(0, color="black", linewidth=0.5)
plt.axvline(0, color="black", linewidth=0.5)

plt.show()