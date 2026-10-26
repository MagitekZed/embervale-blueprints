"""Shared palette for the English manor drafts (house detail plan + estate site plan).

Swaps mage_common's palette for this one, so import it before drawing.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, FLOORS, ROOF_MATS

MANOR = {
    # walls (real blocks from the planner's block catalogue)
    'A': {'name': 'Refined Sandstone Block', 'kind': 'wall', 'color': '#ada198'},          # the house: Bath-stone look
    'S': {'name': 'Limestone Block', 'kind': 'wall', 'color': '#a79a88'},                  # plinth, terrace walls
    'P': {'name': 'Highly Polished Stone Block', 'kind': 'wall', 'color': '#b3b0a9'},      # columns, piers
    'K': {'name': 'Fired Bricks Block', 'kind': 'wall', 'color': '#aa7657'},               # service wing, garden walls
    'R': {'name': 'Refined Stone Block', 'kind': 'wall', 'color': '#84837e'},              # cellars, tunnels
    'L': {'name': 'Shell Limestone Block', 'kind': 'wall', 'color': '#8c7958'},            # grotto shellwork
    'b': {'name': 'Highly Polished Stone Block (balustrade)', 'kind': 'block', 'color': '#b3b0a9', 'height': 1},
    'c': {'name': 'Limestone Block (coping)', 'kind': 'block', 'color': '#a79a88', 'height': 0.5},
    'w': {'name': 'Refined Wood Block (railing)', 'kind': 'block', 'color': '#75675f', 'height': 1},
    'H': {'name': 'Foliage (yew hedge)', 'kind': 'block', 'color': '#4f7a26', 'height': 2.5},
    'h': {'name': 'Foliage (box hedge)', 'kind': 'block', 'color': '#668f27', 'height': 0.5},
    'e': {'name': 'White Luminescent Block (stalactite)', 'kind': 'block', 'color': '#d1cac6', 'height': 1, 'base': 2.5},
    # floors
    '.': {'name': 'Refined Wood Block', 'kind': 'floor', 'color': '#75675f'},
    ',': {'name': 'Highly Polished Stone Block', 'kind': 'floor', 'color': '#b3b0a9'},      # marble halls
    'r': {'name': 'Red Carpet Block', 'kind': 'floor', 'color': '#9e3742'},
    'm': {'name': 'Limestone Block', 'kind': 'floor', 'color': '#a79a88'},                  # terrace paving
    ':': {'name': 'Limestone Road Block', 'kind': 'floor', 'color': '#a38b79'},             # gravel walks
    ';': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},                     # service floors, tunnels
    'z': {'name': 'Smooth Stone Road Block', 'kind': 'floor', 'color': '#746553'},          # stable yard
    'l': {'name': 'Fertile Springlands Dirt', 'kind': 'floor', 'color': '#95b261'},         # lawn
    'f': {'name': 'Flower Soil', 'kind': 'floor', 'color': '#a77e63'},
    'g': {'name': 'Farm Soil', 'kind': 'floor', 'color': '#90450d'},
    '~': {'name': 'Water', 'kind': 'water', 'color': '#3f8fc1'},
    # not blocks: furniture placeholders, doors, windows, secret doors
    'Y': {'name': 'Bookshelf wall (3 m)', 'kind': 'wall', 'color': '#7a5236', 'height': 3},
    'y': {'name': 'Bookshelf (2 m)', 'kind': 'block', 'color': '#8a6040', 'height': 2},
    'v': {'name': 'Wine rack (2 m)', 'kind': 'block', 'color': '#6b4a32', 'height': 2},
    'D': {'name': 'Door', 'kind': 'door', 'color': '#6b4a2e'},
    'G': {'name': 'Great door', 'kind': 'door', 'color': '#4d3a2a'},
    'o': {'name': 'Sash window', 'kind': 'window', 'color': '#8fc3df'},
    'q': {'name': 'Glass wall', 'kind': 'window', 'color': '#a9d8e6'},
    'X': {'name': 'Secret door (bookcase)', 'kind': 'door', 'color': '#7a5236'},
    'x': {'name': 'Secret door (wall panel)', 'kind': 'door', 'color': '#ada198'},
    'Q': {'name': 'Secret door (wine rack)', 'kind': 'door', 'color': '#6b4a32'},
    'Z': {'name': 'Secret door (rock face)', 'kind': 'door', 'color': '#7d776a'},
    'I': {'name': 'Iron door (strong room)', 'kind': 'door', 'color': '#6f7377'},
    '_': {'name': 'Dug out (open)', 'kind': 'dig', 'color': '#3d332a'},
}
PALETTE.clear()
PALETTE.update(MANOR)
ROOF_MATS['slate'] = ('Tarred Shingle Roof Block', '#6b6b66')
ROOF_MATS['slatecap'] = ('Granite Shingle Roof Block', '#626454')
ROOF_MATS['copper'] = ('Castle Roof Block', '#8b9987')            # weathered copper green
ROOF_MATS['stone'] = ('Highly Polished Stone Block', '#b3b0a9')    # pediments and temple domes
