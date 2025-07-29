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
# Pluto includes payload and is used on the ascent
# PlutoDescentPreDeployment has no payload and is used on the descent

length = 4.51  # (m), to convert from openrocket layout to rocketpy coordinate system

# main rocket used on ascent
Pluto = Rocket(
    radius=0.0925,
    mass=64.345,  # mass is excluding fuel, ox and nitrous
    inertia=(80.5, 80.5, 0.288),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=length - 2.5,
    coordinate_system_orientation="tail_to_nose",
)

# rocket used on descent, with no payload mass - other than that its the same
# while the payload is still in the nose cone
PlutoDescentPreDeployment = Rocket(
    radius=0.0925,
    mass=56.471,  # mass is excluding fuel, ox and nitrous
    inertia=(75.1, 75.1, 0.266),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=length - 2.35,
    coordinate_system_orientation="tail_to_nose",
)

# descent rocket without payload
PlutoDescentPostDeployment = Rocket(
    radius=0.01,  # its not a cylinder but is a good enough approximation as we give I and m separately
    mass=56.471 - 3.229,  # minus payload mass
    inertia=(0.0216, 0.0215, 0.00437),
    power_off_drag="RocketPy/dragCurve.csv",  # we dont have the drag of the payload yet but its always under chute so doesnt matter
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=0.01,
    coordinate_system_orientation="tail_to_nose",
)

# payload deployed
Payload = Rocket(
    radius=0.01,  # its not a cylinder but is a good enough approximation as we give I and m separately
    mass=3.229,
    inertia=(0.0216, 0.0215, 0.00437),
    power_off_drag="RocketPy/dragCurve.csv",  # we dont have the drag of the payload yet but its always under chute so doesnt matter
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=0.01,
    coordinate_system_orientation="tail_to_nose",
)

# add motor to ascent vehicle
Pluto.add_motor(Kerberos, position=0)

# nose cone is on both rockets, same with fins and boattail
nose_cone = Pluto.add_nose(length=0.7, kind="lvhaack", position=length)
nose_cone2 = PlutoDescentPreDeployment.add_nose(length=0.7, kind="lvhaack", position=length)

fins = Pluto.add_trapezoidal_fins(
    n=3,
    root_chord=0.41,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.23,
    position=0.7,
    cant_angle=0,
    radius=0.1,
    airfoil=("RocketPy/aerofoil.csv", "degrees"),
)
fins2 = PlutoDescentPreDeployment.add_trapezoidal_fins(
    n=3,
    root_chord=0.41,
    tip_chord=0.16,
    sweep_length=0.30,
    span=0.23,
    position=0.7,
    cant_angle=0,
    radius=0.1,
    airfoil=("RocketPy/aerofoil.csv", "degrees"),
)

boattail = Pluto.add_tail(top_radius=0.0925, bottom_radius=0.06, length=0.293, position=0.293)
boattail2 = PlutoDescentPreDeployment.add_tail(top_radius=0.1, bottom_radius=0.0821, length=0.41, position=0.42)

# fly-away launch lugs will be analysed in more detail in the technical report
Pluto.set_rail_buttons(
    upper_button_position=length - 1.2,  # above separation point
    lower_button_position=length - 3.6,  # top of fin can
    angular_position=60,
)


# chutes
def drogue_trigger(p, h, y):  # deploy at apogee (lag is taken into account later)
    return True if y[5] < 0 else False


def main_trigger(p, h, y):  # assuming nominal deployment at max. altitude allowed (-> max drift)
    return True if y[5] < 0 and h < 450 else False


def payload_trigger(p, h, y):  # deploy at 2km altitude - can go higher if wind is not too strong
    return True if h < 2000 else False


PlutoDescentPostDeployment.add_parachute(
    name="main",
    cd_s=14.612,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise=(0, 0, 0),
)
# add reefing to main parachute with a drogue
PlutoDescentPreDeployment.add_parachute(
    name="drogue_pre_deploy",
    cd_s=0.98033,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=2,  # expected based on previous flight data
    noise=(0, 0, 0),
)
# add reefing to main parachute with a drogue
PlutoDescentPostDeployment.add_parachute(
    name="drogue_post_deploy",
    cd_s=0.98033,
    trigger=payload_trigger,  # if we use the drogue trigger again there is an error with simultaneous deployment
    sampling_rate=100,
    lag=0,  # chute remains open when payload deploys
    noise=(0, 0, 0),
)
# payload chute is parafoil in vertical descent. Control sims will be in the technical report
Payload.add_parachute(
    name="parafoil",
    cd_s=0.4 * 0.562,  # parafoil
    trigger=payload_trigger,
    sampling_rate=100,
    lag=0,
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
    Ascent = Flight(
        rocket=Pluto,
        environment=env,
        rail_length=12,
        inclination=84,
        heading=133,
        terminate_on_apogee=True,
        name="Ascent",
    )
    Ascent.all_info()  
    '''
    Descent1 = Flight(
        rocket=PlutoDescentPreDeployment,
        environment=env,
        rail_length=0.01,  # this doesnt make a difference as it starts off the rail
        inclination=0,
        heading=133,
        initial_solution=Ascent,
        name="Descent Pre-Deployment",
        max_time=164,  # limit the descent time to 100 seconds so that payload deploys at 2km
        # yes this needs to be updated each time the sim is run as it cant be decided based on altitude
    )
    Descent2 = Flight(
        rocket=PlutoDescentPostDeployment,
        environment=env,
        rail_length=0.01,  # this doesnt make a difference as it starts off the rail
        inclination=0,
        heading=133,
        initial_solution=Descent1,
        name="Descent Post-Deployment",
    )
    PayloadDescent = Flight(
        rocket=Payload,
        environment=env,
        rail_length=0.01,  # this doesnt make a difference as it starts off the rail
        inclination=0,
        heading=133,
        initial_solution=Ascent,
        name="Payload",
    )

    # compare all 3 trajectories
    comparison = CompareFlights([Ascent, Descent1, Descent2, PayloadDescent])
    comparison.trajectories_3d(legend=True)

    # all the graphs (uncomment to see)
    print("----- ENV INFO -----")
    env.all_info()
    print("----- ENGINE INFO -----")
    Kerberos.all_info()
    print("----- PLUTO INFO -----")
    Pluto.all_info()
    print("----- ASCENT INFO -----")
    Ascent.all_info()

    # simple info without all the plots (uncomment to see)
    print("---------- ASCENT INFO ----------")
    Ascent.info()
    print("---------- DESCENT PRE-DEPLOYMENT INFO ----------")
    Descent1.info()
    print("---------- DESCENT POST-DEPLOYMENT INFO ----------")
    Descent2.info()
    print("---------- PAYLOAD INFO ----------")
    PayloadDescent.info()
    '''
