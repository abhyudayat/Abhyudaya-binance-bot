# project_root/graph.py

from langgraph.graph import StateGraph

from src.validators import validate
from src.market_orders import execute_market_order
from src.limit_orders import execute_limit_order
from src.stop_limit import execute_stop_limit_order
from src.advanced.oco import execute_oco_order
from src.advanced.twap import execute_twap_order

from src.logger import log_info, log_error


def build_bot_graph():
    graph = StateGraph()

    # -------------------------------------------------
    # Step 1: VALIDATE INPUT
    # -------------------------------------------------
    @graph.node
    def validate_node(state):
        try:
            cleaned = validate(state)
            return {**state, **cleaned}  # merge normalized fields
        except Exception as e:
            log_error("Validation error", {"error": str(e), "input": state})
            raise

    # -------------------------------------------------
    # Step 2: ROUTE ORDER TYPE
    # -------------------------------------------------
    @graph.node
    def route_node(state):
        return state["order_type"].lower()   # return next-node key

    # -------------------------------------------------
    # Step 3A: MARKET ORDER
    # -------------------------------------------------
    @graph.node
    def market_node(state):
        client = state["client"]
        return execute_market_order(
            client,
            state["symbol"],
            state["side"],
            state["quantity"]
        )

    # -------------------------------------------------
    # Step 3B: LIMIT ORDER
    # -------------------------------------------------
    @graph.node
    def limit_node(state):
        client = state["client"]
        return execute_limit_order(
            client,
            state["symbol"],
            state["side"],
            state["quantity"],
            state["price"],
        )

    # -------------------------------------------------
    # Step 3C: STOP-LIMIT
    # -------------------------------------------------
    @graph.node
    def stop_limit_node(state):
        client = state["client"]
        return execute_stop_limit_order(
            client,
            state["symbol"],
            state["side"],
            state["quantity"],
            state["stop_price"],
            state["price"]
        )

    # -------------------------------------------------
    # Step 3D: OCO ORDER
    # -------------------------------------------------
    @graph.node
    def oco_node(state):
        client = state["client"]
        return execute_oco_order(
            client,
            state["symbol"],
            state["side"],
            state["quantity"],
            state["price"],
            state["stop_price"]
        )

    # -------------------------------------------------
    # Step 3E: TWAP ORDER
    # -------------------------------------------------
    @graph.node
    def twap_node(state):
        client = state["client"]
        return execute_twap_order(
            client,
            state["symbol"],
            state["side"],
            state["quantity"]
        )

    # -------------------------------------------------
    # Final Node
    # -------------------------------------------------
    @graph.node
    def done_node(state):
        log_info("Order execution complete", {"result": state})
        return state

    # -------------------------------------------------
    # Graph Edges
    # -------------------------------------------------

    graph.add_edge("validate_node", "route_node")

    graph.add_conditional_edges(
        "route_node",
        {
            "market": "market_node",
            "limit": "limit_node",
            "stop_limit": "stop_limit_node",
            "oco": "oco_node",
            "twap": "twap_node",
        }
    )

    graph.add_edge("*", "done_node")

    return graph.compile()
