from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
from .blender_krita_link import BlenderKritaLink
import asyncio


DOCKER_ID = 'template_docker'
instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        BlenderKritaLink)

instance.addDockWidgetFactory(dock_widget_factory)
