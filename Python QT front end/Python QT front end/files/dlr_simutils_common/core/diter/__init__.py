import sys
import pathlib
import shutil

import google.protobuf.text_format

from . import dtr_pb2


_DITER_EXE_NAME = 'dtr1d_main.exe' if sys.platform.startswith('win') else 'dtr1d_main'

# Find DiTeR executable in PATH
diter_exe = shutil.which(_DITER_EXE_NAME)
if not diter_exe:
    # If executable is not in the PATH, try the package directory
    diter_exe = pathlib.Path(__file__).parent / _DITER_EXE_NAME
    if not diter_exe.is_file():
        diter_exe = None
else:
    diter_exe = pathlib.Path(diter_exe)


def write_request_to_protobuffer(pbd_file, request):
    pbd_file = pathlib.Path(pbd_file)
    pbd_file.write_text(
        google.protobuf.text_format.MessageToString(request)
    )


def generate_simulation_request(
    line_data,
    measurements_data,
    presimulation_time=0,
    discrete_time_step=10,
):

    '''    '''
    # Create simulation request
    simulation_request = dtr_pb2.SimulationRequest()

    # 1. Parameters
    # 1.1 Constants of nature
    nature_constants = simulation_request.parameters.constants_of_nature

    water_constants = nature_constants.water
    water_constants.density = 1000  # water density [kg / m^3]
    water_constants.latent_heat_fusion = 336000  # latent heat of fusion (freezing) [J / kg]
    water_constants.latent_heat_evaporation = 2500000  # latent heat of evaporation [J / kg]
    water_constants.latent_heat_sublimation = 2834000  # latent heat of sublimation [J / kg]
    water_constants.specific_heat_ice = 2050  # specific heat of ice (cp) [J / kg K]
    water_constants.specific_heat_water = 4210  # specific heat of water [J / kg K]

    air_constants = nature_constants.air
    air_constants.specific_heat = 1005  # specific heat of air [J / kg K]
    # air_constants.density = ?  # density of air -- if not present, computed during simulation [kg / m^3]
    # air_constants.viscosity = ?  # kinematic viscosity of air -- as above [m^2 / s]
    # air_constants.thermal_conductivity = ?  # thermal conductivity of air -- as above [W / m K]

    nature_constants.stefan_constant = 5.67e-8  # Stefan constant [W / m^2 K^4]
    nature_constants.molar_mass_ratio = 0.62  # ratio of molar masses of water vapor and dry air
    nature_constants.gas_constant = 461  # gas constant [J / K mol]
    nature_constants.kelvin_celsius_diff = 273.15  # difference between Celsius and Kelvin unit (positive number) [deg C]

    # 1.2 Numerical setup
    numerical_setup = simulation_request.parameters.numerical_setup

    numerical_setup.num_nodes = 100  # number of nodes in discretization
    numerical_setup.time_step = discrete_time_step  # time step of the implicit Euler [s]
    numerical_setup.steady_state_crit = -1  # finish when temperature changes less than this (negative value disables it) [deg C]; NOTE: must be disabled, because we want main simulation to go through all steps!
    # numerical_setup.start time = ?  # start simulation at this time, not the first one in the data [s]
    # numerical_setup.set_end time = ?  # not required // end simulation at this time, not the last one in the data [s]
    numerical_setup.initial_skin_temperature = 0  # initial temperature of line skin [deg C]
    numerical_setup.initial_electrical_current = 0  # initial current flowing through the line [A]
    numerical_setup.radial_distribution = 1  # do we use radial distribution of lambda or not
    numerical_setup.output_rate = -1  # write data every "output_rate" time steps, if 0, don't write at all, if -1, write only at measurement points
    numerical_setup.presimulation_time = presimulation_time  # start running the model this many seconds early so that we mitigate the error caused by model response [s]
    numerical_setup.debug_level = 2  # how verbose do you want the output to be (0 = no output, 2 = error, 5 = info, 7 = full trace)
    # numerical_setup.initial_temperature_distribution = ?  #initial radial temperature distribution [deg C]. If not given, ait is constructed from `initial_skin_temperature`.

    # 1.3 Line properties
    line_properties = simulation_request.parameters.line_properties

    # 1.3.1 Inner material
    inner_material = line_properties.inner_material
    inner_material.density = line_data['inner_part_specific_weight']  # density of the material [kg / m^3]
    inner_material.specific_heat = line_data['inner_part_specific_heat']  # isobaric specific heat capacity [J / kg K]
    inner_material.specific_heat_alpha = line_data['inner_part_specific_heat_coefficient']  # specific heat linear temperature coefficient, measured with respect to 20 deg C [1 / K]
    inner_material.resistivity_alpha = line_data['inner_part_resistivity_coefficient']  # resistivity temperature coefficient, measured with respect to 20 deg C [1 / K]
    inner_material.electric_conductivity = line_data['inner_part_specific_conductivity']  # specific electric conductivity [1 / m ohm]
    inner_material.area = line_data['inner_part_cross_section'] / 1000000  # cross section area of the material [m^2]
    inner_material.radius = 0.5 * line_data['inner_part_diameter'] / 1000  # radius of material [m]
    inner_material.porosity = -1  # porosity factor for density due to strand packing. If negative, it is computed from area and effective area. Value 1 has no effect.

    # 1.3.2 Outer material
    outer_material = line_properties.outer_material
    outer_material.density = line_data['outer_part_specific_weight']  # density of the material [kg / m^3]
    outer_material.specific_heat = line_data['outer_part_specific_heat']  # isobaric specific heat capacity [J / kg K]
    outer_material.specific_heat_alpha = line_data['outer_part_specific_heat_coefficient']  # specific heat linear temperature coefficient, measured with respect to 20 deg C [1 / K]
    outer_material.resistivity_alpha = line_data['outer_part_resistivity_coefficient']  # resistivity temperature coefficient, measured with respect to 20 deg C [1 / K]
    outer_material.electric_conductivity = line_data['outer_part_specific_conductivity']  # specific electric conductivity [1 / m ohm]
    outer_material.area = line_data['outer_part_cross_section'] / 1000000  # cross section area of the material [m^2]
    outer_material.radius = 0.5 * line_data['outer_part_diameter'] / 1000  # radius of material [m]
    outer_material.porosity = -1  # porosity factor for density due to strand packing. If negative, it is computed from area and effective area. Value 1 has no effect.

    # 1.3.3 Common
    line_properties.line_altitude = line_data['line_altitude']  # altitude (height above sea level) of the part of the line for which the simulation is run
    line_properties.line_angle = line_data['line_orientation']  # line angle with respect to the ground, measured from 0 to 360 deg from a certain global axis

    line_properties.thermal_conductivity = line_data['effective_radial_thermal_conductivity']  # thermal conductivity of the line (outer material) [W / m K]
    line_properties.num_outer_strands = round(line_data['outer_part_number_of_wires'] ) # number of wires (strands) in outer part
    line_properties.single_strand_radius = 0.5 * line_data['outer_part_diameter_of_wire'] / 1000  # radius of a single wire (strand) [m]
    line_properties.wetted_factor = line_data['wetted_factor']  # ratio of wetted area of conductor (used for evaporation)
    line_properties.impinging_factor = line_data['impinging_factor']   # ratio of impinging water that reaches the skin temp. 0.7 [Zsolt]
    line_properties.recovery_factor = line_data['recovery_factor']   # recovery factor (= 0.79) (friction heating)
    line_properties.skin_effect = line_data['skin_effect_factor']   # skin effect factor
    line_properties.emissivity = line_data['emissivity']   # emissivity of the line (outer material)
    line_properties.absorptivity = line_data['absorptivity']   # absorptivity of the line (outer material)
    line_properties.rough_surface_correction = line_data['rough_surface_correction']   # correction due to rough line surface for flux computation. If negative, it is computed from other parameters. Value of 1 means no correction.
    line_properties.maximal_temperature = line_data['critical_temperature']   # maximal allowed temperature this line [deg C]

    # To which part of the conductor does maximal temperature refer to?
    # This impacts the definition of the thermal current.
    # SKIN, CORE, or AVG
    # CIGRE model requires SKIN, RADIAL can work with either
    line_properties.thermal_current_def = dtr_pb2.LineProperties.CORE

    # CIGRE vs IEEE convection model
    convection_model = line_data.get('convection_model', 'cigre').lower()
    line_properties.convection_model = (
        dtr_pb2.LineProperties.IEEE if convection_model == 'ieee'
        else dtr_pb2.LineProperties.CIGRE
    )

    # Nusselt parameters
    # 3 values of "B" for different ranges of Reynolds number in Nu = B*Re^n calculation
    line_properties.nusselt_base.append(line_data['nusselt_base_1'])
    line_properties.nusselt_base.append(line_data['nusselt_base_2'])
    line_properties.nusselt_base.append(line_data['nusselt_base_3'])
    # 3 values of "n" for different ranges of Reynolds number in Nu = B*Re^n calculation
    line_properties.nusselt_exponent.append(line_data['nusselt_exp_1'])
    line_properties.nusselt_exponent.append(line_data['nusselt_exp_2'])
    line_properties.nusselt_exponent.append(line_data['nusselt_exp_3'])

    # 2. Numerical setup: inner simulations for time-to-overheat
    time_to_overheat_setup = simulation_request.time_to_overheat_setup
    # time_to_overheat_setup.num_nodes = ?  # number of nodes in discretization
    # time_to_overheat_setup.time_step = ?  # time step of the implicit Euler [s]
    # time_to_overheat_setup.steady_state_crit = 1e-6  # finish when temperature changes less than this (negative value disables it) [deg C]; NOTE: we override value from main simulation setup!
    time_to_overheat_setup.duration = 3600  # run simulation for at most this long [s]
    # time_to_overheat_setup.radial_distribution = ?  # do we use radial distribution of temperature or not
    # time_to_overheat_setup.debug_level = ?  # how verbose do you want the output to be (0 = no output, 2 = error, 5 = info, 7 = full trace)

    # 3. Numerical setup: non-linear solver for radial model
    nonlinear_solver_parameters = simulation_request.nonlinear_solver_parameters
    nonlinear_solver_parameters.min_current = 0  # bisection min current [A]
    nonlinear_solver_parameters.max_current = 2500  # bisection max current [A]
    nonlinear_solver_parameters.current_precision = 1  # how precisely to determine the current [A]
    nonlinear_solver_parameters.temperature_precision = 1e-4  # how precisely to determine the temperature [deg C]

    inner_simulation_setup = nonlinear_solver_parameters.inner_simulation_setup  # numerical setup for simulations performed by the nonlinear_solver
    # inner_simulation_setup.num_nodes = ?  # number of nodes in discretization
    # inner_simulation_setup.time_step = ?  # time step of the implicit Euler [s]
    # inner_simulation_setup.steady_state_crit = 1e-6  # finish when temperature changes less than this (negative value disables it) [deg C]; NOTE: we override value from main simulation setup!
    inner_simulation_setup.duration = 3600  # run simulation for at most this long [s]
    # inner_simulation_setup.radial_distribution = ?  # do we use radial distribution of temperature or not
    # inner_simulation_setup.debug_level = ?  # how verbose do you want the output to be (0 = no output, 2 = error, 5 = info, 7 = full trace)
    inner_simulation_setup.initial_skin_temperature = 0  # initial temperature of line skin [deg C]. If not given, ambient temperature of the first measurement is used
    inner_simulation_setup.initial_electrical_current = 0  # initial current flowing through the line [A]. If not given it defaults to 0

    nonlinear_solver_parameters.max_iterations = 30  # maximal number of iterations of bisection, this implies the precision of the current
    nonlinear_solver_parameters.debug_level = 2  # how verbose do you want the bisection output to be (0 = no output, 2 = error, 5 = info, 7 = full trace)

    # 4. Computation mode
    simulation_request.current_computation_mode = dtr_pb2.SimulationRequest.RADIAL_MODEL  # always use radial model

    # 5. Output folder
    simulation_request.output_folder = 'simulation_output'

    # 6. Measurements (data points)
    for measurements_data_entry in measurements_data:
        measurements = simulation_request.parameters.measurements.add()

        measurements.time = measurements_data_entry['time']

        measurements.ambient_temperature = measurements_data_entry['ambient_temperature']
        measurements.droplet_temperature = measurements_data_entry['ambient_temperature']

        measurements.wind_velocity = measurements_data_entry['wind_speed']
        measurements.wind_angle = measurements_data_entry['wind_direction']
        measurements.pressure = 100 * measurements_data_entry['air_pressure']  # mBar -> kPa
        measurements.rain_rate = measurements_data_entry['rain_rate']
        measurements.humidity = measurements_data_entry['relative_humidity']
        measurements.solar_irradiance = measurements_data_entry['solar_irradiance']

        measurements.electrical_current = measurements_data_entry['line_load']

    # Set initial current and skin temperature from the input data,
    # if available.
    if simulation_request.parameters.measurements:
        first_measurement = simulation_request.parameters.measurements[0]

        numerical_setup = simulation_request.parameters.numerical_setup
        numerical_setup.initial_skin_temperature = first_measurement.ambient_temperature
        numerical_setup.initial_electrical_current = first_measurement.electrical_current

        # NOTE: simulation_request.nonlinear_solver_parameters.inner_simulation_setup
        # also has initial_skin_temperature and initial_electrical_current
        # fields, but those need to be set to 0 to match the behavior of
        # the libdtr-diter wrapper (where this is necessary and to ensure
        # that incremental online computations work as expected).

    return simulation_request
