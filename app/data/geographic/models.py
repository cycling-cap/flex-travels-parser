from typing import Dict

from app.data.geographic.constants import LONGITUDE_RANGE, LATITUDE_RANGE
from app.data.geographic.utils import semicircle_to_degree
from app.data.models import DataModel


class Coordinate(DataModel):
    longitude: float = None
    latitude: float = None
    altitude: float = None
    datum: str = None
    address: str = None
    _org_altitude: float = None

    def set_data(self, data: Dict = None):
        self._org_altitude = self.altitude
        super().set_data(data)

    @property
    def location(self):
        self._get_location()
        if self.is_valid():
            return self.longitude, self.latitude, self.altitude, self.address, self._org_altitude
        else:
            return None, None, None, None, None

    @property
    def position(self):
        if self.is_valid():
            return self.longitude, self.latitude
        else:
            return None, None

    def _get_location(self):
        """
        TODO get address
        TODO correct altitude
        parse readable address and correct altitude
        """
        pass

    def _clean(self):
        self._clean_coordinate()

    def _clean_coordinate(self):
        if self.longitude > LONGITUDE_RANGE[1]:
            self.longitude = semicircle_to_degree(self.longitude)
        if self.latitude > LATITUDE_RANGE[1]:
            self.latitude = semicircle_to_degree(self.latitude)
        if not (LATITUDE_RANGE[0] < self.latitude < LATITUDE_RANGE[1]):
            self.error(DataModel.DataRangeError('latitude must between %s and %s, but %s have been set'
                                                % (LATITUDE_RANGE[0], LATITUDE_RANGE[1], self.latitude)))
        if not (LONGITUDE_RANGE[0] < self.longitude < LONGITUDE_RANGE[1]):
            self.error(DataModel.DataRangeError('latitude must between %s and %s, but %s have been set'
                                                % (LONGITUDE_RANGE[0], LONGITUDE_RANGE[1], self.latitude)))


class Geographic(DataModel):
    position: Coordinate = None

    def _clean(self):
        pass
