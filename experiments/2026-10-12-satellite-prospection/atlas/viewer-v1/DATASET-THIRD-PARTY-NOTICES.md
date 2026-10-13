# Data and map component notices

These notices cover the transformed images, terrain plots and land-cover descriptors in this study. The raw raster windows, full source publications and unresolved-rights material remain in the ignored local data directory. No external publication is authorized by this work.

## Sentinel-2

Contains modified Copernicus Sentinel data (2025, 2026). The source scenes were accessed through Element84 Earth Search, collection `sentinel-2-c1-l2a`, on 12 October 2026. The transformation comprises cropping, per-asset reflectance scaling, reprojection, resampling, cloud/class masking, fixed colour display and derived indices. The [Copernicus Sentinel legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice) governs the source data. Scene identifiers, dates and transformations are retained in the acquisition and processing manifests.

The WorldCover component below incorporates modified Sentinel data from 2021 separately.

## Copernicus GLO-30 surface elevation

produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.

The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.

The study is not endorsed by the Provider, the Licensor or the organisations responsible for Copernicus. Subsequent users who distribute or communicate these data or derivatives must carry the source/modification notice, liability notice and the obligations of Article 6. The provider retains source intellectual-property rights. The licence grants worldwide, free rights to reproduce, distribute, communicate, adapt, modify and combine the data.

Applicable terms: [CSCDA ESA Mission-specific Annex, 31 October 2022](https://s3.waw3-1.cloudferro.com/swift/v1/portal_uploads_prod/CSCDA_ESA_Mission-specific_Annex_31_Oct_22_latest.pdf), PDF pages 21-23, licence for COP-DEM-GLO-30-F, Articles 4-6. Dataset DOI: [10.5270/ESA-c5d3d65](https://doi.org/10.5270/ESA-c5d3d65). This study uses the AWS mirror's 2021 release. The principal TanDEM-X acquisition epoch is 2011-2015, with additional fill sources; the DSM is not a 2026 ground-surface survey.

Transformations: cropped source windows, native-metric grid reprojection at 30 m, mosaicking, smoothing, background subtraction, relief descriptors and coloured elevation/hillshade plots. Elevations are referenced to EGM2008 and include buildings and vegetation.

## ESA WorldCover

© ESA WorldCover project 2021. Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.

Zanaga et al. (2022), *ESA WorldCover 10 m 2021 v200*. Dataset DOI: [10.5281/zenodo.7254221](https://doi.org/10.5281/zenodo.7254221). Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Official [data access and citation terms](https://esa-worldcover.org/en/data-access).

Transformations: cropping, reprojection, nearest-neighbour categorical display, area-averaged binary class fractions on the 30 m analysis grid, class masking and derived distances. The map represents 2021 land cover. Local class accuracy and current land use were not independently verified.

## Geographic context and viewer

Made with Natural Earth. The 1:110 million country and coastline data are public domain under the [official terms](https://www.naturalearthdata.com/about/terms-of-use/). Source commit and hashes are recorded in `atlas/vendor/natural-earth/acquisition.json`. Boundaries provide geographic context and do not encode archaeological or historical territory.

Leaflet 1.9.4 uses the BSD-2-Clause licence, preserved in `atlas/vendor/leaflet-1.9.4/LICENSE`. The release files and hashes are preserved with their acquisition record.

Optional online context: © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright). No OSM tiles are included. Ordinary interactive viewport use must follow the [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/). Automated QA leaves this layer disabled.

## Archaeological and historical observations

Only selected factual coordinate observations, source locators, bibliographic records and an explicitly labelled historical-map coverage footprint are included. Source witnesses remain local. The Cutch No. 6 footprint represents the published metadata coverage of an 1884 map, not archaeological geometry or a palaeochannel. No map scan or complete archaeological gazetteer is redistributed. Complete source handling is recorded in the source register and the project redistribution policy.
