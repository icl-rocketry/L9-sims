import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# imports
from rocketpy.plots.compare import CompareFlights
from rocketpy import Environment, Flight, Rocket
from Kerberos import Kerberos
import datetime


# Rocket

length = 4.51  # (m), to convert from openrocket layout to rocketpy coordinate system

# main rocket used on ascent
Pluto = Rocket(
    radius=0.095,
    mass=56.842,  # mass is excluding fuel, ox and nitrous
    inertia=(71.5, 71.5, 0.25),
    power_off_drag="RocketPy/cd.csv",
    power_on_drag="RocketPy/cd.csv",
    center_of_mass_without_motor=length - 2.61,
    coordinate_system_orientation="tail_to_nose",
)

Pluto_Drogue_Only = Rocket(
    radius=0.095,
    mass=56.842,  # mass is excluding fuel, ox and nitrous
    inertia=(71.5, 71.5, 0.25),
    power_off_drag="RocketPy/cd.csv",
    power_on_drag="RocketPy/cd.csv",
    center_of_mass_without_motor=length - 2.61,
    coordinate_system_orientation="tail_to_nose",
)

# add motor to ascent vehicle
Pluto.add_motor(Kerberos, position=0)
Pluto_Drogue_Only.add_motor(Kerberos, position=0)

# nose cone is on both rockets, same with fins and boattail
nose_cone = Pluto.add_nose(length=0.7, kind="lvhaack", position=length)
Pluto_Drogue_Only.add_nose(length=0.7, kind="lvhaack", position=length)

fins = Pluto.add_trapezoidal_fins(
    n=3,
    root_chord=0.41,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.22,
    position=0.72,
    cant_angle=0,
)
Pluto_Drogue_Only.add_trapezoidal_fins(
    n=3,
    root_chord=0.41,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.22,
    position=0.72,
    cant_angle=0,
)

boattail = Pluto.add_tail(top_radius=0.0925, bottom_radius=0.06, length=0.293, position=0.293)
Pluto_Drogue_Only.add_tail(top_radius=0.0925, bottom_radius=0.06, length=0.293, position=0.293)

Pluto.set_rail_buttons(
    upper_button_position=length - 2.48,  # above fuel tank
    lower_button_position=length - 3.78,  # top of fin can
    angular_position=60,
)
Pluto_Drogue_Only.set_rail_buttons(
    upper_button_position=length - 2.48,  # above fuel tank
    lower_button_position=length - 3.78,  # top of fin can
    angular_position=60,
)

# chutes
def drogue_trigger(p, h, y):  # deploy at apogee (lag is taken into account later)
    return True if y[5] < 0 else False


def main_trigger(p, h, y):  # assuming nominal deployment at max. altitude allowed (-> max drift)
    return True if y[5] < 0 and h < 450 else False


Pluto.add_parachute(
    name="main",
    cd_s=29.128,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise=(0, 0, 0),
)
# add reefing to main parachute with a drogue
Pluto.add_parachute(
    name="drogue",
    cd_s=1.05,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=2,
    noise=(0, 0, 0),
)

Pluto_Drogue_Only.add_parachute(
    name="only_drogue",
    cd_s=0.98,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=2,
    noise=(0, 0, 0),
)

if __name__ == "__main__":

    # Environment
    env = Environment(latitude=39.4751, longitude=-8.3764, elevation=0)
    env.set_atmospheric_model(
        type="custom_atmosphere",
        pressure=None,
        temperature=None,
        # break down 8.7m/s in a 133 degree angle
        wind_u=[(0, 6.36), (10000, 6.36)],  # component in x direction
        wind_v=[(0, -5.93), (10000, -5.93)],  # component in y direction
    )

    # Flights
    Flight_Normal = Flight(
        rocket=Pluto,
        environment=env,
        rail_length=12,
        inclination=84,
        heading=133,
        terminate_on_apogee=False,
        name="Flight",
    )

    Flight_Drogue_Only = Flight(
        rocket=Pluto_Drogue_Only,
        environment=env,
        rail_length=12,
        inclination=84,
        heading=133,
        terminate_on_apogee=False,
        name="Flight_Drogue_Only",
    )

    #Flight_Normal.all_info()

    #Uncomment to see flight with only drogue
    Flight_Drogue_Only.all_info()
    Pluto.draw()