import logging

from oil_division.solver import search

# logging.basicConfig(level=logging.DEBUG)
achieved_development = search()
if achieved_development:
    print(achieved_development.to_detailed_str())
else:
    print("Not Found")
