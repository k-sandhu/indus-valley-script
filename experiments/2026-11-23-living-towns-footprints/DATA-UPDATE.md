# Data update record: living-town buried urban footprints

Date: 2026-11-23.
Package: `experiments/2026-11-23-living-towns-footprints/`.
Target shared registers (for maintainer integration after merge; untouched here): `knowledge/DATA.md` and `data/MANIFEST.json`.

## Summary of coverage gains

This package closes a spatial-metadata gap identified in `knowledge/DATA.md` and `experiments/2026-10-26-indus-living-atlas/living-towns/REPORT.md`, where living-town candidates carried only 5 km index coordinates and no delimited archaeological or modern-overlap polygons. We add:

1. **Three versioned four-layer GeoJSON packages** (`harappa-windows-v1.geojson`, `lakhanjo-daro-windows-v1.geojson`, `rupnagar-windows-v1.geojson`) containing 91 verified WGS 84 polygons across published archaeological zones (Layer 1), 10 m modern built-up footprints (Layer 2), concealed overlap zones with propagated uncertainty bounds (Layer 3), and 28 scored geophysical open parcels and municipal rescue corridors (Layer 4).
2. **Audited coordinate corrections and scale checks** for two living-town sites:
   - **Lakhanjo-Daro Mound D / Trench C**: registered from Biagi and Vidale (2022, Fig. 3) to `27.724792°N, 68.848272°E` (2.00 m RMSE), documenting a 455 m north offset in the published caption (`27°43'44"N, 68°50'55"E`) and a 2.55× scale-bar error on Figure 3.
   - **Rupnagar (Ropar) Nalagarh Kothi metric datum**: located at `30.971621°N, 76.523804°E` (UTM 43N `645522.77 E, 3427452.78 N`), projecting all 21 trenches published in *Indian Archaeology 2011–2012 – A Review* (pp. 72–76) and documenting the 1.06 km southeast offset of the report's printed coordinate (`30.9664°N, 76.5331°E`).
3. **No inscribed objects, faces, museum accessions or newly measured radiocarbon dates** are added by this study.

## Newly acquired local-only inputs

All newly downloaded rasters, imagery mosaics and OpenStreetMap extracts live under logical path `data/raw/2026-11-23-living-towns-footprints/` (physical storage path `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\`), tracked locally in `data/raw/2026-11-23-living-towns-footprints/acquisition-manifest.json` and kept out of Git per `knowledge/provenance/REDISTRIBUTION.md`.

| Logical path | Physical path | Product and licence | Bytes | SHA-256 |
|---|---|---|---|---|
| `data/raw/2026-11-23-living-towns-footprints/worldcover/ESA_WorldCover_2021_lakhanjo_daro_N27E066.tif` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\worldcover\ESA_WorldCover_2021_lakhanjo_daro_N27E066.tif` | ESA WorldCover 10 m 2021 v200 (`N27E066` clip), CC BY 4.0 | 31,434 | `dbabc4d0168cdb1fdc740911852ea5f49f05fa6137b0833fc8c95840e01608a7` |
| `data/raw/2026-11-23-living-towns-footprints/worldcover/ESA_WorldCover_2021_rupnagar_N30E075.tif` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\worldcover\ESA_WorldCover_2021_rupnagar_N30E075.tif` | ESA WorldCover 10 m 2021 v200 (`N30E075` clip), CC BY 4.0 | 34,474 | `fd745fdeed0e0afed677c86b04b845114b333bf74caf16f98289f211927cdd8f` |
| `data/raw/2026-11-23-living-towns-footprints/mosaics/lakhanjo_daro_z17_x90598-90606_y55019-55026.png` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\mosaics\lakhanjo_daro_z17_x90598-90606_y55019-55026.png` | Esri World Imagery z17 mosaic (local visual reference only) | 9,950,388 | `31a0f13508b18bd4c709bb12613afdda3f52e8c7350d5c9cd285dd19cb7a3d26` |
| `data/raw/2026-11-23-living-towns-footprints/mosaics/lakhanjo_daro_z18_x181199-181210_y110040-110050.png` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\mosaics\lakhanjo_daro_z18_x181199-181210_y110040-110050.png` | Esri World Imagery z18 mosaic (local visual reference only) | 17,134,953 | `1a96a67f2ceb6a091ce20f15ac5aec061a25eacc2ed243fcbc5ecad8edaa947c` |
| `data/raw/2026-11-23-living-towns-footprints/mosaics/rupnagar_z17_x93396-93404_y53665-53672.png` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\mosaics\rupnagar_z17_x93396-93404_y53665-53672.png` | Esri World Imagery z17 mosaic (local visual reference only) | 8,477,172 | `12d46b30180dfa02d1590967dc05384f198c79328f983b4122086c407f350323` |
| `data/raw/2026-11-23-living-towns-footprints/mosaics/rupnagar_z18_x186796-186805_y107332-107342.png` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\mosaics\rupnagar_z18_x186796-186805_y107332-107342.png` | Esri World Imagery z18 mosaic (local visual reference only) | 11,155,656 | `ef710f93c0ab4b09e2343d026c62eea1aeda7ba0cafd576fec585a78d0889720` |
| `data/raw/2026-11-23-living-towns-footprints/mosaics/rupnagar_mound_z18_x186791-186800_y107329-107338.png` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\mosaics\rupnagar_mound_z18_x186791-186800_y107329-107338.png` | Esri World Imagery z18 mound-centred mosaic (local visual reference only) | 11,081,420 | `8583e82d433b8410be26f29585c0e1aa50b1abcf6f77749690e8f0496042eeda` |
| `data/raw/2026-11-23-living-towns-footprints/osm/osm_harappa.json` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\osm\osm_harappa.json` | OpenStreetMap Overpass extract (725 elements), ODbL 1.0 | 82,619 | `c2e13dfca27cc6d4d608c314821d3339bdb21c749a8a6926b380155eeb8c9fbe` |
| `data/raw/2026-11-23-living-towns-footprints/osm/osm_lakhanjo_daro.json` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\osm\osm_lakhanjo_daro.json` | OpenStreetMap Overpass extract (1,368 elements), ODbL 1.0 | 157,930 | `bc27d72303277139937a616a6bd750058e43cb28c0d54be8d169069f2168ff9d` |
| `data/raw/2026-11-23-living-towns-footprints/osm/osm_rupnagar.json` | `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\osm\osm_rupnagar.json` | OpenStreetMap Overpass extract (2,431 elements), ODbL 1.0 | 283,682 | `7458dee5f87e5503e6c0dcf17b8d3f3cfceb42af53c7f59d928b28ef36665beb` |

Full byte counts and SHA-256 checksums for all 19 held and newly acquired inputs are verified automatically by `code/verify.py` and logged in [summary-v1.json](summary-v1.json).

## Held local inputs reused without duplication

- Copernicus GLO-30 30 m DEM tiles (`N30_00_E072_00`, `N27_00_E068_00`, `N30_00_E076_00`) already held under `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/` and `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/`.
- ESA WorldCover 2021 v200 Harappa tile clip (`data/raw/2026-10-12-satellite-prospection/SPATIAL_CONTROL_20261012T053309958546Z_B02_WorldCover_N30E072.tif`).
- Harappa Esri World Imagery z16 and z18 mosaics and audited Wheeler (1947, Plate XV) control-point sets (`experiments/2026-10-21-plan-registration/control-R1/` and `control-R2/`).
- Primary archaeological publications already held locally: Kenoyer (1991, 2008), Biagi and Vidale (2022), Directorate of Antiquities Sindh (2022), Shar and Shah (2022) and *Indian Archaeology 2011–2012 – A Review*.
