from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
# from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
from .blender_krita_link import BlenderKritaLink, BlenderKritaLinkExtension


DOCKER_ID = "template_docker"
instance = Krita.instance()

extension = BlenderKritaLinkExtension(parent = instance)
instance.addExtension(extension)

dock_widget_factory = DockWidgetFactory(
    DOCKER_ID, DockWidgetFactoryBase.DockRight, BlenderKritaLink
)

instance.addDockWidgetFactory(dock_widget_factory)