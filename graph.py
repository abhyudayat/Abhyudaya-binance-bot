# project_root/graph.py

from langgraph.graph import StateGraph
from src.validators import validate
from src.market_orders import execute_market
from src.limit_orders import execute_limit
from src.stop_limit import execute_stop_limit
from src.advanced.oco import execute_oco
from src.advanced.twap import execute_twap
from src.advanced.grid_strategy import execute_grid
from src.logger import log, log_error


def build_bot_graph():
    """
    Builds a LangGraph workflow that:
    1. Validates the input
    2. Routes to the correct order module
    3. Logs and returns output
    """

    graph = StateGraph()

    # --- Node 1: VALIDATE INPUT ---
    @graph.node
    def validate_node(state):
        try:
            cleaned = validate(state)
            return cleaned
        except Exception as e:
            log_error("Validation error", {"error": str(e), "input": state})
            raise

    # --- Node 2: ROUTE ORDER TYPE ---
    @graph.node
    def route_node(state):
        order_type = state["order_type"].lower()

        # return a special key that determines the next node
        return {"next": order_type, **state}

    # --- Node 3A: MARKET ORDER ---
    @graph.node
    def market_node(state):
        return execute_market(state)

    # --- Node 3B: LIMIT ORDER ---
    @graph.node
    def limit_node(state):
        return execute_limit(state)

    # --- Node 3C: STOP-LIMIT ORDER ---
    @graph.node
    def stop_limit_node(state):
        return execute_stop_limit(state)

    # --- Node 3D: OCO ORDER ---
    @graph.node
    def oco_node(state):
        return execute_oco(state)

    # --- Node 3E: TWAP ORDER ---
    @graph.node
    def twap_node(state):
        return execute_twap(state)

    # --- Node 3F: GRID ORDER ---
    @graph.node
    def grid_node(state):
        return execute_grid(state)

    # Final order → logger
    @graph.node
    def done_node(state):
        log("Order execution complete", state)
        return state

    # --- Graph Structure ---

    graph.add_edge("validate_node", "route_node")

    graph.add_conditional_edges(
        "route_node",
        {
            "market": "market_node",
            "limit": "limit_node",
            "stop_limit": "stop_limit_node",
            "oco": "oco_node",
            "twap": "twap_node",
            "grid": "grid_node",
        }
    )

    graph.add_edge("*", "done_node")

    return graph.compile()
