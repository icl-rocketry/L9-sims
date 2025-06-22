# imports
from math import exp
from rocketpy import Fluid, LiquidMotor, CylindricalTank, MassFlowRateBasedTank

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# Define fluids
ox_liq = Fluid(name="nitrous_l", density=1220)
ox_gas = Fluid(name="nitrous_g", density=1.977)
fuel_liq = Fluid(name="ethanol_l", density=789)
fuel_gas = Fluid(name="ethanol_g", density=0.79)
press_liq = Fluid(name="nitrogen_l", density=807)
press_gas = Fluid(name="nitrogen_g", density=12.51*17)

# Define tanks geometry
# TODO: use custom endcaps if the geometry is not a perfect sphere
ox_shape = CylindricalTank(radius = 0.185/2, height = 0.71, spherical_caps = False)
fuel_shape = CylindricalTank(radius = 0.185/2, height = 0.2881, spherical_caps = False)
press_shape = CylindricalTank(radius = 0.157/2, height = 0.56, spherical_caps = True)

# Define tanks
ox_tank = MassFlowRateBasedTank(
    name="oxidizer tank",
    geometry=ox_shape,
    flux_time=7.95,
    initial_liquid_mass=16.06,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=16.06 / 7.96,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0,
    liquid=ox_liq,
    gas=ox_gas,
)

fuel_tank = MassFlowRateBasedTank(
    name="fuel tank",
    geometry=fuel_shape,
<<<<<<< Updated upstream
    flux_time=9.35,
    initial_liquid_mass=6.44,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=6.44 / 9.36,
=======
    flux_time=7.95,
    initial_liquid_mass=5.35,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out= 5.35 / 7.96,
>>>>>>> Stashed changes
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0,
    liquid=fuel_liq,
    gas=fuel_gas,
)

press_tank = MassFlowRateBasedTank(
    name="nitrogen tank",
    geometry=press_shape,
    flux_time=7.95,
    initial_liquid_mass=0,
    initial_gas_mass=2.06,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=0,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out= 2.06 / 7.95,
    liquid=press_liq,
    gas=press_gas,
)

# Define motor
# if the thrust curve is changed, define a specific impulse variable so we can calculate the mass flow rate of the propellants
Goofy = LiquidMotor(
    thrust_source="rocketpy/ThanosR40.eng",
    dry_mass=2.7, # mass of engine, not tanks!
    dry_inertia=(0.6050, 0.6094, 0.1004),
    nozzle_radius=0.025,
    center_of_dry_mass_position=0.28,
    nozzle_position=0,
    burn_time=7.95,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)
Goofy.add_tank(tank=ox_tank, position=4.31 - 2.92 - 0.719/2)
Goofy.add_tank(tank=fuel_tank, position=4.31 - 2.32 - 0.288/2)
Goofy.add_tank(tank=press_tank, position=4.31 - 1.59 - 0.56/2)