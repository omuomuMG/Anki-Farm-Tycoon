import struct
import unittest
from pathlib import Path

from tests._bootstrap import ROOT, import_target


resource_module = import_target("utils.resource_manager")


class ResourceTests(unittest.TestCase):
    def test_new_animal_sprites_are_rgba_1024_pngs(self):
        for filename in ("child_sheep.png", "sheep.png", "unicorn.png"):
            with self.subTest(filename=filename):
                path = ROOT / "Resources" / filename
                data = path.read_bytes()[:33]
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(data[12:16], b"IHDR")
                width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
                self.assertEqual((width, height), (1024, 1024))
                self.assertEqual(bit_depth, 8)
                self.assertEqual(color_type, 6, "PNG must contain an alpha channel")

    def test_unicorn_sprite_is_used_when_child_sprite_is_missing(self):
        pixmap = resource_module.ResourceManager._load_pixmap_candidates(
            ("child_unicorn.png", "unicorn.png"),
            "🦄",
        )
        self.assertEqual(Path(pixmap.path).name, "unicorn.png")


if __name__ == "__main__":
    unittest.main()
