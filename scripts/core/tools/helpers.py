from core.tools.adss.ads import Ads
from core.tools.afina.afina import Afina
from utils import INSTRUCTIONS


def choose_browser(*args, **kwargs):
    if INSTRUCTIONS["afina_api_key"] and INSTRUCTIONS["afina_api_key"] != "":
        return Afina(*args, **kwargs)
    else:
        return Ads(*args, **kwargs)
