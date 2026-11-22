# Data update: Copernicus DEM GLO-30 tiles and prospection pilot frames

Recorded on 22 November 2026 for maintainer integration into `knowledge/DATA.md` and `data/MANIFEST.json`. This package adds 10 full 1-degree Copernicus DEM GLO-30 GeoTIFF tiles to local bulk storage on D: (421,453,464 bytes total), reuses 6 already-held full 30 m tiles without duplication, and produces tracked sampling frames and blind field packets for regions P01 to P09. No inscribed-object counts or object metadata columns change.

## 1. Storage and licensing

All newly acquired raw GeoTIFF tiles live in local-only bulk storage under the `data/raw` directory junction:

- Logical repository path: `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/`
- Physical workstation path: `D:\projects\indus_valley_script\data\raw\2026-11-22-geospatial-prospection-pilot\dem\30m\`
- Local acquisition manifest: `data/raw/2026-11-22-geospatial-prospection-pilot/dem/acquisition_manifest.json` (mirrored in tracked `outputs/dem_manifest.json`)
- Source endpoint: AWS Open Data public Copernicus DEM GLO-30 bucket (`https://copernicus-dem-30m.s3.amazonaws.com/`)
- License notice: Copernicus DEM licence. (c) DLR e.V. 2010–2014 and (c) Airbus Defence and Space GmbH 2014–2018 provided under COPERNICUS by the European Union and ESA. Raw tiles remain local-only and untracked in Git.

## 2. Complete 16-tile Copernicus GLO-30 inventory (P01 to P09)

Every tile is a 3600 by 3600 pixel 32-bit floating-point WGS84 GeoTIFF at 1 arcsecond (0.0002778 degree) pixel spacing.

| Tile | Regions covered | Status | Bytes | SHA-256 (first 16 hex) | Logical path |
|---|---|---|---:|---|---|
| `N27_00_E070_00` | P01 | New local download | 45,020,472 | `e94448c064139ba3` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N27_00_E070_00_DEM.tif` |
| `N27_00_E071_00` | P01 | New local download | 43,636,362 | `749396b83f4315ca` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N27_00_E071_00_DEM.tif` |
| `N28_00_E070_00` | P01, P02 | New local download | 43,189,207 | `488b8f785306bd92` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N28_00_E070_00_DEM.tif` |
| `N28_00_E071_00` | P01, P02 | New local download | 44,672,367 | `2c5c777e7aac8421` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N28_00_E071_00_DEM.tif` |
| `N29_00_E071_00` | P01, P08, P09 | New local download | 42,497,940 | `faaf8dfbaf64e18f` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N29_00_E071_00_DEM.tif` |
| `N29_00_E072_00` | P08, P09 | New local download | 40,687,321 | `0116c3b57bebff0d` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N29_00_E072_00_DEM.tif` |
| `N29_00_E073_00` | P06 and P08 buffer | Reused local tile | 40,659,147 | `3e4fec34b44d0a2e` | `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N29_00_E073_00_DEM.tif` |
| `N29_00_E074_00` | P05, P06 | Reused local tile | 40,682,886 | `fac1ec35c82e39cf` | `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N29_00_E074_00_DEM.tif` |
| `N29_00_E075_00` | P03, P04, P05, P06, P07 | Reused local tile | 40,011,539 | `fa8732319f44596e` | `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N29_00_E075_00_DEM.tif` |
| `N29_00_E076_00` | P03, P04, P07 | Reused local tile | 39,668,602 | `f9516646de89f5c3` | `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N29_00_E076_00_DEM.tif` |
| `N30_00_E071_00` | P08, P09 | New local download | 42,159,209 | `b00b507dbd566608` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N30_00_E071_00_DEM.tif` |
| `N30_00_E072_00` | P08, P09 | Reused local tile | 40,085,904 | `269a9377da5f6394` | `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N30_00_E072_00_DEM.tif` |
| `N30_00_E073_00` | P08 buffer | Reused local tile | 39,852,816 | `5c33f26f290f9005` | `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N30_00_E073_00_DEM.tif` |
| `N30_00_E074_00` | P05 | New local download | 40,005,278 | `199abc82d71bbeba` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N30_00_E074_00_DEM.tif` |
| `N30_00_E075_00` | P04, P05 | New local download | 39,835,212 | `4ca389a4af29554e` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N30_00_E075_00_DEM.tif` |
| `N30_00_E076_00` | P04 | New local download | 39,750,096 | `1f682577320595c6` | `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N30_00_E076_00_DEM.tif` |

Full 64-character SHA-256 hashes, exact AWS S3 URLs, HTTP status codes and retrieval timestamps are recorded in `outputs/dem_manifest.json` and in per-tile `.source.json` sidecars inside the D: storage folder.

## 3. Additional reused local datasets

We also read three existing local datasets without altering them:

- `data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_ORENGO_SOURCE_AOI.geojson` (Orengo et al. 2020 Cholistan classifier footprint polygon).
- `data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_SINGH_CORES_DERIVED.json` (UTM Zone 43N coordinates for Singh et al. 2017 sediment cores `GS-7`, `GS-10`, `GS-11`, `GS-13`, `GS-14`, `SRH-5`, `KNL-1` and `MNK-6`).
- `data/raw/2026-10-12-satellite-prospection/SPATIAL_CONTROL_20261012T053309958546Z_B0{1,2,4}_derived.npz` and `processed-v1/B0{1,2,4}.npz` (ESA WorldCover 2021 v200 land-cover fractions and Sentinel-2 L2A NDVI composites for blocks B01, B02 and B04).

## 4. Regional coverage gain and remaining gaps

Prior to this package, full 30 m Copernicus DEM tiles covered P06 and the southern halves of P03, P04, P05 and P08, while Cholistan (P01 and P02), the western half of P08 and P09, and the northern halves of P04 and P05 had only 90 m coverage or narrow cropped windows. The 10 new tiles complete continuous 30 m terrain coverage across all nine northern settlement-prospection regions (P01 to P09).

Three key geospatial data gaps remain open for future passes:
1. Full ESA WorldCover 2021 v200 built-up masks outside blocks B01, B02 and B04 (specifically across all of P03, P04 and P05, where modern villages drive most 30 m DEM rises).
2. Digitized Survey of India historical map mound footprints (Green et al. 2019; Garcia-Molsosa et al. 2023) and the 337-row Orengo et al. (2020) Cholistan cluster point table, neither of which is publicly downloadable in raw vector form.
3. MAHSA database concordance records and local field-access parcel polygons needed to upgrade regions from feasibility level F0 to F1 or F2.
