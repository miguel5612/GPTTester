from . import clients, digital_assets, projects

all_routers = [
    clients.router,
    digital_assets.router,
    projects.router,
]

# Backwards compatibility for legacy imports
routers = all_routers
