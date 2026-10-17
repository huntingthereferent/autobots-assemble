"""Source validation and nonfabrication tests for Internet world map."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET
from views.traces.internet_map import (
 read_geojson,read_probes,read_traffic,render_map,validate_snapshot,write,polygon_paths)

def geometry():
    return {"type":"FeatureCollection","features":[
        {"type":"Feature","properties":{"ISO_A2_EH":chr(65+i//26)+chr(65+i%26)},
          "geometry":{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,0]]]}}
        for i in range(110)]}

def snapshot(traffic=None,probes=None):
    return {"schema":"internet-observations-map/v1",
            "checked_at":"2026-10-17T20:00:00+00:00",
            "traffic":traffic,
            "traffic_state":"SOURCE_MEASURED" if traffic else "TOKEN_NOT_CONFIGURED",
            "probe_state":"PUBLIC_SAMPLE" if probes else "SOURCE_UNAVAILABLE",
            "probes":probes}

def cf_data():
    return {"success":True,"result":{
      "top_0":[{"clientCountryAlpha2":"US","clientCountryName":"United States","value":"18.5"},
               {"clientCountryAlpha2":"DE","clientCountryName":"Germany","value":"4.2"}],
      "meta":{"normalization":"PERCENTAGE",
              "dateRange":[{"startTime":"2026-10-16T20:00:00Z","endTime":"2026-10-17T20:00:00Z"}],
              "lastUpdated":"2026-10-17T20:00:00Z"}}}

class MapTests(unittest.TestCase):
    def test_world_geometry_contract(self):
        geo=read_geojson(geometry())
        self.assertEqual(len(geo),110)
        self.assertIn(" L",polygon_paths(geo,None))
        with self.assertRaises(ValueError):read_geojson({"features":[]})

    def test_probe_is_not_traffic(self):
        v=read_probes({"results":[
            {"is_public":True,"status":{"id":1},"geometry":{"coordinates":[10.,20.]}},
            {"is_public":False,"status":{"id":1},"geometry":{"coordinates":[30.,40.]}},
            {"is_public":True,"status":{"id":2},"geometry":{"coordinates":[50.,60.]}}]})
        self.assertEqual(v["points"],[[10.,20.]])
        s=snapshot(probes=v)
        out=render_map(read_geojson(geometry()),s)
        self.assertIn("NO SOURCE DATA",out)
        self.assertIn("1 connected public probes",out)
        self.assertIn("not representative",out)

    def test_cloudflare_share_is_not_global_traffic(self):
        t=read_traffic(cf_data())
        self.assertEqual(t["values"][0]["percent"],18.5)
        self.assertIn("not global packet count",t["measurement_kind"])
        image=render_map(read_geojson(geometry()),snapshot(traffic=t))
        self.assertIn("Cloudflare sampled HTTP request share",image)
        self.assertNotIn("NO SOURCE DATA",image)
        ET.fromstring(image)

    def test_tokenless_never_claims_measured_traffic(self):
        bad=snapshot()
        bad["traffic_state"]="SOURCE_MEASURED"
        with self.assertRaises(ValueError):validate_snapshot(bad)
        bad=snapshot(read_traffic(cf_data()))
        bad["traffic_state"]="TOKEN_NOT_CONFIGURED"
        with self.assertRaises(ValueError):validate_snapshot(bad)

    def test_reject_bad_values_and_duplicate_countries(self):
        bad=cf_data()
        bad["result"]["meta"]["normalization"]="MIN_MAX"
        with self.assertRaises(ValueError):read_traffic(bad)
        bad=cf_data()
        bad["result"]["top_0"].append(bad["result"]["top_0"][0])
        with self.assertRaises(ValueError):read_traffic(bad)
        bad=cf_data()
        bad["result"]["top_0"][0]["value"]="-3"
        with self.assertRaises(ValueError):read_traffic(bad)

    def test_only_source_data_published(self):
        with TemporaryDirectory() as d:
            data=snapshot()
            svg=render_map(read_geojson(geometry()),data)
            write(data,svg,Path(d))
            self.assertTrue((Path(d)/"internet-map.svg").is_file())
            self.assertTrue((Path(d)/"internet-map.json").is_file())
            self.assertNotIn("Bearer",(Path(d)/"internet-map.json").read_text())

if __name__=="__main__":unittest.main()
