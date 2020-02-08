import abc
from typing import Dict

from app.base.exceptions import PyrError, PyrTypeError
from app.utils.date import to_timestamp, timestamp_to_str


class DataModel(metaclass=abc.ABCMeta):
    timestamp = None  # timestamp in second
    time = None  # readable time with timezone
    _timezone = None
    _timestamp = None
    _skip_timezone = False

    class DataParseError(PyrError):
        pass

    class DataTypeError(PyrTypeError):
        pass

    class DataRangeError(PyrError):
        pass

    class DataTimestampError(PyrError):
        pass

    class DataNoneValueError(PyrError):
        pass

    _data = None
    _errors: [PyrError] = []

    def __init__(self, init_data: Dict):
        self.set_data(init_data)

    def set_data(self, data: Dict = None):
        if data is not None:
            self.__dict__.update(data)

    def set_time(self, timestamp, timezone, skip=False):
        self._skip_timezone = skip
        self._timestamp = timestamp
        self._timezone = timezone

    def clean(self):
        self._clean()

    @abc.abstractmethod
    def _clean(self):
        """
        check and try to auto convert properties,
        put error into _errors
        """
        self._clean_timezone()

    def _clean_timezone(self):
        if self._skip_timezone:
            return
        if self._timezone is None:
            self._errors.append(self.DataTimestampError('Missing timezone information'))
        else:
            if isinstance(self._timestamp, str):
                self.timestamp = to_timestamp(self._timestamp, self._timezone)
            elif isinstance(self._timestamp, int):
                self.timestamp = self._timestamp
            else:
                self._errors.append(self.DataTimestampError('Timestamp must be str or int, bug got %s'
                                                            % type(self._timestamp)))

            if self.time is None:
                self.time = timestamp_to_str(self.timestamp)


    def is_valid(self):
        self._clean()
        return len(self._errors) == 0


class Environment(DataModel):
    temperature = None
    gradient = None

    def _clean(self):
        pass


class Physiologic(DataModel):
    heart_rate = None
    speed = None
    power = None

    def _clean(self):
        pass


class TravellerProfile(DataModel):
    wake_time = None
    sleep_time = None
    weight = None
    user_running_step_length = None
    user_walking_step_length = None
    gender = None
    age = None
    height = None
    language = None
    elev_setting = None
    weight_setting = None
    resting_heart_rate = None
    default_max_biking_heart_rate = None
    default_max_heart_rate = None
    hr_setting = None
    speed_setting = None
    dist_setting = None
    power_setting = None
    activity_class = None
    position_setting = None
    temperature_setting = None
    height_setting = None

    def _clean(self):
        pass


class Gear(DataModel):
    UNKNOWN = 'unknown'
    GEAR_TYPE_PHONE = 'phone'
    GEAR_TYPE_RIDE_COMPUTER = 'ride computer'
    GEAR_TYPE_CAMERA = 'camera'
    GEAR_TYPE_SPORT_CAMERA = 'sport camera'
    GEAR_TYPE_UAV = 'UAV'  # unmanned aerial vehicle

    type = None
    brand = None
    manufacturer = None
    model = None

    device_type = None
    software_version = None
    serial_number = None
    device_index = None
    garmin_product = None
    battery_voltage = None
    battery_status = None
    ant_network = None
    source_type = None
    cum_operating_time = None
    utc_offset = None
    time_offset = None
    time_mode = None
    time_zone_offset = None
    backlight_mode = None
    display_orientation = None
    number_of_screens = None

    def _clean(self):
        if self.type is None:
            self.type = self.UNKNOWN
        if self.brand is None:
            self._errors.append(self.DataNoneValueError("Gear's brand can not be none"))
        if self.manufacturer is None:
            self._errors.append(self.DataNoneValueError("Gear's manufacturer can not be none"))
        if self.model is None:
            self._errors.append(self.DataNoneValueError("Gear's model can not be none"))


class Activity(DataModel):
    sub_type = None
    start_time = None
    start_position_lat = None
    start_position_long = None
    total_elapsed_time = None
    total_timer_time = None
    total_distance = None
    total_cycles = None
    nec_lat = None
    nec_long = None
    swc_lat = None
    swc_long = None
    total_work = None
    time_in_hr_zone = None
    time_in_power_zone = None
    time_standing = None
    avg_left_power_phase = None
    avg_left_power_phase_peak = None
    avg_right_power_phase = None
    avg_right_power_phase_peak = None
    avg_power_position = None
    max_power_position = None
    message_index = None
    total_calories = None
    total_fat_calories = None
    enhanced_avg_speed = None
    avg_speed = None
    enhanced_max_speed = None
    max_speed = None
    avg_power = None
    max_power = None
    total_ascent = None
    total_descent = None
    first_lap_index = None
    num_laps = None
    normalized_power = None
    training_stress_score = None
    intensity_factor = None
    left_right_balance = None
    threshold_power = None
    stand_count = None
    event_type = None
    sport = None
    sub_sport = None
    avg_heart_rate = None
    max_heart_rate = None
    avg_cadence = None
    max_cadence = None
    event_group = None
    trigger = None
    avg_fractional_cadence = None
    max_fractional_cadence = None
    total_fractional_cycles = None
    avg_left_torque_effectiveness = None
    avg_right_torque_effectiveness = None
    avg_left_pedal_smoothness = None
    avg_right_pedal_smoothness = None
    avg_combined_pedal_smoothness = None
    sport_index = None
    avg_left_pco = None
    avg_right_pco = None
    avg_cadence_position = None
    max_cadence_position = None

    def _clean(self):
        pass


class Unclassified(DataModel):
    def _clean(self):
        pass
