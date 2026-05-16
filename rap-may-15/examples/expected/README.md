# Expected outputs

This folder holds no binaries. The actual JPG, SVG, and STL are produced on demand by the commands in `../README.md`, and that requires a macOS install with the Output package and Rhino. The notes below describe what each output should look like so a reviewer can cross-check their own run.

## case-study-plan.jpg (PIAF raster)

- Format: JPG, RGB, ~300 DPI.
- Page size: the default PIAF paper, 24 by 36 inches per `print.paper_width_in` and `print.paper_height_in` in the state. At 300 DPI that is roughly 7200 by 10800 pixels.
- Approximate file size: 200 to 800 KB depending on the amount of black hatch on the page.
- Content: the 80 by 60 foot site as the outer rectangle, the 48 by 24 foot footprint inside it, twelve column dots in a 4 by 3 grid, the perimeter wall outline broken by six apertures (two south windows, one north door, one north window, one east window, one west window), and two zone outlines for living (east) and service (west). Legend in the bottom-right corner.

## case-study-plan.svg (vector)

- Format: SVG, stdlib-generated, single root element, no embedded raster.
- ViewBox: sized to the site (80 by 60 units, the controller's foot units).
- Approximate file size: under 50 KB.
- Content: same geometry as the JPG. Expect a `<polygon>` for the site, a `<polygon>` for each zone, a `<line>` for each wall segment, and a `<circle>` for each column dot. Should open in any browser.

## case-study-model.stl

- Format: binary STL of the extruded walls plus slab plus columns.
- Approximate triangle count: 5,000 to 20,000 triangles depending on tactile3d resolution and aperture curve segmentation.
- Approximate file size: 250 KB to 1 MB.
- Bounding box: 48 by 24 feet in plan, 10 feet tall (`wall_height`), clipped at 4 feet (`cut_height`) on the upper face. Floor slab adds 0.5 feet (`floor_thickness`) below the walls when `floor_enabled` is true.
