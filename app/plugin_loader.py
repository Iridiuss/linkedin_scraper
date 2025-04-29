import importlib.util, pkgutil, pathlib
from typing import List, Type
import logging

# Use absolute path in Docker container
PLUGIN_PATH = pathlib.Path("/code/lead_plugins")

class BasePlugin:
    name: str  # unique slug

    def fetch(self) -> List[dict]:
        """Return a list of raw lead dicts matching DB columns."""
        raise NotImplementedError


registry: List[BasePlugin] = []

def autodiscover():
    registry.clear()
    logging.info(f"Looking for plugins in: {PLUGIN_PATH}")
    
    if not PLUGIN_PATH.exists():
        logging.error(f"Plugin directory does not exist: {PLUGIN_PATH}")
        return registry
        
    for finder, name, ispkg in pkgutil.iter_modules([str(PLUGIN_PATH)]):
        logging.info(f"Found potential plugin: {name}")
        full_path = PLUGIN_PATH / name / "plugin.py"
        
        if not full_path.exists():
            logging.warning(f"Plugin file not found: {full_path}")
            continue
            
        logging.info(f"Loading plugin: {name}")
        try:
            spec = importlib.util.spec_from_file_location(name, full_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            plugin_cls = getattr(mod, "Plugin", None)
            
            if plugin_cls is None:
                logging.warning(f"No Plugin class found in {name}")
                continue
                
            instance = plugin_cls()
            registry.append(instance)
            logging.info(f"Successfully loaded plugin: {name}")
        except Exception as e:
            logging.error(f"Error loading plugin {name}: {str(e)}")
            
    logging.info(f"Loaded plugins: {[p.name for p in registry]}")
    return registry 