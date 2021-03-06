# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Clipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest

from tempfile import mktemp
from qgis.core import QgsVectorLayer, QgsRasterLayer
from PyQt4.QtCore import QFileInfo
from osgeo import gdal

from safe.test.utilities import (
    get_qgis_app,
    standard_data_path)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.datastore.geopackage import GeoPackage


class TestGeoPackage(unittest.TestCase):
    """Test the GeoPackage datastore."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(
        int(gdal.VersionInfo('VERSION_NUM')) < 2000000,
        'GDAL 2.0 is required for geopackage.')
    def test_create_geopackage(self):
        """Test if we can store geopackage."""

        # Create a geopackage from an empty file.
        path = QFileInfo(mktemp() + '.gpkg')
        self.assertFalse(path.exists())
        data_store = GeoPackage(path)
        path.refresh()
        self.assertTrue(path.exists())

        # Let's add a vector layer.
        layer_name = 'flood_test'
        layer = standard_data_path('hazard', 'flood_multipart_polygons.shp')
        vector_layer = QgsVectorLayer(layer, 'Flood', 'ogr')
        result = data_store.add_layer(vector_layer, layer_name)
        self.assertTrue(result[0])

        # We should have one layer.
        layers = data_store.layers()
        self.assertEqual(len(layers), 1)
        self.assertIn(layer_name, layers)

        # Add the same layer with another name.
        layer_name = 'another_vector_flood'
        result = data_store.add_layer(vector_layer, layer_name)
        self.assertTrue(result[0])

        # We should have two layers.
        layers = data_store.layers()
        self.assertEqual(len(layers), 2)
        self.assertIn(layer_name, layers)

        # Test the URI of the new layer.
        expected = path.absoluteFilePath() + '|layername=' + layer_name
        self.assertEqual(data_store.layer_uri(layer_name), expected)

        # Test a fake layer.
        self.assertIsNone(data_store.layer_uri('fake_layer'))

        # Test to add a raster
        layer_name = 'raster_flood'
        layer = standard_data_path('hazard', 'classified_hazard.tif')
        raster_layer = QgsRasterLayer(layer, layer_name)

        result = data_store.add_layer(raster_layer, layer_name)
        self.assertTrue(result[0])

        # We should have 3 layers inside.
        layers = data_store.layers()
        self.assertEqual(len(layers), 3)

        # Check the URI for the raster layer.
        expected = 'GPKG:' + path.absoluteFilePath() + ':' + layer_name
        self.assertEqual(data_store.layer_uri(layer_name), expected)

        # Add a second raster.
        layer_name = 'big raster flood'
        self.assertTrue(data_store.add_layer(raster_layer, layer_name))
        self.assertEqual(len(data_store.layers()), 4)

    @unittest.skipIf(
        int(gdal.VersionInfo('VERSION_NUM')) < 2000000,
        'GDAL 2.0 is required for geopackage.')
    def test_read_existing_geopackage(self):
        """Test we can read an existing geopackage."""
        geopackage = QFileInfo(standard_data_path('other', 'jakarta.gpkg'))
        data_store = GeoPackage(geopackage)

        # We should have 3 layers in this geopackage.
        self.assertEqual(len(data_store.layers()), 3)

        # Test we can load a vector layer.
        roads = QgsVectorLayer(
            data_store.layer_uri('roads'),
            'Test',
            'ogr'
        )
        self.assertTrue(roads.isValid())

        # Test we can load a raster layer.
        flood = QgsRasterLayer(
            data_store.layer_uri('flood'),
            'flood'
        )
        self.assertTrue(flood.isValid())


if __name__ == '__main__':
    unittest.main()
