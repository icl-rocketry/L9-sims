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
env.set_atmospheric_model(type="custom_atmosphere", wind_u=[[0, 3.4],[5000, 10.2]], wind_v=[[0, 1.3],[5000, 3.9]])

# Creating the 'stochastic environment' counterpart
stochastic_env = StochasticEnvironment(
    environment=env,
    wind_velocity_x_factor=(1, 0.1),
    wind_velocity_y_factor=(1, 0.1))
# Reporting the attributes of the `StochasticEnvironment` object:
stochastic_env.visualize_attributes()

# Two rocket objects are created for the two different configurations during ascent & descent phases
# NimbusAscent object includes the payload mass
# NimbusDescent object has no payload
# Note: The payload (and its deployment) is not simulated, there will be a separate guided recovery sim

# Creating the (deterministic) rocket objects and flights ----------------------------------------------------
NimbusAscent = Rocket(
    radius=0.1,
    mass=54.647,  # mass is excluding tanks and engine
    inertia=(69.032, 69.032, 0.417),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor= 4.31 - 2.48,
    coordinate_system_orientation="tail_to_nose",
)

# NimbusDescent = Rocket(
#     radius=0.1,
#     mass=54.647,  # mass is excluding tanks and engine
#     inertia=(59.121, 59.121, 0.298),
#     power_off_drag="RocketPy/dragCurve.csv",
#     power_on_drag="RocketPy/dragCurve.csv",
#     center_of_mass_without_motor=4.31 - 2.48,
#     coordinate_system_orientation="tail_to_nose",
# )

# Adding motor only for ascent rocket
NimbusAscent.add_motor(Thanos_R, position=0)

# Creating nose cone objects for ascent and descent phases
nose_coneA = NimbusAscent.add_nose(length=0.35, kind="von karman", position=4.28)
#nose_coneD = NimbusDescent.add_nose(length=0.35, kind="von karman", position=4.28)

# Creating fins for ascent and descent rockets
fins = NimbusAscent.add_trapezoidal_fins(
    n=3,
    root_chord=0.36,
    tip_chord=0.16,
    sweep_length=0.24,
    span=0.25,
    position=0.36,
    cant_angle=0,
    radius=0.082,
)

# fins2 = NimbusDescent.add_trapezoidal_fins(
#     n=3,
#     root_chord=0.36,
#     tip_chord=0.16,
#     sweep_length=0.24,
#     span=0.25,
#     position=0.36,
#     cant_angle=0,
#     radius=0.082,
# )

# Creating boattails for ascent and descent rockets
boattail = NimbusAscent.add_tail(top_radius=0.1, bottom_radius=0.0821, length=0.41, position=0.42)
#boattail2 = NimbusDescent.add_tail(top_radius=0.1, bottom_radius=0.0821, length=0.41, position=0.42)

# Setting rail buttons only for ascent rocket
NimbusAscent.set_rail_buttons(
    upper_button_position = 2.82,
    lower_button_position = 0.36,
    angular_position = 60,
    )

def drogue_trigger(p, h, y):
    return True if y[5] < 0 else False

def main_trigger(p, h, y):
    return True if y[5] < 0 and h < 5000 else False

main = NimbusAscent.add_parachute(
    name="main",
    cd_s=10.4,
    trigger=main_trigger,
    sampling_rate=100,
    lag=7,
    noise = (0, 0, 0), # Set to 0, noise simulates pressure sensor which is not implemented in this sim
)

# add reefing to main parachute with a drogue
drogue = NimbusAscent.add_parachute(
    name="drogue",
    cd_s=0.3936,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=0,
    noise = (0, 0, 0), # Set to 0, noise simulates pressure sensor which is not implemented in this sim
)


# # draw rocket
# NimbusAscent.draw()

# Flights
Ascent = Flight(rocket=NimbusAscent, environment=env, rail_length=12, inclination=90, heading=0, name="Ascent")
#Descent = Flight(rocket=NimbusDescent, environment=env, rail_length=12, inclination=0, heading=0, initial_solution=Ascent, name="Descent")

# Results
comparison = CompareFlights([Ascent, Ascent])
comparison.trajectories_3d(legend=True)

# print("----- ASCENT INFO -----")
# Ascent.info()
# print("----- DESCENT INFO -----")
# Descent.info()

# MONTE CARLO SECTION OF SCRIPT ---------------------------------------------------------
# Note: The uncertainties assigned to the components in this script are arbitrary - will finalise later

# Creating the corresponding 'stochastic rocket' objects -------------------
stochastic_Ascent = StochasticRocket(
    rocket=NimbusAscent,
    mass=(54.647, 1, "normal"),
)
# Reporting the attributes of the `StochasticRocket` object:
# stochastic_Ascent.visualize_attributes()

# stochastic_Descent = StochasticRocket(
#     rocket=NimbusDescent,
#     mass=(54.647, 1, "normal"),
# )
# Reporting the attributes of the `StochasticRocket` object:
# stochastic_Ascent.visualize_attributes()

# Creating the 'stochastic aerosurface' objects for ascent
stochastic_nose_coneA = StochasticNoseCone(
    nosecone=nose_coneA,
)

stochastic_fin_setA = StochasticTrapezoidalFins(
    trapezoidal_fins=fins,
)

stochastic_tailA = StochasticTail(
    tail=boattail,
)

# # Creating the 'stochastic aerosurface' objects for descent
# stochastic_nose_coneD = StochasticNoseCone(
#     nosecone=nose_coneD,
# )

# stochastic_fin_setD = StochasticTrapezoidalFins(
#     trapezoidal_fins=fins2,
# )

# stochastic_tailD = StochasticTail(
#     tail=boattail2,
# )

# Converting Liquid Motor object to a GenericMotor to be compatible with 'Stochastic' objects
# Note: From the docs, apparently this object is less accurate than Liquid/SolidMotor (verify values)
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

# Adding components to the 'stochastic rocket' objects
# Note: Bug in code (not sure if it's me or Rocketpy) doesn't allow multiple sets of fins to be added to stochastic rocket
#       The omission of canards for the ascent phase should lead to the landing ellipses being smaller than reality,
#       this is due to the destabilising effects of the canards in pitch & yaw not being included.
#       The omission of the canards for the descent phase should have negligible impact on the results,
#       this is due to the canards only developing small aerodynamic forces at low speeds (using parachutes)

# Ascent
stochastic_Ascent.add_motor(GenericThanos_R, position=0.001)
stochastic_Ascent.add_nose(stochastic_nose_coneA, position=(4.28, 0.001))
stochastic_Ascent.add_trapezoidal_fins(stochastic_fin_setA, position=0.32)
# stochastic_Ascent.add_trapezoidal_fins(stochastic_canardsA, position=3.04)
stochastic_Ascent.add_tail(stochastic_tailA)

# # Descent
# stochastic_Descent.add_nose(stochastic_nose_coneA, position=(4.28, 0.001))
# stochastic_Descent.add_trapezoidal_fins(stochastic_fin_setD, position=0.32)
# # stochastic_Descent.add_trapezoidal_fins(stochastic_canardsD, position=3.04)
# stochastic_Descent.add_tail(stochastic_tailD)
stochastic_Ascent.add_parachute(main)
stochastic_Ascent.add_parachute(drogue)

# Monte Carlo Flights -----------------------------------------------------------

# Ascent flight
stochastic_flightAscent = StochasticFlight(
    flight=Ascent,
    inclination=(90, 1),  # mean = 86, std = 1
    heading=(45, 15),  # mean = 0, std = 2
)

# # Extract the final state at the last timestep from the Ascent flight object
# t_final = Ascent.apogee_time
# final_state_vectorA = Ascent.get_solution_at_time(t_final)

# # Print the final ascent state vector for verification
# print("Final State Vector (Initial Solution):", final_state_vectorA)

# # Defining another descent flight since 'StochasticFlight' object has to be initialised with a tuple/list and not a 'Flight' object as before
# Descent2 = Flight(rocket=NimbusDescent, environment=env, rail_length=12, inclination=0, heading=0, initial_solution=final_state_vectorA, name="Descent2")

# # Descent flight
# stochastic_flightDescent = StochasticFlight(
#     flight=Descent2,                       # Pass the existing flight object
#     inclination=0,                         # Define inclination or randomize it
#     heading=0,                             # Define heading or randomize it
#     initial_solution=final_state_vectorA,  # Use the extracted final ascent state vector
# )

# Initialising Monte Carlo objects for the sims
numberOfSims = 100 # Setting the number of Monte Carlo sims to run

# Data for ascent phase
test_dispersionAscent = MonteCarlo(
    filename="ascent",
    environment=stochastic_env,
    rocket=stochastic_Ascent,
    flight=stochastic_flightAscent,
)

# Running the Monte Carlo simulations for the ascent phase
# Note: The result of this call should be multiple ascent flights with ballistic descents and no payload deployment
test_dispersionAscent.simulate(number_of_simulations=numberOfSims, append=False)


# # Data for descent phase
# test_dispersionDescent = MonteCarlo(
#     filename="descent",
#     environment=stochastic_env,
#     rocket=stochastic_Descent,
#     flight=stochastic_flightDescent,
# )

# # Running the Monte Carlo simulations for the descent phase
# # Note: The result of this call should be multiple descent flights, all initialised using the 'nominal' ascent flight (and payload has been deployed)
# test_dispersionDescent.simulate(number_of_simulations=numberOfSims, append=False)

# Plotting the simulated apogee and landing zones
test_dispersionAscent.plots.ellipses()
# test_dispersionDescent.plots.ellipses()
test_dispersionAscent.prints.all()