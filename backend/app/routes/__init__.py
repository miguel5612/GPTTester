from . import clients, digital_assets, projects

all_routers = [
    clients.router,
    digital_assets.router,
    projects.router,
]

# Backwards compatibility: older modules expect a variable named ``routers``.
routers = all_routers
