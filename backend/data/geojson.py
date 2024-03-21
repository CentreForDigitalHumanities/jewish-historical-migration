"""Export to GeoJSON support."""
import json
from dataclasses import dataclass, field
from pathlib import Path

from typing import Dict, List, Union, Optional

import data.models as models

Feature = Dict[str, any]


@dataclass
class RecordData:
    languages: Optional[str]
    scripts: Optional[str]
    category1: Optional[str]
    category2: Optional[str]
    period: Optional[str]



@dataclass
class FeatureData:
    area: str
    province_region: str
    placename: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pleiades: Optional[int] = None
    records: List[RecordData] = field(default_factory=list)

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
                'Province_region': self.province_region,
                'area': self.area,
                'inscriptions-count': number_of_inscriptions
            }
        }
        if self.pleiades:
            feature['properties']['pleiades'] = self.pleiades
        return feature


def export_geojson(filepath: Path) -> None:
    """Export to GeoJSON."""
    places = models.Place.objects.all()
    features: List[Feature] = []
    # Go through list of places to get one feature per place
    for place in places:
        assert isinstance(place, models.Place)
        area = place.area.name if place.area else ""
        province_region = place.region.name if place.region else ""
        fd = FeatureData(area=area, province_region=province_region, placename=place.name,
                         pleiades=place.pleiades_id)
        if place.coordinates:
            fd.longitude, fd.latitude = place.coordinates.coords  # Point stores first x, then y
        records: List[models.Record] = list(place.records.all())
        number_of_inscriptions = ' + '.join([str(record.inscriptions_count) for record in records])
        features.append(fd.to_geojson_feature(number_of_inscriptions))

    geojson: Dict[str, Union[str, List[Feature]]] = {
        "type": "FeatureCollection",
        "features": features,
    }

    with open(filepath, 'w') as f:
        json.dump(geojson, f, indent=4)
