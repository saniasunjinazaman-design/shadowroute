import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from detector.detector import selected_path

class DetectorTests(unittest.TestCase):
    def test_normal_route(self):
        text = "Table master4:\n10.150.0.0/24 unicast [u_as3 20:23:02.642] * (100) [AS150i]\n BGP.as_path: 3 2 150\n"
        self.assertEqual(selected_path(text, "10.150.0.0/24"), [3, 2, 150])
    def test_hijack_route(self):
        text = "Table master4:\n10.150.0.0/24 unicast [u_as3 20:23:02.642] * (100) [AS151i]\n BGP.as_path: 3 151\n"
        self.assertEqual(selected_path(text, "10.150.0.0/24"), [3, 151])
    def test_missing_prefix(self):
        self.assertIsNone(selected_path("Table master4:\n", "10.150.0.0/24"))
    def test_no_selected_route(self):
        text = "Table master4:\n10.150.0.0/24 unicast [u_as3 20:23:02.642] (100) [AS150i]\n BGP.as_path: 3 2 150\n"
        with self.assertRaises(ValueError): selected_path(text, "10.150.0.0/24")
    def test_malformed_path(self):
        text = "Table master4:\n10.150.0.0/24 unicast [u_as3 20:23:02.642] * (100) [AS150i]\n BGP.as_path: 3 {151}\n"
        with self.assertRaises(ValueError): selected_path(text, "10.150.0.0/24")
    def test_missing_table(self):
        with self.assertRaises(ValueError): selected_path("", "10.150.0.0/24")

if __name__ == "__main__":
    unittest.main(verbosity=2)
