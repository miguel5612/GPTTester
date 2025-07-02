from . import clients, digital_assets, projects

all_routers = [
    clients.router,
    digital_assets.router,
    projects.router,
]

# Backwards compatibility: some modules import `routers`
# so expose it as an alias to `all_routers`.
routers = all_routers
