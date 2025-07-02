from . import clients, digital_assets, projects

all_routers = [
    clients.router,
    digital_assets.router,
    projects.router,
]

# Placeholder for dynamically added routers. main.py imports this name
# expecting a list, so provide an empty one by default.
routers: list = []
