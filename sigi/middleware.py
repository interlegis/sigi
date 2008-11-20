try:
    # try use maintenancemode middleware from django-maintenancemode project
    import maintenancemode.middleware
    class MaintenanceModeMiddleware(maintenancemode.middleware.MaintenanceModeMiddleware):
        pass
except ImportError:
    # otherwise, a thin wrapper for middleware
    class MaintenanceModeMiddleware(object):
        pass
