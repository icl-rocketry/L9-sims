# This script assigns uncertainties to rocket and environmental parameters and runs Monte Carlo sims accordingly
# Note: Script assumes all necessary files are in the current working directory

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# Import necessary modules
from rocketpy import Environment, Rocket, Flight, CompareFlights, MonteCarlo, GenericMotor
from rocketpy.stochastic import (
    StochasticEnvironment,
    StochasticRocket,
    StochasticFlight,
    StochasticNoseCone,
    StochasticTail,
    StochasticTrapezoidalFins,
)
from Thanos import Thanos_R
import datetime

# Initialising the (deterministic) simulation environment
env = Environment(latitude=55, longitude=-2.64, elevation=325)
envtime = datetime.date.today()
env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
# typical met values in july. Scale factor of 
env.set_atmospheric_model(type="custom_atmosphere", wind_u=[[0, 3.4],[1000, 8.2],[5000, 10.9]], wind_v=[[0, 1.3],[1000, 3.4],[5000, 4.3]])

# Creating the 'stochastic environment' counterpart
stochastic_env = StochasticEnvironment(
    environment=env,
    # add the effects of turbulence with the typical intensity factor. This adds random noise to the monte carlo sims
    wind_velocity_x_factor=(1, 0.15),
    wind_velocity_y_factor=(1, 0.15))
# Reporting the attributes of the `StochasticEnvironment` object:
stochastic_env.visualize_attributes()

# Two rocket objects are created for the two different configurations during ascent & descent phases

# Creating the (deterministic) rocket objects and flights ----------------------------------------------------
bipropAscent = Rocket(
    radius=0.1,
    mass=54.647,  # mass is excluding tanks and engine
    inertia=(69.032, 69.032, 0.417),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor= 4.31 - 2.48,
    coordinate_system_orientation="tail_to_nose",
)

# Adding motor only for ascent rocket
bipropAscent.add_motor(Thanos_R, position=0)

# Creating rocket components
nose_coneA = bipropAscent.add_nose(length=0.35, kind="von karman", position=4.28)

fins = bipropAscent.add_trapezoidal_fins(
    n=3,
    root_chord=0.36,
    tip_chord=0.16,
    sweep_length=0.24,
    span=0.25,
    position=0.36,
    cant_angle=0,
    radius=0.082,
)

boattail = bipropAscent.add_tail(top_radius=0.1, bottom_radius=0.0821, length=0.41, position=0.42)

bipropAscent.set_rail_buttons(
    upper_button_position = 2.82,
    lower_button_position = 0.36,
    angular_position = 60,
    )

# parachute triggers - change the main trigger to 500 for nominal flight, 5000 (or anything above apogee) for main at apogee case
def drogue_trigger(p, h, y):
    return True if y[5] < 0 else False

def main_trigger(p, h, y):
    return True if y[5] < 0 and h < 500 else False

# add the chutes to the rocket
main = bipropAscent.add_parachute(
    name="main",
    cd_s=9.8,
    trigger=main_trigger,
    sampling_rate=100,
    lag=3,
    noise = (0, 0, 0),
)

drogue = bipropAscent.add_parachute(
    name="drogue",
    cd_s=0.3936,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=1,
    noise = (0, 0, 0), # Set to 0, noise simulates pressure sensor which is not implemented in this sim
)



# Flights
Ascent = Flight(rocket=bipropAscent, environment=env, rail_length=9, inclination=85, heading=60, name="Ascent")

# Results
comparison = CompareFlights([Ascent, Ascent])
comparison.trajectories_3d(legend=True)




# MONTE CARLO SECTION OF SCRIPT ---------------------------------------------------------
# Note: The uncertainties assigned to the components in this script are arbitrary - will finalise later

# Creating the corresponding 'stochastic rocket' objects
stochasticBiprop = StochasticRocket(
    rocket=bipropAscent,
    mass=(54.647, 1, "normal"),
)

# Creating the stochastic objects for ascent
stochastic_nose_coneA = StochasticNoseCone(
    nosecone=nose_coneA,
)

stochastic_fin_setA = StochasticTrapezoidalFins(
    trapezoidal_fins=fins,
)

stochastic_tailA = StochasticTail(
    tail=boattail,
)

# Converting Liquid Motor object to a GenericMotor to be compatible with 'Stochastic' objects
GenericThanos_R = GenericMotor(
    thrust_source="OpenRocket/ThanosR40.eng",
    burn_time=6.53,
    chamber_radius=0.085,
    chamber_height=0.635 + 0.369,
    chamber_position=1,
    propellant_initial_mass=7+4,
    nozzle_radius=0.025,
    dry_mass=3.1,
    center_of_dry_mass_position=1.0824,
    dry_inertia=(0.6050, 0.6094, 0.1004),
    nozzle_position=0,
    reshape_thrust_curve=False,
    interpolation_method="linear",
    coordinate_system_orientation="nozzle_to_combustion_chamber",
    )


# Ascent
stochasticBiprop.add_motor(GenericThanos_R, position=0.001)
stochasticBiprop.add_nose(stochastic_nose_coneA, position=(4.28, 0.001))
stochasticBiprop.add_trapezoidal_fins(stochastic_fin_setA, position=0.32)
stochasticBiprop.add_tail(stochastic_tailA)
stochasticBiprop.add_parachute(main)
stochasticBiprop.add_parachute(drogue)

# Monte Carlo Flights -----------------------------------------------------------

# Ascent flight
stochastic_flightAscent = StochasticFlight(
    flight=Ascent,
    inclination=(85, 0.25),  # mean = 87, std. dev = 0.25 - taken from accuracies in launch rail alignment
    heading=(60, 1),  # mean = 60, std = 1 - taken from accuracies in launch rail alignment. Launch with the wind for safety
)

# Initialising Monte Carlo objects for the sims
numberOfSims = 100 # Setting the number of Monte Carlo sims to run

# Data for ascent phase
test_dispersionAscent = MonteCarlo(
    filename="ascent",
    environment=stochastic_env,
    rocket=stochasticBiprop,
    flight=stochastic_flightAscent,
)

# Running the Monte Carlo simulations for the ascent phase
test_dispersionAscent.simulate(number_of_simulations=numberOfSims, append=False)

# Plotting the simulated apogee and landing zones
test_dispersionAscent.plots.ellipses()
test_dispersionAscent.prints.all()