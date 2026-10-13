# Data access and methods for the satellite prospection study

Official sources and APIs were checked on 12 October 2026. Unsigned access works for the selected Sentinel-2, Copernicus elevation and WorldCover objects. The [bounded probe](data-access-probe.json) contains catalogue responses and 13 successful 512-byte TIFF-header requests; two separately preserved follow-ups bring the total to 15 requests and 7,680 raster bytes. The [source register](data-source-register.json) links the original responses, corrected documentation route, product XML and applicable licence terms. These observations establish access and schema, with pixel analysis left to the separate extraction pipeline.

## Catalogue selection and item identity

Pin `https://earth-search.aws.element84.com/v1` with collection `sentinel-2-c1-l2a` for this run. Its COGs are the Collection 1 reprocessing. The operator currently describes v2 as beta, with this data renamed `sentinel-2-l2a`. API version and collection name jointly identify the dataset. The probes confirm the same 2024 item ID and object checksum across v1/C1 and v2. [Element 84 collection documentation](https://github.com/Element84/earth-search/blob/main/docs/collections/sentinel-2-l2a.md)

| API/collection | Observed metadata and use |
|---|---|
| v1 `sentinel-2-c1-l2a` | STAC1.0.0; explicit HTTPS COGs, scale/offset in `raster:bands`; tested 2019, 2024 and 2026 items |
| v1 `sentinel-2-l2a` | Original collection with COG and JP2 assets; tested items have an offset flag inconsistent with their band offset |
| v1 `sentinel-2-pre-c1-l2a` | Listed in the live catalogue; no item returned by the bounded 2019 query |
| v2 `sentinel-2-l2a` | STAC1.1.0; Collection 1 item; asset-level scale/offset and S3 storage references |
| v1 `cop-dem-glo-30` | One elevation asset per inspected tile, public S3 href with `requester_pays=false` |

A bounded GET request to `/search` used `collections`, longitude/latitude `bbox`, an ISO 8601 interval, `limit=2` and `query={"eo:cloud_cover":{"lt":5}}` for imagery. A production search should follow pagination, retain the complete query and freeze the chosen item JSON. Scene-wide cloud percentage screens candidates for access; local per-pixel masks determine whether the actual study window is usable. Item `datetime` is sensing time; baseline and metadata identify subsequent reprocessing. The 2019 Collection 1 example has baseline 05.00, so acquisition year cannot select the gain/offset rule. Adjacent MGRS tiles and repeat processing versions can share one acquisition; record that dependence before constructing seasonal summaries.

## Reflectance and grid schema

Use `reflectance=DN×scale+offset`, with reflectance-band no-data excluded first. In the 2024 C1 example `S2A_T42RXS_20241225T055244_L2A`, `red` and `nir` are uint16, no-data 0, scale 0.0001 and offset−0.1. Its public `product_metadata.xml` reports baseline 05.11, quantification 10000 and additive offset−1000 for the listed bands, which gives the same conversion. The 2026 example has baseline 05.13 and the same declared coefficients. A decoder should read each selected asset's coefficients and apply them once; a library's raw array read and any explicit physical-value conversion must have a recorded contract. [Copernicus radiometry](https://sentiwiki.copernicus.eu/web/s2-products), [STAC raster specification](https://github.com/stac-extensions/raster/blob/v1.1.0/README.md)

| Quantity | v1 fields | v2 fields observed |
|---|---|---|
| Scale/offset | `assets.red["raster:bands"][0].scale/offset` | `assets.red["raster:scale"]` and `raster:offset` |
| No-data/type | Band object `nodata`, `data_type` | Core asset `nodata`, `data_type` |
| Horizontal CRS | Item `proj:epsg` | Item `proj:code`, such as `EPSG:32642` |
| Grid | Asset `proj:shape`, `proj:transform` | Same grid fields |
| Storage | HTTPS href or S3 href with storage metadata | S3 href plus `storage:refs` and item `storage:schemes` |

`nir` is B08 at 10 m. `nir08` is the narrow B8A band at 20 m; the choice should remain consistent across dates. B11/B12 and SCL are 20 m in the inspected items. Use actual asset transforms when aligning these with 10 m bands. Categorical masks require nearest-neighbour or declared modal resampling. Continuous reflectance can use a declared continuous interpolator; resampling does not add native spatial information. Baseline-dependent surface reflectance can include negative valid values, which need separate treatment from no-data.

The legacy 2024 item declares `earthsearch:boa_offset_applied=true` alongside `raster:bands.offset=-0.1`. A [project issue](https://github.com/Element84/earth-search/issues/66) reports this class of ambiguity. This audit did not compare its raster pixels. Keeping the tested C1 assets and product-metadata witness avoids basing this run's decoding on that legacy flag.

## Per-pixel quality

The inspected C1 items expose `scl`, `cloud` (`CLD_20m.tif`) and `snow` (`SNW_20m.tif`), together with granule and product metadata. The cloud header also passed an unsigned range request. An initial conservative terrestrial mask can retain SCL 4 vegetation and 5 nonvegetated land, then apply declared cloud/snow thresholds and window coverage requirements. Class 6 water and 7 unclassified need explicit context rules. [Copernicus scene classification, Table 3](https://sentiwiki.copernicus.eu/web/s2-processing)

| SCL | Meaning for quality screening |
|---|---|
| 0,1 | No data; saturated or defective |
| 2,3 | Cast/dark shadows; cloud shadows |
| 4,5 | Vegetation; nonvegetated land |
| 6,7 | Water; unclassified |
| 8,9,10,11 | Medium/high cloud probability; thin cirrus; snow/ice |

Cloud and snow layers encode probabilities and their metadata declares no-data 0. Zero is also the clear endpoint of a probability scale, so this declaration alone cannot distinguish clear pixels from unavailable ones. Use spectral no-data and SCL validity, then screen the raw probability values under a documented rule. This is a schema interpretation requiring confirmation in the extraction contract. Full SAFE products have additional quality masks; availability of SCL and probabilities should not be reported as acquisition of every band-specific defect mask. Record retained area and valid observations per pixel so mosaics with unequal usable coverage can be compared.

## Elevation access and limits

The Ganweriwala example is `Copernicus_DSM_COG_10_N28_00_E071_00_DEM`. Its public asset can be addressed as:

`https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/Copernicus_DSM_COG_10_N28_00_E071_00_DEM/Copernicus_DSM_COG_10_N28_00_E071_00_DEM.tif`

The same unsigned scheme worked for N 26 E 067 near Kirthar and N 29 E 074 near Kalibangan. The naming component 10 denotes 1.0 arcsecond rather than 10 metres. The AWS conversion retains 3600 rows at these latitudes and removes shared east/south posts. Read the affine transform: the inspected tile's corner is offset by half a post from an integer degree. Native GLO-30 is geographic sampling, approximately 31 m north–south and 27 m east–west near 28.6°N. Compute metric slope, distance and area in an appropriate projected grid. [AWS conversion documentation](https://copernicus-dem-30m.s3.amazonaws.com/readme.html)

Copernicus is an edited DSM, principally based on 2011–2015 TanDEM-X, with other elevation data filling gaps. It includes buildings and vegetation; water flattening and edits can produce artificial relief edges. Its horizontal reference is WGS 84-G 1150 and vertical reference EGM 2008, with heights in metres. The published specifications are absolute vertical error<4 m at 90% linear error and relative error<2 m on slopes≤20% or<4 m above 20%, within a 1°×1°cell. These are product specifications rather than local pixel confidence intervals. The three AWS/STAC items expose elevation only. The source handbook's height-error mask excludes systematic and unwrapping errors, and is absent from those items. Small-relief candidates therefore need comparison against modern structures, neighbouring terrain, acquisition artefacts and field measurements. [Product specifications](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM), [handbook§1.2.5.3](https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf)

The AWS registry describes its mirror as the 2021 release. CDSE now lists later releases including 2024_1. Retain the actual mirror and item identity; the catalogue item's 2021 timestamp does not date every underlying elevation observation. Missing land tiles require unresolved coverage accounting; ocean conventions cannot supply replacement land heights. [AWS dataset description](https://registry.opendata.aws/copernicus-dem/)

## WorldCover controls and attribution

WorldCover 2021 v200 provides 10 m classes in 3°tiles. Both N 27 E 069 and N 24 E 066 map COG headers were accessible unsigned. Class 50 includes buildings, roads and railways; waste dumps and extraction sites belong to class 60. Record built-up fraction and distance to class 50, and compare candidate behaviour near these modern features. Water and tree cover also matter for DSM interpretation. Current imagery should check development since 2021; WorldCover 2020/2021 differences also contain algorithm changes. The global validation's built-up user accuracy is 65.9±3.3%, so a local class label remains a screening observation. [ManualTable 3](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf), [validationTable 2](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PVR_V2.0.pdf)

WorldCover's InputQuality layer records input observations and discarded-S2 percentage. It is a different quantity from the probability that a built-up label is correct. The provider currently lists that layer through authenticated viewer/Terrascope routes; the tested unsigned map access does not include it. Any construction exclusion or buffer should be fixed in the protocol, with excluded-area accounting and a sensitivity comparison appropriate to the intended search setting. [Data-access documentation](https://esa-worldcover.org/en/data-access)

## Licence record for transformed products

The catalogue's licence vocabulary is coarse: the inspected v1 collections use `proprietary`, while v2 Sentinel uses `other`. The linked provider terms permit the uses summarized below. Our raw acquired metadata and source documents remain ignored local witnesses; the authored methods and access record are reusable project work.

| Contributing data | Applicable rights and notice |
|---|---|
| Sentinel-2 | Copernicus Sentinel notice permits modification/combination. Use “Contains modified Copernicus Sentinel data [Year]” for transformed imagery, with its contributing acquisition years and EarthSearch access/processing provenance. [Legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice) |
| Copernicus GLO-30 | GLO-30-F free/open provider licence permits adaptation and distribution. Apply its Article 6(b) modified-data notice naming WorldDEM-30, DLR 2010–2014, Airbus 2014–2018, COPERNICUS, EU and ESA. Carry the associated liability/endorsement conditions. Dataset DOI:10.5270/ESA-c 5 d 3 d 65. [Actual licence, PDFpp.21–23](https://s3.waw3-1.cloudferro.com/swift/v1/portal_uploads_prod/CSCDA_ESA_Mission-specific_Annex_31_Oct_22_latest.pdf) |
| WorldCover 2021 v200 | CC BY 4.0; cite Zanaga etal.(2022), DOI 10.5281/zenodo.7254221, the licence and changes. Retain the provider's ESA WorldCover 2021/modified Sentinel 2021 attribution. [Provider citation and terms](https://esa-worldcover.org/en/data-access) |

A combined map or exported derivative should retain these component notices and a record of cropping, reprojection, resampling, masking and scaling. The source register supplies notice components and exact primary links. No blanket licence is assigned to a mixed source-data product.
