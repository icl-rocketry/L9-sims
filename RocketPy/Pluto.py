import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# imports
from rocketpy import Environment, Rocket, Flight, CompareFlights
from Thanos import Thanos_R
import datetime


# Rocket
# Nimbus includes payload and is used on the ascent
# NimbusEmpty has no payload and is used on the descent
# the individual payload + parafoil is not simulated, that's for our guided recovery sim
Nimbus = Rocket(
    radius=0.1,
    mass=48.406,  # mass is excluding tanks and engine
    inertia=(66.8, 66.8, 0.385),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor= 4.31 - 2.48,
    coordinate_system_orientation="tail_to_nose",
)

NimbusDescent = Rocket(
    radius=0.925,
    mass=48.406,  # mass is excluding tanks and engine
    inertia=(55.821, 55.821, 0.265),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=4.31 - 2.48,
    coordinate_system_orientation="tail_to_nose",
)

Nimbus.add_motor(Thanos_R, position=0)

nose_cone = Nimbus.add_nose(length=0.7, kind="lvhaack", position=4.31)
nose_cone2 = NimbusDescent.add_nose(length=0.7, kind="lvhaack", position=4.31)


fins = Nimbus.add_trapezoidal_fins(
    n=3,
    root_chord=0.4411,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.21,
    position=0.46,
    cant_angle=0,
    radius=0.1,
)

fins2 = NimbusDescent.add_trapezoidal_fins(
    n=3,
    root_chord=0.4411,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.21,
    position=0.46,
    cant_angle=0,
    radius=0.1,
)



boattail = Nimbus.add_tail(top_radius=0.1, bottom_radius=0.0821, length=0.41, position=0.42)
boattail2 = NimbusDescent.add_tail(top_radius=0.1, bottom_radius=0.0821, length=0.41, position=0.42)

# rail buttons?
Nimbus.set_rail_buttons(
    upper_button_position = 2.82,
    lower_button_position = 0.36,
    angular_position = 60,
    )

def drogue_trigger(p, h, y):
    return True if y[5] < 0 else False

def main_trigger(p, h, y):
    return True if y[5] < 0 and h < 500 else False

main = NimbusDescent.add_parachute(
    name="main",
    cd_s=15.5509,
    trigger=main_trigger,
    sampling_rate=100,
    lag=7,
    noise = (0, 0, 0), # Set to 0, noise simulates pressure sensor which is not implemented in this sim
)

# add reefing to main parachute with a drogue
drogue = NimbusDescent.add_parachute(
    name="drogue",
    cd_s=0.3936,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=0,
    noise = (0, 0, 0), # Set to 0, noise simulates pressure sensor which is not implemented in this sim
)

# we only want to run this if we are running this file specifically as a nominal sim

if __name__ == "__main__":

    # Environment
    env = Environment(latitude=39.4751, longitude=-8.3764, elevation=0)
    envtime = datetime.date.today() + datetime.timedelta(days = 1)
    env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
    env.set_atmospheric_model(type="Forecast", file="GFS")

    # draw rocket
    Nimbus.draw()

    # Flights
    Ascent = Flight(rocket=Nimbus, environment=env, rail_length=12, inclination=86, heading=130, terminate_on_apogee=True, name="Ascent")
    Descent = Flight(rocket=NimbusDescent, environment=env, rail_length=12, inclination=0, heading=130, initial_solution=Ascent, name="Descent")

    # Results
    comparison = CompareFlights([Ascent, Descent])
    comparison.trajectories_3d(legend=True)

    print("----- ENV INFO -----")
    env.all_info()
    print("----- THANOS INFO -----")
    Thanos_R.all_info()
    print("----- Nimbus INFO -----")
    Nimbus.all_info()
    print("----- ASCENT INFO -----")
    Ascent.all_info()
    print("----- DESCENT INFO -----")
    Descent.info()