__all__ = [
    "build_url",
    "parse_language_header",
    "load_json",
    "load_toml",
    "get_avatar_url",
    "get_server_icon_url",
    "get_relay_docs_url",
    "lower",
    "parse_blocks",
    "parse_blocks_all",
    "parse_custom_block"
    "convert_block_id",
    "convert_guild_locale",
    "parse_convert_slash_option_name",
    "define_listener_parser",
    "create_status_text",
    "generate_model_tree",
    "ListenerData",
    "ActionsData"
]

from binascii import crc32
import orjson
import rtoml
import httpx
import inspect
from math import isnan
from collections import namedtuple
from datetime import datetime, timezone
from inspect import isclass
from pydantic import HttpUrl, ConstrainedInt
from typing import Callable, Dict, Any, List, Literal, Optional, Tuple, Union, get_args, get_origin, TYPE_CHECKING
from pyconduit import FunctionStore, EMPTY, Variable
from pyconduit.categories.logic import LogicalOperators
from relay_packages import Parameter, ParameterType
from relay.models import Emoji, Model, ObjectOrSnowflake, Snowflake, Permissions, Color, ExtendedUrl, Components, ValidChannel, ValidMember
from hikari import Snowflake as HSnowflake
from hikari import UNDEFINED
from urllib.parse import quote
from traceback import format_exception

if TYPE_CHECKING:
    from relay.strings import StringsStore


def create_docstring(
    text : Optional[list] = None,
    headers : Optional[dict] = None, 
    admonitions : Optional[dict] = None
) -> str:
    """
    Creates docstring from parse_docstring() result.
    """
    # TODO: Complete this method.
    # Blockly splits the text to new lines at 60 characters
    # and it breaks the indent so we split to new lines
    # ourselves before Blockly does.
    LINE_LIMIT = 59
    # Blockly's tooltip removes trailing spaces,
    # so we use a blank character that acts like a "space".
    PARAM_PREFIX = chr(0x00A0) * 8
    HEADER_PREFIX = chr(0x00A0) * 4
    NW = chr(0x00A0) + "\n"
    doc = "".join(text or [])
    if admonitions:
        doc += NW + NW
    for k, v in (admonitions or {}).items():
        doc += k + NW
        for kk in v:
            doc += HEADER_PREFIX + kk + NW
    if headers:
        doc += NW + NW
    for k, v in (headers or {}).items():
        doc += k + NW
        for kk, vv in v.items():
            doc += HEADER_PREFIX + kk + NW
            for l in vv:
                n = (LINE_LIMIT - len(PARAM_PREFIX))
                doc += NW.join([PARAM_PREFIX + l[i:i+n] for i in range(0, len(l), n)])
    return doc


def parse_docstring(doc : Optional[str]) -> Dict[str, Any]:
    """
    Strip markdown docstring to use with Blockly tooltips.
    """
    if not doc:
        return {}
    admonition = None
    header = None
    subheader = None
    admonitions = {}
    headers = {}
    text = []
    for line in doc.splitlines():
        l = line.strip().removesuffix(":")
        if not l:
            admonition = None
            header = None
            subheader = None
            continue
        # Check if line is a admonition.
        if l.startswith("!!!") or l.startswith("???"):
            admonition = l.strip('!?').replace('"', "").split(" ", maxsplit = 1)[-1]
            admonitions[admonition] = []
            continue
        # Check if line is a header.
        elif l.istitle():
            header = l
            headers[l] = {}
            continue
        # Check if line is a parameter name.
        elif header and l.islower():
            subheader = l
            continue
        # If line is an admonition, add it to list.
        if admonition:
            admonitions[admonition].append(l)
        # If line is an parameter description, add it to list.
        elif header and subheader:
            if subheader not in headers[header]:
                headers[header][subheader] = []
            headers[header][subheader].append(l)
        # Else, just add it to description.
        elif (not header) and (not admonition):
            text.append(l)
    return {
        "text": text,
        "headers": headers, 
        "admonitions": admonitions
    }


def extract_blockly(
    exclude : List[str] = [], 
    sort : List[str] = [], 
    colors : Dict[str, str] = {},
    styles : Dict[str, Any] = {},
    elements : Dict[str, list] = {},
    replace : Dict[str, str] = {}
):
    """
    Get ConduitBlock parameters and create blocks in Blockly format.
    """
    # TODO: Refactor.
    blocks = {} if not sort else {x : [] for x in sort}
    block_names = []
    # Add block styles.
    theme = {
        "componentStyles": styles, "blockStyles": {
        (lower(x) + "_blocks") : {"colourPrimary": y} for x, y in colors.items()
    }}
    for block in FunctionStore.functions.values():
        if "SKIP" in block.conduit.tags:
            continue
        cat = replace.get(block.conduit._category, block.conduit._category)
        if (block.conduit.display_name in exclude) or ((cat + ".*") in exclude):
            continue
        if cat not in blocks:
            blocks[cat] = []
        # Does block returns something?
        returns = \
            UNDEFINED if block.conduit.return_type == None else \
            parse_blockly_type(block.conduit.return_type, "OUTPUT")
        # Block data in Blockly format
        block_data = define_block(
            category = block.conduit._category,
            name = block.conduit._name,
            parameters = export_block_parameters(dict(block.conduit.parameters)),
            tooltip = block.conduit.description,
            prefix = "%{BKY_BLOCK_" + block.conduit.display_name.replace(".", "_") + "}",
            check = returns if returns != UNDEFINED else "Block",
            is_statement = returns == UNDEFINED
        )
        # Append to blocks.
        blocks[cat].append(block_data)
        block_names.append(block.conduit.display_name)
    # Create toolbox for each category.
    categories = {}
    for k, v in blocks.items():
        # TODO: Remove manual check.
        if k == "STORAGE":
            continue
        # Define a category.
        categories[k] = {
            "kind": "category",
            "name": "%{BKY_CATEGORY_" + k + "}",
            "toolboxitemid": k,
            "contents": [{"kind": "block", "type": x["type"]} for x in v],
            "colour": colors.get(k, "#000000"),
            "cssConfig": {
                "container": "blocklyToolboxCategory relayCategory" + k,
                # Make icon div to include Tabler icons.
                "icon": "blocklyTreeIcon ti relayCategory" + k
            }
        }
        # Add elements.
        for l in elements.get(k, []):
            for ei, e in enumerate(l[1:]):
                categories[k]["contents"].insert(l[0] + ei, e)
                if (e["kind"] == "block"):
                    block_names.append(e["type"].replace("_", ".", 1))
    return theme, categories, block_names, blocks,


def extract_model(n : str, model : Model, creatable : bool = True) -> Dict:
    """
    Creates a new Blockly definition that has parameters of pydantic Model.

    If "creatable" is True, then the all attributes will be created as block fields,
    if False, then a block dropdown will be added with list of attributes names. 
    """
    category, name = n.split("_", 1)
    return define_block(
        category = category,
        name = name,
        parameters = \
            export_model_parameters(model) if creatable else
            export_selector_parameters(model),
        style = "discordmodels",
        prefix = "%{BKY_BLOCK_" + category + "_" + name + "}",
        check = model.__name__ if creatable else None,
        tooltip = model.__doc__
    )


BlockParameters = namedtuple(
    "BlockParameters", 
    ["display_name", "name", "type", "required"]
)

BlockDropdown = namedtuple(
    "BlockDropdown",
    ["display_name", "name", "options"]
)

BlockMessage = namedtuple(
    "BlockMessage",
    ["message", "args"]
)


def export_block_parameters(parameters : Dict[str, inspect.Parameter]) -> List[BlockParameters]:
    """
    Exports a ConduitBlock's parameters to use with creating Blockly.
    """
    params = []
    for x, y in parameters.items():
        if x.endswith("__") or x.startswith("_") or (x == "silent"):
            continue
        prm = BlockParameters(
            display_name = x if (not str(x[-1]).isnumeric()) else None,
            name = x,
            type = parse_blockly_type(y.annotation, "INPUT"),
            required = y.default == inspect._empty
        )
        params.append(prm)
    return params


def export_model_parameters(model : Model) -> List[BlockParameters]:
    """
    Exports a pydantic Model's attributes to use with creating Blockly.
    """
    params = []
    for x, y in model.__annotations__.items():
        if x.endswith("__") or x.startswith("_") or (x == "silent"):
            continue
        p = BlockParameters(
            display_name = x,
            name = x,
            type = parse_blockly_type(y, "INPUT"),
            required = False
        )
        params.append(p)
    return params


def export_selector_parameters(model : Model) -> Tuple[BlockDropdown, BlockParameters]:
    """
    Exports a pydantic Model's attribute names to use with creating Blockly.
    """
    return [
        BlockDropdown(
            display_name = None,
            name = "key",
            options = [
                ["%{BKY_VALUE_" + x.upper() + "}", x] for x in model.__annotations__.keys() 
                if (x not in ["guild_id", "token", "application_id", "version"]) and (not x.startswith("_"))
            ]
        ),
        BlockParameters(
            display_name = None,
            name = "source",
            type = model.__name__,
            required = True
        )
    ]


def make_block_message(
    params : List[Union[BlockParameters, BlockDropdown]],
    prefix : Optional[str] = None,
    category : Optional[str] = None
) -> BlockMessage:
    # TODO: Remove "category".
    """
    Creates a BlockMessage from list of BlockParameters.
    """
    if len(params) == 1:
        return BlockMessage(
            message = (prefix or "") + " %1",
            args = [params[0]]
        )
    else:
        msg = (prefix or "") + "  "
        args = []
        for i, item in enumerate(params):
            # Don't show field name if display name doesn't exists.
            if not item.display_name:
                msg = msg + " " + " %" + str(i + 1)
            else:
                field_string = ("" if not category else category + "_") + item.display_name.upper()
                msg = msg + " " + "%{BKY_FIELD_" + field_string + "}" + " %" + str(i + 1)
            # Insert message.
            args.append(item)
        return BlockMessage(
            message = msg,
            args = args
        )


def define_block(
    category : str,
    name : str,
    parameters : List[Union[BlockParameters, BlockDropdown]],
    style : Optional[str] = None,
    tooltip : Optional[str] = None,
    prefix : Optional[str] = None,
    check : Optional[str] = None,
    is_statement : bool = False
) -> Dict[str, Any]:
    """
    Creates a new block definition for Blockly. 
    """
    deft = {
        "type": f"{category}_{name}",
        "style": lower(style or category) + "_blocks",
        "helpUrl": "%{BKY_HELP_" + category + "_" + name.replace(".", "_") + "}",
        "tooltip": create_docstring(parse_docstring(tooltip or "").get("text")),
    }
    # Define output.
    if is_statement:
        deft["previousStatement"] = check
        deft["nextStatement"] = check
    else:
        deft["output"] = check
    message = make_block_message(
        params = parameters,
        prefix = prefix,
        category = category
    )
    args = []
    for p in message.args:
        if type(p) is BlockParameters:
            args.append({ "type": "input_value", "name": p.name, "check": p.type, "align": "RIGHT" })
        elif type(p) is BlockDropdown:
            args.append({ "type": "field_dropdown", "name": p.name, "options": p.options })
    # Add "args0" and "message0".
    deft.update({
        "message0": message.message,
        "args0": args
    })
    return deft


def append_tag_content(text : str, value : str, strip_tags : bool = False) -> str:
    """
    Appends `value` to the end of `text` without breaking curly braces.

    "{% foo.bar.key %}" -> "{% foo.bar.key.new_key %}"
    """
    tag = []
    source = text
    valid = [
        ["{# ", " #}"],
        ["{< ", " >}"],
        ["{: ", " :}"],
        ["{% ", " %}"]
    ]
    for s, e in valid:
        if source.startswith(s) and source.endswith(e):
            source = source.removeprefix(s).removesuffix(e)
            tag = [s, e]
    if strip_tags:
        return source + value
    if tag:
        return tag[0] + source + value + tag[1]
    return text + value


def get_container_block_values(block : dict) -> Union[Literal[UNDEFINED], Callable]:
    """
    Some blocks such as lists or dictionaries can be defined directly in JSON
    without needing to have a separate step. 

    This method is different than `parse_custom_block()` method. This method
    is for blocks that has inputs, the other method is for blocks that doesn't have any inputs.
    
    So if we have a supported block, we can get the block parameters and 
    return a value directly that will be set as step parameter.
    """
    action = block["action"]
    if action == "LISTS.CREATE":
        return lambda prm: [x for x in prm.values()]
    elif action == "DICTIONARY.PAIR":
        return lambda prm: [] if (not "key" in prm) or (not "value" in prm) else [str(prm["key"]), prm["value"]]
    elif action == "DICTIONARY.CREATE":
        def parse_dict(prm : dict):
            result = {}
            for x in prm.values():
                if (type(x) is list) and (len(x) == 2):
                    result[x[0]] = x[1]
            return result
        return parse_dict
    elif action.startswith("DISCORDM.MODEL_"):
        def parse_model_values(prm : dict):
            if ("source" in prm) and (type(prm["source"]) is str):
                return append_tag_content(prm["source"], "." + prm["key"])
            return None
        return parse_model_values
    elif action.startswith("DISCORDM."):
        return lambda prm: prm
    return UNDEFINED


def parse_custom_block(block : dict, extra : dict, ctx : dict) -> Union[Literal[UNDEFINED], Any]:
    """
    Some blocks such as lists or dictionaries can be defined directly in JSON
    without needing to have a separate step. 

    This method is different than `get_container_block_values()` method. This method
    is for blocks that doesn't have any inputs, the other method is for blocks that have inputs.
    
    So if we have a supported block, we can get the block parameters and 
    return a value directly that will be set as step parameter.
    """
    action = str(block["type"]).replace("_", ".", 1)
    if action == "TEXT.VALUE":
        return block["fields"]["value"].replace("\\n", "\n")
    elif action == "TEXT.MULTILINE_VALUE":
        return block["fields"]["value"]
    elif action == "LOGIC.NONE":
        return None
    elif action == "LOGIC.VALUE":
        return block["fields"]["value"] == "true"
    elif action == "VARIABLE.GET":
        var = extra["variables"][block["fields"]["name"]["id"]]
        # Handle global blocks later, so we stop here.
        if var["type"] == "GLOBAL":
            return UNDEFINED
        return "{# " + "".join([convert_block_id(x) for x in var["id"]]) + " #}"
    elif action == "FUNCTION.VALUE":
        if "loops" in ctx:
            level = len(ctx["loops"][ctx["current_loop"]]) + 1
            return "{% " + ".".join(["parent"] * level) + ".ctx.func_arg %}"
        return None
    elif action == "MATH.VALUE":
        return float(block["fields"]["value"])
    elif action == "WORKFLOW.EVENT_ID":
        return "{% job.id %}"
    # TODO: Remove this.
    elif action == "WORKFLOW.LOOP_ITEM":
        if "loops" in ctx:
            level = len(ctx["loops"][ctx["current_loop"]]) + 1
            return "{% " + ".".join(["parent"] * level) + ".ctx.loop_item %}"
        return None
    elif action == "DISCORDM.COMPONENT_ROW":
        return "ROW"
    return UNDEFINED


def parse_convert_slash_option_name(name : str) -> int:
    """
    Converts a slash parameter option type name to value.
    """
    if name == "TEXT":
        return 3
    return 0


def parse_is_statement(key : str, block : dict, steps : List[Dict]) -> Optional[Tuple[str, Any]]:
    """
    A step can contain inner steps, so we check here if current input's
    blocks needs to be added inside or outside.
    """
    action = block["action"]
    # Check for IF block.
    if (action == "WORKFLOW.IF") and (key == "do"):
        return ("do", block["parameters"].pop("condition", None), )
    # Check for IF/ELSE block.
    elif (action == "WORKFLOW.IF_ELSE"):
        if (key == "do"):
            return ("do", block["parameters"].pop("condition", None), )
        # TODO: Re-enable this.
        """
        elif (key == "else"):
            # TODO: Add this to pyconduit instead.
            # Inject a NOT block for getting the reverse value of condition.
            _id = append_tag_content(block["route_checks"]["do"], "_REVERSE", strip_tags = True)
            steps.append({
                "action": "LOGIC.LOGICAL_NOT",
                "id": _id,
                "parameters": {
                    "value": block["route_checks"]["do"]
                }
            })
            return ("else", "{: " + _id + " :}", )
        """
    # Check for loop block.
    elif (action == "WORKFLOW.LOOP_FOR_EACH"):
        if (key == "do"):
            return ("do", UNDEFINED, )


def save_export_ctx(state : str, block : dict, ctx : dict) -> None:
    action = block["action"]
    if state == "BEFORE_LEVEL":
        if action in [
            "WORKFLOW.IF",
            "WORKFLOW.IF_ELSE",
            "WORKFLOW.LOOP_FOR_EACH"
        ]:
            if (action == "WORKFLOW.LOOP_FOR_EACH"):
                ctx["current_loop"] = block["id"]
                if "loops" not in ctx:
                    ctx["loops"] = {}
                ctx["loops"][block["id"]] = []
            elif "loops" in ctx:
                if block["id"] not in ctx["loops"][ctx["current_loop"]]:
                    ctx["loops"][ctx["current_loop"]].append(block["id"])


def convert_id(text : str):
    return "".join([convert_block_id(x) for x in text])


def parse_blocks(block : dict, extra : dict, ctx : dict = {}) -> List[Dict]:
    """
    Parse a Blockly export format and return a list of pyconduit steps.

    In Blockly, blocks can contain inner blocks, however pyconduit's workflow format
    defines steps as 1-dimensional list, not nested, so this block walks for every block and adds to a list.
    """
    steps = []
    current = {
        "action": str(block["type"]).replace("_", ".", 1),
        "id": convert_id(block["id"])
    }
    if block.get("enabled", True) == False:
        current["enabled"] = False
    # Add block fiels to parameters.
    current["parameters"] = block.get("fields", {})
    # Every input can contain more than more input,
    # and these inputs can contain an inner block.
    for k, v in block.get("inputs", {}).items():
        override = parse_custom_block(v["block"], extra, ctx)
        if override == UNDEFINED:
            # current["parameters"][k] = "{% previous.result %}"
            # [!! CONTINUE FROM HERE !!]
            # TODO: Remove this.
            current["parameters"][k] = "{: " + convert_id(v["block"]["id"]) + " :}"
            save_export_ctx("BEFORE_LEVEL", current, ctx)
            blocks = parse_blocks(v["block"], extra, ctx)
            # If block is a list or dictionary block, then don't add it as a new step, 
            # modify the previous step's parameter instead.
            if blocks:
                container = get_container_block_values(blocks[-1])
                if container != UNDEFINED:
                    current["parameters"][k] = container(blocks.pop()["parameters"])
            # If block is a statement input,
            # add it as a router.
            route, route_check = parse_is_statement(k, current, blocks) or (None, None, )
            if route:
                del current["parameters"][k]
                if (route_check != UNDEFINED):
                    current["condition"] = route_check
                current["steps"] = blocks
            else:
                steps.extend(blocks)
        else:
            current["parameters"][k] = override
    # Check for custom block.
    if current["action"] == "WORKFLOW.CUSTOM_ACTION":
        current["action"] = current["parameters"].get("action", "")
        current["parameters"] = current["parameters"].get("parameters", {})
        if type(current["parameters"]) is not dict:
            current["parameters"] = {}
    elif current["action"] == "VARIABLE.SET":
        var = extra["variables"][current["parameters"]["name"]["id"]]
        # TODO: Hotfix for global variables
        if var["type"] == "GLOBAL":
            current["action"] = "STORAGE.WRITE"
            current["parameters"]["key"] = var["name"].removeprefix("♦ ")
            del current["parameters"]["name"]
        else:
            current["parameters"]["name"] = convert_id(var["id"])
    elif current["action"] == "VARIABLE.GET":
        var = extra["variables"][current["parameters"]["name"]["id"]]
        # TODO: Hotfix for global variables
        if var["type"] == "GLOBAL":
            current["action"] = "STORAGE.READ"
            current["parameters"]["key"] = var["name"].removeprefix("♦ ")
            current["parameters"]["default"] = None
            del current["parameters"]["name"]
    elif current["action"] == "FUNCTION.RETURN":
        current["parameters"]["function"] = extra.get("function_id", None)
    elif current["action"].startswith("WORKFLOW.SLASH_PARAMETER_"):
        current["parameters"]["type"] = parse_convert_slash_option_name(current["action"].removeprefix("WORKFLOW.SLASH_PARAMETER_"))
    # Get dynamic action if defined in parameters.
    if "dynamic_action" in current["parameters"]:
        current["action"] = current["parameters"]["dynamic_action"]
        del current["parameters"]["dynamic_action"]
    # Don't include non-executable blocks.
    if current["action"] in [
        "WORKFLOW.IF",
        "WORKFLOW.IF_ELSE"
    ]:
        current["action"] = "DUMMY"
    # TODO: Hotfix for join_with
    if current["action"] == "TEXT.JOIN":
        current["parameters"]["join_with"] = ""
    # Blockly has option to disable blocks. In this case,
    # don't include disabled blocks in the result.
    # Also ignore dummy blocks.
    if current["action"] not in ["WORKFLOW.DUMMY", "WORKFLOW.FORCED"]:
        if current.get("enabled", True):
            steps.append(current)
    # If block has a previous or/and next connection,
    # get next blocks too.
    if "next" in block:
        steps.extend(parse_blocks(block["next"]["block"], extra, ctx))
    return steps


ListenerData = namedtuple(
    "ListenerData", 
    ["type", "event", "content", "definition", "identity", "override_id"],
    defaults = [None, None, None, {}, None, None]
)

ActionsData = namedtuple(
    "ActionsData",
    ["metadata", "id", "enabled", "blocks"]
)


def define_listener_parser(
    name : str, 
    fields : Dict[str, str], 
    blocks : Dict[str, List]
) -> Optional[ListenerData]:
    """
    Gets the required metadata for saving the action of specified listener name.
    Some listeners require parsed blocks (steps) for building metadata, so we pass the current blocks to this method too.
    """
    # TODO: Make interaction events to work conditionally.
    # TODO: Add a validation to frontend so users can know there are reserved names.
    action = name.replace("_", ".", 1)
    # Gateway event listener, event name is same as with "event" block field.
    # Gateway events are not related with Interactions, so their definitions are empty.
    if action == "WORKFLOW.EVENT_LISTENER":
        if fields["event"] == "-":
            return
        return ListenerData(
            type = "ACTIONS",
            event = fields["event"]
        )
    # Webhook listener.
    elif action == "WORKFLOW.WEBHOOK_LISTENER":
        return ListenerData(
            type = "ACTIONS",
            event = "WEBHOOK"
        )
    # Function definitions.
    elif action == "FUNCTION.CREATE":
        return ListenerData(
            type = "ACTIONS",
            event = "FUNCTION",
            override_id = convert_id(fields["function_id"])
        )
    # Component listeners are listeners that executes the actions when an user interacted
    # with a Message Component such as Selects or Buttons.
    elif action == "WORKFLOW.COMPONENT_LISTENER":
        name = fields["name"].lower().strip().replace(" ", "-").strip("/._\\@#$")
        if name in ["pack", "actions", "relay", "help"]:
            return
        return ListenerData(
            type = "COMPONENT",
            event = "NONE",
            content = name
        )
    # Modal listeners listens for a modal response wih given modal's custom_id.
    elif action == "WORKFLOW.MODAL_LISTENER":
        id = fields["id"].lower().strip().replace(" ", "-").strip("/._\\@#$")
        return ListenerData(
            type = "MODAL",
            event = "NONE",
            content = id
        )
    # Context listeners are listeners that adds an option to Discord's right-click menu under
    # "Apps" for users or messages.
    elif action == "WORKFLOW.CONTEXT_LISTENER":
        context_value = fields["type"]
        content_type = 3 if context_value == "MESSAGE" else 2
        if context_value not in ["MESSAGE", "USER"]:
            return
        context_name = fields["name"].strip().strip("/._\\@#$")
        return ListenerData(
            type = "CONTEXT",
            event = "NONE",
            # TODO: Add condition for context type too.
            content = context_name.lower().replace(" ", "_"),
            definition = {
                "type": content_type,
                "name": context_name
            },
            identity = (content_type, context_name, )
        )
    # Slash listeners registers Slash Commands for current guild.
    elif action == "WORKFLOW.SLASH_LISTENER":
        name = fields["name"].lower().strip().replace(" ", "-").strip("/._\\@#$")
        if name in ["pack", "actions", "relay", "help"]:
            return
        return ListenerData(
            type = "SLASH",
            event = "NONE",
            content = name,
            definition = {
                "type": 1,
                "name": name,
                "description": "A Slash Command created in Relay Actions!",
                "options": [x["parameters"] for x in blocks.get("params", [])]
            },
            identity = (1, name, )
        )


def parse_blocks_all(data : dict) -> List[ActionsData]:
    """
    Parses a Blockly workspace and returns a list of workflows.
    """
    actions = []
    extra = {
        "variables": {x["id"] : x for x in data.get("variables", [])}
    }
    # Make sure we have a Workspace data, not a Block data.
    if ("blocks" not in data) or (type(data["blocks"]) is not dict):
        return []
    if type(data["blocks"].get("blocks", None)) is not list:
        return []
    # Now parse all listeners.
    for b in data["blocks"]["blocks"]:
        # Check if block has inputs.
        if "inputs" not in b:
            continue
        # Check if block contains a "value" statement input.
        if "value" not in b["inputs"]:
            continue
        # Check if block is a "WORKFLOW_*_LISTENER" or "FUNCTION_CREATE" block.
        if (not (b["type"].startswith("WORKFLOW_") and b["type"].endswith("_LISTENER"))) \
            and (not (b["type"] == "FUNCTION_CREATE")):
            continue
        # Start parsing all blocks.
        blocks = {x : parse_blocks(
            block = b["inputs"][x]["block"],
            # Inject current listener's ID for FUNCTION blocks.
            # TODO: Is this the only way?
            extra = {
                **extra, 
                "function_id": convert_id(b.get("fields", {}).get("function_id", "")) or None
            }, 
            ctx = {}
        ) for x in b["inputs"]}
        # Get listener data for block.
        listener = define_listener_parser(
            name = b["type"], 
            fields = b.get("fields", None) or {}, 
            blocks = blocks
        )
        if listener:
            actions.append(
                ActionsData(
                    metadata = listener,
                    id = listener.override_id or convert_id(b["id"]),
                    enabled = b.get("enabled", True),
                    blocks = blocks["value"]
                )
            )
    return actions


BLOCK_ID = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%()*+,-./:;=?@[]^_`{|}~"


def convert_block_id(char : str):
    return str(BLOCK_ID.index(char) + 1).zfill(2)


def make_run(t : str, content : Any, event : str, workflow : str) -> str:
    """
    Creates a new run ID to save the action in database.
    Previously, run IDs was equal with workflow ID, however now run IDs can contain some metadata
    to prevent needing to fetch the whole document.
    """
    if t == "PACK":
        if not isinstance(content, tuple):
            raise ValueError("Parameter `pack` must be a tuple.")
        return f"{content[0]}@{content[1]}.{event}.{workflow}"
    elif t == "SLASH":
        return f"slash@{content}.{event}.{workflow}"
    elif t == "COMPONENT":
        return f"component@{content}.{event}.{workflow}"
    elif t == "CONTEXT":
        return f"context@{content}.{event}.{workflow}"
    elif t == "MODAL":
        return f"modal@{content}.{event}.{workflow}"
    elif t == "ACTIONS":
        return f"actions.{event}.{workflow}"
    raise ValueError("Invalid format.")


def parse_run(run : str) -> Tuple[str, Any, str, str]:
    """
    Parses a run ID which created by make_run() and returns a tuple of parameters.
    """
    *p, e, w = run.split(".")
    p = "".join(p)
    if p == "actions":
        return "ACTIONS", None, e, w,
    elif p.startswith("slash@"):
        return "SLASH", p.removeprefix("slash@"), e, w, 
    elif p.startswith("component@"):
        return "COMPONENT", p.removeprefix("component@"), e, w, 
    elif p.startswith("context@"):
        return "CONTEXT", p.removeprefix("context@"), e, w, 
    elif p.startswith("modal@"):
        return "MODAL", p.removeprefix("modal@"), e, w, 
    elif "@" in p:
        return "PACK", tuple(p.split("@")), e, w, 
    raise ValueError("Invalid format.")


def convert_type_name(data):
    """
    Convert a non-subscriptable to name.
    """
    if data in [inspect._empty, EMPTY, UNDEFINED]:
        return (None, None, )
    elif data == bool:
        return ("Boolean", ["Boolean"], )
    # We don't need to get inner type of tuple, so behave like a untyped list.
    elif data in [tuple, Tuple, list]:
        return ("List", ["List"],)
    elif data in [int, float]:
        return ("Number", ["Number", "String"], )
    elif data == Any:
        return (None, None, )
    elif data in [Dict, dict]:
        return ("Dictionary", ["Dictionary"], )
    elif data == str:
        return ("String", None, )
    elif data == Emoji:
        return ("String", None, )
    elif data == Variable:
        return (None, None, )
    elif data == Permissions:
        return ("Permissions", ["Permissions", "Dictionary"], )
    elif data == Color:
        return ("Color", ["Color", "String", "List", "Number"], )
    elif data == LogicalOperators:
        return ("LogicalOperators", ["String", "LogicalOperators"])
    elif (data == type(None)) or (str(data) == "NoneType"):
        return ("NoneType", ["NoneType"], )
    elif data == slice:
        return ("Slice", ["Slice"], )
    elif data in [ObjectOrSnowflake, ValidChannel, ValidMember]:
        return ("ObjectOrSnowflake", ["Snowflake", "ObjectOrSnowflake", "String", "Overwrites", "Role", "Channel", "Message", "Member", "User"], )
    elif data == Snowflake:
        return ("Snowflake", ["Snowflake", "ObjectOrSnowflake", "String"], )
    elif data == Components:
        # return ("Components", ["List", "NoneType", "Component"])
        return ("Components", None, )
    elif data == httpx.Response:
        return ("HTTPResponse", ["HTTPResponse"])
    elif isclass(data) and issubclass(data, Model):
        return (data.__name__, [data.__name__, "Dictionary"], )
    elif isclass(data) and issubclass(data, ConstrainedInt):
        return ("Number", ["Number", "String"], )
    elif data in [HttpUrl, ExtendedUrl]:
        return ("String", None)
    elif data == datetime:
        return ("Datetime", ["Datetime"])
    elif data == timezone:
        return ("Timezone", ["Timezone"])
    return "Unknown"


def flatten(aList):
    t = []
    for i in aList:
        if type(i) != list:
            if i not in t:
                t.append(i)
        else:
            for x in flatten(i):
                if x not in t:
                    t.append(x)
    return t


def exception_hash(exc : Exception) -> str:
    """
    Creates a hash of the exception trace.
    This is used for prevent to creating duplicate exception logs.
    """
    e = format_exception(etype=type(exc), value=exc, tb=exc.__traceback__, limit = 1)[-1]
    e = e.replace(" ", "").replace("\n", "").lower()
    c = crc32(e.encode("utf-8")) & 0xffffffff
    return str(c)


def parse_blockly_type(annotation : Any, io : str):
    parsed = parse_blockly_type_hint(annotation, io)
    if type(parsed) == str:
        return parsed
    args = flatten(parsed or [None])
    if None in args:
        return None
    return args


def generate_model_tree(
    model : Model, 
    exclude : List[str] = [], 
    level_sep : str = " > ",
    opt : str = "*"
):
    """
    Generates a list of annotation names in a pydantic model.
    This also lists the sub-models' annotation names too.

    ```py
    class Author(Model):
        name : str
        id : str

    class Message(Model):
        content : str
        author : Author

    generate_model_tree(Message)
    # Returns: ["content", "author", "author > name", "author > id"]
    ```
    """
    tree = []
    for k, v in model.__annotations__.items():
        # Excluded keys won't be included in tree.
        if k in exclude:
            continue
        args = get_args(v) or [v]
        is_optional = False
        # Allow "Union[Model, None]" type hints too because 
        # they also contain a sub-model at least, even if it is optional.
        # But we can add an indicator to tree, so people can know that 
        # it is an optional field.
        if len(args) == 2 and args[1] == None.__class__:
            args = [args[0]]
            is_optional = True
        # We don't accept Unions, Lists, Dict or anything else.
        # It must be a direct Model annotation.
        elif get_origin(v) != None:
            args = [None]
        # If everything seems fine, create a tree entry.
        if isclass(args[0]) and issubclass(args[0], Model):
            suffix = opt if is_optional else ""
            tree.append(k + suffix)
            for i in generate_model_tree(args[0], exclude, level_sep, opt):
                tree.append(k + suffix + level_sep + i)
        else:
            tree.append(k)
    return tree


def parse_blockly_type_hint(annotation : Any, io : str):
    """
    Convert type hints to list of names for Blockly.
    """
    iom = 1 if io == "INPUT" else 0
    origin = get_origin(annotation)
    overrided = convert_type_name(origin or annotation)
    if overrided != "Unknown":
        return overrided[iom]
    elif origin == None and overrided == "Unknown":
        print(f"Blockly - Unknown field '{annotation}'")
        return None
    else:
        args = []
        for x in get_args(annotation):
            args.append(parse_blockly_type_hint(x, io))
        return args


def get_relay_docs_url(
    language : str = "en",
    page : str = None
) -> str:
    """
    Creates a Relay docs URL.
    """
    # TODO: As there is no English documentation, keep it to always Turkish documentation.
    return "https://relay.ysfchn.com/tr" + (page or "/")
    # return "https://relay.ysfchn.com" + ("" if language == "en" else "/" + language) + (page or "/")


def lower(
    text : str
) -> str:
    """
    Converts a text to lowercase by handling Turkish characters as expected.
    """
    return text.translate(text.maketrans("İI", "ii")).lower()


def load_json(
    data : Union[bytes, str],
    default : Any = None
) -> Union[None, Dict[str, Any], List[Any]]:
    """
    Loads a JSON with orjson, this is a shortcut that swallows the decoding exception and
    returns the default value if JSON couldn't parsed.
    """
    try:
        return orjson.loads(data)
    except orjson.JSONDecodeError:
        return default


def load_toml(
    data : str,
    default : Any = None
) -> Union[None, Dict[str, Any]]:
    """
    Loads a TOML with rtoml, this is a shortcut that swallows the decoding exception and
    returns the default value if TOML couldn't parsed.
    """
    try:
        return rtoml.loads(data)
    except rtoml.TomlParsingError:
        return default


async def send_discord(
    client : httpx.AsyncClient,
    method : str,
    route : str,
    auth : Union[Tuple[str, str], Tuple[str]],
    data : Optional[dict] = None
) -> Tuple[int, Union[None, Dict[str, Any], List[Any]]]:
    """
    Makes a Discord request to httpx.AsyncClient and returns a two-sized tuple,
    first one is for status code and second one is the returned data in JSON.
    """
    resp = await client.request(
        method, f"https://discord.com/api/v9{route}", 
        headers = {"Authorization": " ".join([x or "none" for x in auth])},
        json = data
    )
    data = load_json(await resp.aread())
    return resp.status_code, data


async def send_http(
    client : httpx.AsyncClient,
    method : str,
    url : str,
    data : Optional[dict] = None,
    response : str = "JSON",
    if_http_error : Any = None,
    if_read_error : Any = None
) -> Tuple[httpx.Response, Any]:
    """
    Makes a request and parses the reponse automatically.
    """
    resp = await client.request(method, url, json = data)
    if not resp.is_success:
        return resp, if_http_error,
    if response == "JSON":
        return resp, load_json(await resp.aread(), if_read_error),
    elif response == "TOML":
        return resp, load_toml(await resp.aread(), if_read_error),
    return resp, await resp.aread(),


def create_embed_preview_document(
    url : str = None,
    title : str = None,
    description : str = None,
    author : str = None,
    image : str = None,
    expand_image : bool = True
):
    """
    Creates a HTML string with <meta> tags defined in dictionary.
    """
    tags = {
        "og:url": url,
        "og:title": title,
        "og:description": description,
        "og:site_name": author,
        "og:image": image
    }
    return "<html><head>" + \
        "".join([f"<meta property=\"{x}\" content=\"{y or '{0}'}\">" for x, y in tags.items() if y or x == "og:url"]) + \
        ('<meta name="twitter:card" content="summary_large_image">' if expand_image else '') + \
        "</head><body></body></html>"


def get_avatar_url(
    id : str,
    discriminator : str,
    avatar_hash : str = None,
    extension : str = "jpg",
    size : Optional[int] = 128,
    allow_animated : bool = False
) -> str:
    """
    Creates a Discord avatar URL.
    If there is no avatar_hash, return Discord's default avatar based on discriminator.
    If allow_animated is True, then the returned avatar will be a GIF if avatar is animated even extension is not "gif".
    """
    is_animated = False if (not avatar_hash) or (not allow_animated) else avatar_hash.startswith("a_")
    if avatar_hash:
        return f"https://cdn.discordapp.com/avatars/{id}/{avatar_hash}.{'gif' if is_animated else extension}" + ("?size=" + str(size) if size else "")
    else:
        return f"https://cdn.discordapp.com/embed/avatars/{int(discriminator) % 5}.png"


def get_server_icon_url(
    id : str,
    avatar_hash : str = None,
    extension : str = "jpg",
    size : Optional[int] = 128,
    allow_animated : bool = False
) -> str:
    """
    Creates a Discord server avatar URL.
    If there is no avatar_hash, returns a default avatar.
    If allow_animated is True, then the returned avatar will be a GIF if avatar is animated even extension is not "gif".
    """
    is_animated = False if (not avatar_hash) or (not allow_animated) else avatar_hash.startswith("a_")
    if avatar_hash:
        return f"https://cdn.discordapp.com/icons/{id}/{avatar_hash}.{'gif' if is_animated else extension}" + ("?size=" + str(size) if size else "")
    else:
        return "/assets/static/no_server_icon.jpg"


def parse_language_header(
    header : str,
    include_variants : bool = False,
    default : str = "en"
) -> List[Tuple[str, str]]:
    """
    Parses a Accept-Language header value and returns a list of language codes. 
    Quality values are not returned in list, however they will be sorted according to quality values.
    """
    output = []
    for language in header.lower().replace(" ", "").replace("_", "-").replace(";q=", ";").split(","):
        x = language.split(";")
        output.append((
            # Language code
            (default if x[0] == "*" else \
            x[0] if include_variants else \
            x[0].split("-")[0]),
            # Quality value
            (1 if len(x) == 1 else float(x[1]))
        ))
    if not output:
        return (default, 1)
    return sorted(output, key = lambda x: x[1], reverse = True)


def group_guilds(
    guilds : Dict[str, Any],
    guilds_id : List[str]
):
    """
    Sort and group given guilds.
    """
    guilds_sorted = sorted(
        guilds.items(),
        key = lambda x: int(x[0] in guilds_id) + int(bool(int(x[1]["permissions"]) & 1 << 3)), 
        reverse = True
    )
    guilds_items = {"LAUNCH": [], "INVITE": [], "NO_PERMS": []}
    for k, v in guilds_sorted:
        # If Relay is not in guild and user has permissions, show "Invite" button.
        if (k not in guilds_id) and (int(v["permissions"]) & 1 << 5):
            guilds_items["INVITE"].append([k, v])
        # If Relay is in guild and user has permissions, show "Launch" button.
        elif (int(v["permissions"]) & 1 << 3):
            guilds_items["LAUNCH"].append([k, v])
        # Else show "Missing permissions" button.
        else:
            guilds_items["NO_PERMS"].append([k, v])
    return guilds_items


# TODO: Maybe pydantic or something else would be more efficient. 
def check_value(
    data : Any,
    parameter_type : ParameterType,
    parameter_options : Optional[List[str]] = None
) -> bool:
    """
    Checks for a single value.

    Used in Relay Web.
    """
    if parameter_type == ParameterType.ANY:
        return True
    elif parameter_type == ParameterType.BOOLEAN:
        return data in [False, True]
    elif parameter_type == ParameterType.NUMBER:
        return (type(data) is int) or (type(data) is float)
    elif parameter_type == ParameterType.STRING:
        return type(data) is str
    elif parameter_type == ParameterType.CHOICE:
        return data in parameter_options
    elif parameter_type in [
        ParameterType.ROLE, 
        ParameterType.USER, 
        ParameterType.TCHANNEL, 
        ParameterType.VCHANNEL, 
        ParameterType.SNOWFLAKE
    ]:
        if type(data) is not str:
            return False
        if not str(data).isnumeric():
            return False
        try:
            return HSnowflake(data).created_at.year > 2017
        except Exception:
            return False
    return False


def build_url(
    url : str = None,
    query : Dict[str, str] = None,
    encode : bool = True,
) -> str:
    """
    Creates a unencoded or encoded query string from specified values.
    """
    return (url or "") + ("" if not query else "?" + "&".join([x + "=" + (y if not encode else quote(y, safe = "")) for x, y in query.items() if y != None]))


def convert_guild_locale(
    locale : str
) -> str:
    """
    Converts a Discord guild locale to Relay guild locale.
    """
    l = locale.lower().replace("-", "_")
    if "_" in l:
        return l
    return l + "_" + l


def pack_report_url(
    tr : "StringsStore",
    pack_id : str,
    pack_version : str
) -> str:
    """
    Returns a URL for reporting a Relay Package.
    """
    return build_url(
        "https://github.com/fluxteam/IssueTracker/issues/new",
        {
            "title": "[Relay Packages] " + tr("web.report_title", pack_id),
            "body": (
                f'<!-- {tr("web.report_body")} -->\n\n---\n\n'
                f'* {tr("web.report_package_name")}: `{pack_id}`\n'
                f'* {tr("web.report_package_version")}: `{pack_version}`\n'
                f'* {tr("web.report_language")}: `{tr.language}`\n'
            )
        }
    )


def split_type_value(
    type_value : ParameterType
) -> Union[ 
    Tuple[ParameterType, ParameterType],
    Tuple[None, ParameterType],
    Tuple[ParameterType]
]:
    """
    Splits a ParameterType enum value to parts and returns ParameterType enums in tuple that
    parsed from the base enum.

    For example:
    If a ParameterType.MAPPING_STRING_STRING passed, it returns a tuple that contains (ParameterType.STRING, ParameterType.STRING),
    If a ParameterType.LIST_ROLE passed, it returns a tuple that contains (None, ParameterType.ROLE)

    If output is a tuple that contains two non-empty values, then it is a mapping.
    If output is a tuple that contains two values (first one is None), then it is a list.
    If output is a tuple that contains one value, then it is a single value.

    Used in Relay Web.
    """
    # If type value has;
    # 1 digit  - The value is a single value.
    #
    # 2 digits - The value is a list.
    #            1nd digit is always 1.
    #            2nd digit represents the type of the values.
    #
    # 3 digits - The value is a key/value mapping.
    #            1nd digit is always 1.
    #            2nd digit represents the key's type.
    #            3rd digit represents the value's type.
    val = list(str(type_value.value)[:3])
    # List
    if len(val) == 2 and val[0] == "1":
        return None, ParameterType(int(val[1]))
    # Mapping
    elif len(val) == 3 and val[0] == "1":
        return ParameterType(int(val[1])), ParameterType(int(val[2]))
    # Single
    else:
        return (ParameterType(int(val[0])), )


def parse_form_data(
    form_data : Dict[str, Any],
    parameters : Dict[str, Parameter]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validates package parameters with user specified data.
    It returns a two-item tuple.

    The first value is a boolean value that represents if there are errors with validations.
    And the second value is the user data with default parameters added. If success is False,
    it returns a dictionary of parameter names and error codes.

    Used in Relay Web.
    """
    errors = {}
    data = form_data
    for param_name, param in parameters.items():
        # If type value has;
        # 1 digit  - The value is a single value.
        #
        # 2 digits - The value is a list.
        #            1nd digit is always 1.
        #            2nd digit represents the type of the values.
        #
        # 3 digits - The value is a key/value mapping.
        #            1nd digit is always 1.
        #            2nd digit represents the key's type.
        #            3rd digit represents the value's type.
        types = split_type_value(param.type)
        IS_MAPPING = len(types) == 2 and types[0] != None
        IS_LIST = len(types) == 2 and types[0] == None
        IS_SINGLE = len(types) == 1
        value = data.get(param_name, None)
        # If required parameter is not specified.
        if param.required and value == None:
            errors[param_name] = "missing_required_value"
        # TODO: Maybe add another a package metadata option to allow empty list and mapping.
        # If parameter is a list or mapping and user
        # has specified a value but contains no items, return error.
        elif IS_MAPPING and param.required and (type(value) is dict) and len(value) == 0:
            errors[param_name] = "has_no_item"
        elif IS_LIST and param.required and (type(value) is list) and len(value) == 0:
            errors[param_name] = "has_no_item"
        # If parameter is not specified, use default.
        elif value == None:
            data[param_name] = param.default
        # Check maximum value size.
        elif len(str(value)) > 300:
            errors[param_name] = "value_too_long"
        # If type is not correct, return error.
        # Check for single type.
        elif IS_SINGLE:
            if not check_value(data = value, parameter_type = types[0], parameter_options = param.options):
                errors[param_name] = "invalid_value"
        # Check for list type.
        elif IS_LIST and (type(value) is list):
            for item in value:
                if not check_value(data = item, parameter_type = types[1], parameter_options = param.options):
                    errors[param_name] = "invalid_value"
        # Check for mapping type.
        elif IS_MAPPING and (type(value) is dict):
            for k, v in value.items():
                status = all([
                    check_value(data = k, parameter_type = types[0], parameter_options = param.options),
                    check_value(data = v, parameter_type = types[1], parameter_options = param.options)
                ])
                if not status:
                    errors[param_name] = "invalid_value"
        else:
            errors[param_name] = "invalid_value"
    if errors:
        return False, errors
    else:
        return True, data