# imports
from math import exp
from rocketpy import Fluid, LiquidMotor, CylindricalTank, MassFlowRateBasedTank

import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

length = 4.51  # (m), to convert from openrocket layout to rocketpy coordinate system

# Define fluids
ox_liq = Fluid(name="nitrous_l", density=1220)
ox_gas = Fluid(name="nitrous_g", density=1.977)
fuel_liq = Fluid(name="ethanol_l", density=789)
fuel_gas = Fluid(name="ethanol_g", density=0.79)
press_liq = Fluid(name="nitrogen_l", density=807)
press_gas = Fluid(name="nitrogen_g", density=1.251)

# Define tanks geometry
# TODO: use custom endcaps if the geometry is not a perfect sphere
ox_shape = CylindricalTank(radius=0.185 / 2, height=0.840, spherical_caps=True)
fuel_shape = CylindricalTank(radius=0.185 / 2, height=0.404, spherical_caps=True)
press_shape = CylindricalTank(radius=0.157 / 2, height=0.535, spherical_caps=True)

# Define tanks
ox_tank = MassFlowRateBasedTank(
    name="oxidizer tank",
    geometry=ox_shape,
    flux_time=6.95,
    initial_liquid_mass=16.06,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=16.06 / 6.96,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0,
    liquid=ox_liq,
    gas=ox_gas,
)

fuel_tank = MassFlowRateBasedTank(
    name="fuel tank",
    geometry=fuel_shape,
    flux_time=6.95,
    initial_liquid_mass=5.35,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=5.35 / 6.96,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0,
    liquid=fuel_liq,
    gas=fuel_gas,
)

press_tank = MassFlowRateBasedTank(
    name="nitrogen tank",
    geometry=press_shape,
    flux_time=6.95,
    initial_liquid_mass=2.06,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=2.06 / 6.96,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0,
    liquid=press_liq,
    gas=press_gas,
)

# Define motor
# if the thrust curve is changed, define a specific impulse variable so we can calculate the mass flow rate of the propellants
Kerberos = LiquidMotor(
    thrust_source="rocketpy/Kerberos_TC.eng",
    dry_mass=0,  # mass of engine, not tanks!
    #dry_inertia=(0.6050, 0.6094, 0.1004),
    dry_inertia=(0, 0., 0),
    nozzle_radius=0.025,
    center_of_dry_mass_position=1.0824,
    nozzle_position=0,
    burn_time=6.95,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)
Kerberos.add_tank(tank=ox_tank, position=length - 2.94)
Kerberos.add_tank(tank=fuel_tank, position=length - 3.56)
Kerberos.add_tank(tank=press_tank, position=length - 1.89)
