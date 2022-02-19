from krita import DockWidgetFactory, DockWidgetFactoryBase
from .procedural_generator import ProceduralGenerator

DOCKER_ID = 'procedural_generator'
instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        ProceduralGenerator)

instance.addDockWidgetFactory(dock_widget_factory)
