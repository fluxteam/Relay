from typing import Dict, Tuple
import rtoml
import importlib
from pathlib import Path
from relay.classes import Events
from relay.listeners import Event
from relay.enums import DiscordLanguage
from relay.utils import extract_blockly, extract_model, generate_model_tree, lower


def _read_files() -> Tuple[Dict, Dict]:
    # Read blocks.yml and config.toml from relay/blockly folder.
    p = Path().resolve() / "relay" / "blockly"
    if not p.exists():
        raise FileNotFoundError("Blockly path doesn't exists.")
    # Load standard blocks and blockly configuration.
    s1 = rtoml.load((p / "blocks.toml"))
    s2 = rtoml.load((p / "config.toml"))
    return s1, s2, 


def _parse_element(text : str) -> Dict:
    """
    Creates a Blockly flyout item from a string.
    """
    # Separator
    if text == "separator":
        return { "kind": "sep", "gap": "60" }
    # Label
    elif text.startswith("label:"):
        lbl = text.removeprefix("label:")
        return { "kind": "label", "text": "%{BKY_TOOLBOX_LABEL_" + lbl + "}"}
    # Button
    elif text.startswith("button:"):
        btn = text.removeprefix("button:")
        return { "kind": "button", "text": "%{BKY_TOOLBOX_BUTTON_" + btn + "}", "callbackKey": btn }
    # Block
    elif text.startswith("block:"):
        return { "kind": "block", "type": text.removeprefix("block:") }
    raise ValueError(f"Unknown element: {text}")


def extract():
    """
    Parse blockly configuration.
    """
    blocks, config = _read_files()
    # 1. Load classes by name and store them in list.
    models = importlib.import_module(config["models"]["module"])
    mc = [getattr(models, x) for x in config["models"]["creatable"]]
    mr = [getattr(models, x) for x in config["models"]["readable"]]
    mc.reverse()
    mr.reverse()
    # 2. Load categories.
    result = {"icons": {}, "colors": {}, "sort": [], "elements": {}, "exclude": [], "styles": {}, "replace": {}}
    for category in config["categories"]:
        i = category["id"]
        if "icon" in category:
            result["icons"][i] = category["icon"]
        result["colors"][i] = category["color"]
        if "elements" in category:
            result["elements"][i] = [[x[0], *[_parse_element(y) for y in x[1:]]] for x in category["elements"]]
        if category.get("visible", True):
            result["sort"].append(i)
    # 3. Insert blocks for classes.
    result["elements"]["DISCORD"].extend([[1, *[{"kind": "block", "type": "DISCORDM_" + x.__name__.upper()} for x in mc]]])
    result["elements"]["DISCORD"].extend([[1, *[{"kind": "block", "type": "DISCORDM_MODEL_" + x.__name__.upper()} for x in mr]]])
    # 4. Add standard blocks to includes.
    for k, v in blocks.items():
        if k not in result["elements"]:
            result["elements"][k] = []
        bl = []
        for b in v:
            bl.append({ "kind": "block", "type": b["type"] })
        result["elements"][k].extend([[0, *bl]])
    # 5. Add keys.
    result["exclude"] = config["exclude"]["blocks"]
    result["styles"] = config["styles"]
    result["replace"] = config["replace_rules"]
    result["flags"] = config["flags"]
    result["settings"] = config["settings"]
    result["changelog"] = config["changelog"]
    result["sounds"] = config["sounds"]
    result["prefixes"] = config["prefixes"]
    # 6. Generate blocks for models.
    model_blocks = []
    for i in mc:
        model_blocks.append(extract_model("DISCORDM_" + i.__name__.upper(), i))
    for j in mr:
        model_blocks.append(extract_model("DISCORDM_MODEL_" + j.__name__.upper(), j, creatable = False))
    return blocks, model_blocks, result


def load():
    # Extract Blockly data.
    standard_blocks, model_blocks, data = extract()
    theme, categories, block_names, blocks = extract_blockly(
        exclude = data["exclude"], 
        sort = data["sort"], 
        colors = data["colors"], 
        styles = data["styles"],
        replace = data["replace"],
        elements = data["elements"]
    )
    blocks["DISCORD"].extend(model_blocks)
    extra_state = {
        "EVENTS": {},
        "FLAGS": data["flags"],
        "SETTINGS": data["settings"],
        "CHANGELOG": data["changelog"],
        "SOUNDS": data["sounds"],
        "PREFIXES": data["prefixes"]
    }
    for k, v in standard_blocks.items():
        if k not in blocks:
            blocks[k] = []
        for item in v:
            blocks[k].insert(0, item)
            # Inject available events to dropdown.
            # TODO: Cleanup
            if item["type"] == "WORKFLOW_EVENT_LISTENER":
                for event, lstnr in Event.__events__.values():
                    if (not event.is_remote()) or (event in [Events.INTERACTION_CREATE, Events.WEBHOOK]):
                        # These keys are not exposed to user because they 
                        # won't need them, so we hide them in tree too.
                        exclude = ["token", "version", "guild_id", "application_id", "action_id"]
                        tree = generate_model_tree(lstnr, exclude, level_sep = " › ")
                        extra_state["EVENTS"][event.value] = [
                            [
                                " › ".join([
                                    "%{BKY_VALUE_" + y.strip().upper().replace("*", "") + "}" + \
                                    ("*" if "*" in y else "") for y in x.split("›")
                                ]), 
                                x.replace("*", "").replace(" ", "").replace("›", ".")
                            ] for x in tree
                        ]
            elif item["type"] == "WORKFLOW_COMMAND_TRANSLATION":
                blocks[k][0]["args0"][3]["options"].extend([
                    [
                        (f"{y.name} ({y.native})" if y.name != y.native else y.name), 
                        lower(x)
                    ] for x, y in DiscordLanguage.__members__.items()
                ])
    return theme, categories, block_names, blocks, extra_state, data["colors"], data["icons"],