#/graph.py
#langgragh stateflow model with nodes and edges 

from langgraph.graph import StateGraph, START, END
from typing import Dict, Any

from src.validators import validate
from src.market_orders import execute_market_order
from src.limit_orders import execute_limit_order
from src.stop_limit import execute_stop_limit_order
from src.advanced.oco import execute_oco_order
from src.advanced.twap import execute_twap_order

from src.logger import log_info, log_error


State = Dict[str, Any]


def build_bot_graph():

    graph = StateGraph(State)

    def validate_node(state: State) -> State:
        try:
            cleaned = validate(state)
            return {**state, **cleaned}
        except Exception as e:
            log_error("Validation error", {"error": str(e)})
            raise

    def route_node(state: State):
        return {"next": state["order_type"].lower(), **state}

    def market_node(state: State) -> State:
        return execute_market_order(
            state["client"],
            state["symbol"],
            state["side"],
            state["quantity"]
        )

    def limit_node(state: State) -> State:
        return execute_limit_order(
            state["client"],
            state["symbol"],
            state["side"],
            state["quantity"],
            state["price"]
        )

    def stop_limit_node(state: State) -> State:
        return execute_stop_limit_order(
            state["client"],
            state["symbol"],
            state["side"],
            state["quantity"],
            state["stop_price"],
            state["price"]
        )
 
    def oco_node(state: State) -> State:
        return execute_oco_order(
            state["client"],
            state["symbol"],
            state["side"],
            state["quantity"],
            state["price"],
            state["stop_price"]
        )

    def twap_node(state: State) -> State:
        return execute_twap_order(
            state["client"],
            state["symbol"],
            state["side"],
            state["quantity"]
        )

    def done_node(state: State) -> State:
        log_info("Order execution complete", {"result": state})
        return state

    # Nodes
    graph.add_node("validate_node", validate_node)
    graph.add_node("route_node", route_node)
    graph.add_node("market_node", market_node)
    graph.add_node("limit_node", limit_node)
    graph.add_node("stop_limit_node", stop_limit_node)
    graph.add_node("oco_node", oco_node)
    graph.add_node("twap_node", twap_node)
    graph.add_node("done_node", done_node)

    # EDGES
    graph.set_entry_point("validate_node")
    graph.add_edge("validate_node", "route_node")
    graph.add_conditional_edges(
        "route_node",
        lambda s: s["next"],
        {
            "market": "market_node",
            "limit": "limit_node",
            "stop_limit": "stop_limit_node",
            "oco": "oco_node",
            "twap": "twap_node",
        }
    )


    execution_nodes = [
        "market_node", 
        "limit_node", 
        "stop_limit_node", 
        "oco_node", 
        "twap_node"
    ]
    for node in execution_nodes:
        graph.add_edge(node, "done_node")
    
    
    graph.add_edge("done_node", END)

    return graph.compile()
