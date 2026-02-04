from satellite.gee_auth import ee
import geemap

def grid_stats(image, roi, scale=500):
    grid = geemap.create_grid(roi, scale)
    return image.reduceRegions(
        collection=grid,
        reducer=ee.Reducer.mean(),
        scale=scale
    )
