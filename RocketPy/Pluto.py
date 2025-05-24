import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# imports
from rocketpy.plots.compare import CompareFlights
from rocketpy import Environment, Flight, Rocket
from Goofy import Goofy
import datetime


# Rocket
# Pluto includes payload and is used on the ascent
# PlutoDescent has no payload and is used on the descent
Pluto = Rocket(
    radius=0.0925,
    mass=53.866,  # mass is excluding tanks and engine
    inertia=(66.5, 66.5, 0.242),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=4.34 - 2.35,
    coordinate_system_orientation="tail_to_nose",
)

PlutoDescent = Rocket(
    radius=0.0925,
    mass=53.866,  # mass is excluding tanks and engine
    inertia=(66.5, 66.5, 0.242),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=4.34 - 2.35,
    coordinate_system_orientation="tail_to_nose",
)

Pluto.add_motor(Goofy, position=0)

nose_cone = Pluto.add_nose(length=0.7, kind="lvhaack", position=4.31)
nose_cone2 = PlutoDescent.add_nose(length=0.7, kind="lvhaack", position=4.31)


fins = Pluto.add_trapezoidal_fins(
    n=3,
    root_chord=0.41,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.22,
    position=0.7,
    cant_angle=0,
    radius=0.1,
)

fins2 = PlutoDescent.add_trapezoidal_fins(
    n=3,
    root_chord=0.41,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.22,
    position=0.7,
    cant_angle=0,
    radius=0.1,
)



boattail = Pluto.add_tail(top_radius=0.0925, bottom_radius=0.06, length=0.293, position=0.293)
boattail2 = PlutoDescent.add_tail(top_radius=0.1, bottom_radius=0.0821, length=0.41, position=0.42)

# rail buttons?
Pluto.set_rail_buttons(
    upper_button_position = 2.82,
    lower_button_position = 0.36,
    angular_position = 60,
    )

def drogue_trigger(p, h, y):
    return True if y[5] < 0 else False

def main_trigger(p, h, y):
    return True if y[5] < 0 and h < 450 else False

main = PlutoDescent.add_parachute(
    name="main",
    cd_s=14.612,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise = (0, 0, 0),
)

# add reefing to main parachute with a drogue
drogue = PlutoDescent.add_parachute(
    name="drogue",
    cd_s=0.98033,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=2,
    noise = (0, 0, 0),
)

# we only want to run this if we are running this file specifically as a nominal sim

if __name__ == "__main__":

    # Environment
    env = Environment(latitude=39.4751, longitude=-8.3764, elevation=0)
    envtime = datetime.date.today() + datetime.timedelta(days = 1)  # tomorrow
    env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
    env.set_atmospheric_model(type="Forecast", file="GFS")

    # draw rocket
    Pluto.draw()

    # Flights
    Ascent = Flight(rocket=Pluto, environment=env, rail_length=12, inclination=84, heading=133, terminate_on_apogee=True, name="Ascent")
    Descent = Flight(rocket=PlutoDescent, environment=env, rail_length=0.01, inclination=0, heading=133, initial_solution=Ascent, name="Descent")

    # Results
    comparison = CompareFlights([Ascent, Descent])
    comparison.trajectories_3d(legend=True)

    # print("----- ENV INFO -----")
    # env.all_info()
    # print("----- THANOS INFO -----")
    # Thanos_R.all_info()
    # print("----- PLUTO INFO -----")
    # Pluto.all_info()
    # print("----- ASCENT INFO -----")
    # Ascent.all_info()

    # simple info without all the plots
    Ascent.info()
    Descent.info()