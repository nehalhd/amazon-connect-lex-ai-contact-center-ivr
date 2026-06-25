

import json

# --- Mock "database" -------------------------------------------------------
MOCK_ORDERS = {
    "12345": {"status": "Shipped", "eta": "June 26, 2026", "item": "Wireless Headphones"},
    "67890": {"status": "Processing", "eta": "June 28, 2026", "item": "Smart Watch"},
    "11111": {"status": "Delivered", "eta": "Delivered on June 20, 2026", "item": "Bluetooth Speaker"},
}

STORE_HOURS_MESSAGE = (
    "Our store is open Sunday through Thursday, from 9 AM to 9 PM, "
    "and Friday and Saturday from 10 AM to 6 PM."
)


def lambda_handler(event, context):
    """Lex V2 invokes this with the full session state on every fulfillment/code-hook call."""
    intent_name = event["sessionState"]["intent"]["name"]
    slots = event["sessionState"]["intent"]["slots"]

    if intent_name == "CheckOrderStatus":
        return handle_check_order_status(event, slots)
    elif intent_name == "StoreHours":
        return close_dialog(event, "Fulfilled", STORE_HOURS_MESSAGE)
    elif intent_name == "SpeakToAgent":
        return close_dialog(
            event,
            "Fulfilled",
            "Sure, connecting you with a live agent now. Please hold.",
        )
    else:
        return close_dialog(
            event,
            "Fulfilled",
            "I'm sorry, I didn't quite catch that. Could you rephrase, "
            "or say 'agent' to speak with someone?",
        )


def handle_check_order_status(event, slots):
    order_number = get_slot_value(slots, "OrderNumber")

    # Slot not filled yet -> ask for it (Lex will re-invoke this Lambda once it has the value)
    if not order_number:
        return elicit_slot(event, "OrderNumber", "Sure — what's your order number?")

    order = MOCK_ORDERS.get(order_number)
    if order:
        if order["status"] == "Delivered":
            message = f"Your order for the {order['item']} was {order['eta']}."
        else:
            message = (
                f"Your order for the {order['item']} is currently {order['status']}. "
                f"Estimated delivery: {order['eta']}."
            )
    else:
        message = (
            f"I couldn't find an order with number {order_number}. "
            "Please double check the number, or say 'agent' to speak with someone."
        )

    return close_dialog(event, "Fulfilled", message)


# --- Lex V2 response helpers -------------------------------------------------

def get_slot_value(slots, slot_name):
    slot = slots.get(slot_name)
    if slot and slot.get("value"):
        return slot["value"].get("interpretedValue")
    return None


def elicit_slot(event, slot_name, message):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_name,
            },
            "intent": event["sessionState"]["intent"],
            "sessionAttributes": event["sessionState"].get("sessionAttributes", {}),
        },
        "messages": [{"contentType": "PlainText", "content": message}],
    }


def close_dialog(event, fulfillment_state, message):
    intent = event["sessionState"]["intent"]
    intent["state"] = fulfillment_state
    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": intent,
            "sessionAttributes": event["sessionState"].get("sessionAttributes", {}),
        },
        "messages": [{"contentType": "PlainText", "content": message}],
    }
