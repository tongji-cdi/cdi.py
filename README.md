# cdi.py
Python API to control the smart space equipments at CDI.

## Installation
```
pip install git+https://github.com/tongji-cdi/cdi.py.git
```

## Usage
```python
from cdipy import CDI

# Login as a user with priviledge
cdi = CDI('API_ADDRESS', 'USERNAME', 'PASSWORD')

# cdi.spaces contains all available spaces at the lab.
for space in cdi.spaces:
  print(space.name)

# Set light level
cdi.spaces_by_name['SPACE_NAME'].set_lights(100, selection='all')

# Open door
cdi.spaces_by_name['SPACE_NAME'].open_door()

# Set AC temperature
cdi.spaces_by_name['SPACE_NAME'].set_temperature(26)
```
