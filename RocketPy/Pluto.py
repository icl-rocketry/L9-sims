import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
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

length = 4.34  # (m), to convert from openrocket layout to rocketpy coordinate system

# main rocket used on ascent
Pluto = Rocket(
    radius=0.0925,
    mass=53.866,  # mass is excluding tanks and engine
    inertia=(66.5, 66.5, 0.242),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=length - 2.35,
    coordinate_system_orientation="tail_to_nose",
)

# rocket used on descent, with no payload mass - other than that its the same
PlutoDescent = Rocket(
    radius=0.0925,
    mass=53.866,  # mass is excluding tanks and engine
    inertia=(66.5, 66.5, 0.242),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=length - 2.35,
    coordinate_system_orientation="tail_to_nose",
)

# payload deployed
Payload = Rocket(
    radius=0.05, # its not a cylinder but is a good enough approximation as we give cd values separately
    mass=3.0,
    inertia=(1.0, 1.0, 0.01),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=0.1,
    coordinate_system_orientation="tail_to_nose",
)

# add motor to ascent vehicle
Pluto.add_motor(Goofy, position=0)

# nose cone is on both rockets, same with fins and boattail
nose_cone = Pluto.add_nose(length=0.7, kind="lvhaack", position=length)
nose_cone2 = PlutoDescent.add_nose(length=0.7, kind="lvhaack", position=length)

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

# fly-away launch lugs will be analysed in more detail in the technical report
Pluto.set_rail_buttons(
    upper_button_position=length - 2.65,
    lower_button_position=length - 3.45,
    angular_position=0,
)

# chutes
def drogue_trigger(p, h, y):  # deploy at apogee (lag is taken into account later)
    return True if y[5] < 0 else False
def main_trigger(p, h, y):  # assuming nominal deployment at max. altitude allowed (-> max drift)
    return True if y[5] < 0 and h < 450 else False
def payload_trigger(p, h, y):  # deploy at 2km altitude - can go higher if wind is not too strong
    return True if h < 2000 else False

main = PlutoDescent.add_parachute(
    name="main",
    cd_s=14.612,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise=(0, 0, 0),
)
# add reefing to main parachute with a drogue
drogue = PlutoDescent.add_parachute(
    name="drogue",
    cd_s=0.98033,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=2,  # expected based on previous flight data
    noise=(0, 0, 0),
)
# payload chute is parafoil in vertical descent. Control sims will be in the technical report
Payload.add_parachute(
    name="payload",
    cd_s=0.5,  # parafoil
    trigger=payload_trigger,
    sampling_rate=100,
    lag=0,
    noise=(0, 0, 0),
)




if __name__ == "__main__":

    # Environment
    env = Environment(latitude=39.4751, longitude=-8.3764, elevation=0)
    envtime = datetime.date.today()  # current date
    # a more through analysis with varying wind speeds vs drift will be done in the tehcnical report
    env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
    env.set_atmospheric_model(type="Forecast", file="GFS")
    Pluto.draw()

    # Flights
    Ascent = Flight(
        rocket=Pluto,
        environment=env,
        rail_length=12,
        inclination=84,
        heading=133,
        terminate_on_apogee=True,
        name="Ascent",
    )
    Descent = Flight(
        rocket=PlutoDescent,
        environment=env,
        rail_length=0.01, # this doesnt make a difference as it starts off the rail
        inclination=0,
        heading=133,
        initial_solution=Ascent,
        name="Descent",
    )
    PayloadDescent = Flight(
        rocket=Payload,
        environment=env,
        rail_length=0.01, # this doesnt make a difference as it starts off the rail
        inclination=0,
        heading=133,
        initial_solution=Ascent,
        name="Payload",
    )

    # compare all 3 trajectories
    comparison = CompareFlights([Ascent, Descent, PayloadDescent])
    comparison.trajectories_3d(legend=True)

    # all the graphs
    print("----- ENV INFO -----")
    env.all_info()
    print("----- ENGINE INFO -----")
    Goofy.all_info()
    print("----- PLUTO INFO -----")
    Pluto.all_info()
    print("----- ASCENT INFO -----")
    Ascent.all_info()
    print("----- DESCENT INFO -----")
    Descent.all_info() 
    print("----- PAYLOAD INFO -----")
    PayloadDescent.all_info()

    # simple info without all the plots
    Ascent.info()
    Descent.info()
    PayloadDescent.info()
