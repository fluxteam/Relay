from typing import Any, List, Optional, Union
from pyconduit import Category, Node, Job
from pyconduit import block
from relay.utils import convert_id

def go_until_id(node : Node, id : str) -> Optional[Node]:
    if node.is_root:
        return
    if id == node.id:
        return node
    return go_until_id(node._parent, id)

class Workflow(Category):
    """
    Blocks to manage workflow.
    """

    @block(tags = ["SKIP"])
    @staticmethod
    def set_parent_context(
        node__ : Node,
        *,
        key : str,
        value : Any
    ) -> None:
        print("Running set_parent_context for", key, value)
        node__.parent.ctx[key] = value

    @block(tags = ["SKIP"])
    @staticmethod
    def loop_for_each(
        node__ : Node,
        *,
        iterable : Union[List[Any], str, dict]
    ) -> None:
        """
        For each.
        """
        nodes = []
        length = len(iterable)
        copied_nodes = None
        for i, value in enumerate(iterable):
            x = node__.new_node(action = "WORKFLOW.SET_PARENT_CONTEXT", parameters = {
                    "key": "loop_item",
                    "value": value
                })
            nodes.append(x)
            if copied_nodes == None:
                copied_nodes = node__.nodes.copy().items
            # Don't copy steps in the last iteration,
            # because they are already defined.
            if i != (length - 1):
                nodes.extend(copied_nodes)
        node__.nodes.add_items(nodes, True)

    @block(label = "function.call", tags = ["SKIP"])
    @staticmethod
    def function_call(
        job__ : Job,
        node__ : Node,
        *,
        function_id : str,
        value : Any,
        name : str
    ) -> None:
        func : Optional[list] = job__.ctx.get("functions", {}).get(convert_id(function_id), None)
        if not func:
            raise ValueError(f"Function '{convert_id(function_id)}' not found.")
        node__.parent.nodes_from_array([
        {
            "action": "WORKFLOW.SET_PARENT_CONTEXT",
            "parameters": {
                "key": "func_arg",
                "value": value
            }
        },
        {
            "action": "DUMMY",
            "steps": func["steps"],
            "id": convert_id(function_id)
        }, 
        {
            "action": "WORKFLOW.SELF_GET",
            "parameters": {
                "value": "{% parent.ctx.func_value %}"
            }
        }], True)
        print("\n".join(node__.job.tree(4)))

    @block(label = "function.return", tags = ["SKIP"])
    @staticmethod
    def function_return(
        node__ : Node,
        *,
        function : str,
        value : Any
    ) -> None:
        n = go_until_id(node__, function)
        n.parent.ctx["func_value"] = value
        print("Set context to:", repr(n.parent))