"""Export to GeoJSON support."""
import json
from dataclasses import dataclass, field
from pathlib import Path

from typing import Dict, List, Union, Optional

import data.models as models
from .serializers import RecordSerializer

Feature = Dict[str, any]


@dataclass
class FeatureData:
    area: str
    province_region: str
    placename: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pleiades: Optional[int] = None
    record_data: List[Dict] = field(default_factory=list)

    def to_geojson_feature(self, number_of_inscriptions: Union[int, str]) -> \
            Optional[Feature]:
        feature: Feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    self.longitude,
                    self.latitude
                ]  # GeoJSON uses this order but it is different to daily use
            },
            'properties': {
                'placename': self.placename,
                'Province_region': self.province_region,
                'area': self.area,
                'inscriptions-count': number_of_inscriptions,
                'records': self.record_data,
            }
        }
        if self.pleiades:
            feature['properties']['pleiades'] = self.pleiades
        return feature


def create_geojson() -> Dict:
    """Export to GeoJSON as a Python dictionary."""
    places = models.Place.objects.prefetch_related("records").all()
    features: List[Feature] = []
    # Go through list of places to get one feature per place
    for place in places:
        assert isinstance(place, models.Place)
        records: List[models.Record] = list(place.records.all())
        if len(records) == 0:
            # We do not want to plot places on the map for which there are no records.
            continue
        area = place.area.name if place.area else ""
        province_region = place.region.name if place.region else ""
        fd = FeatureData(area=area, province_region=province_region, placename=place.name,
                         pleiades=place.pleiades_id)
        if place.coordinates:
            fd.longitude, fd.latitude = place.coordinates.coords  # Point stores first x, then y
        record_data: List[Dict] = []
        number_of_inscriptions = 0
        for record in records:
            number_of_inscriptions += record.inscriptions_count
            record_data.append(RecordSerializer(record).data)
        fd.record_data = record_data
        features.append(fd.to_geojson_feature(number_of_inscriptions))

    geojson: Dict[str, Union[str, List[Feature]]] = {
        "type": "FeatureCollection",
        "features": features,
    }
    return geojson


def export_geojson(filepath: Path, ) -> None:
    with open(filepath, 'w') as f:
        json.dump(create_geojson(), f, indent=4)