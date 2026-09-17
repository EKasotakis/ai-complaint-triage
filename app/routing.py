from app.schemas import ComplaintCategory


ROUTING_RULES = {
    ComplaintCategory.TECHNICAL: "Technical Support",
    ComplaintCategory.PRODUCT_QUALITY: "Quality Team",
    ComplaintCategory.DELIVERY: "Logistics Team",
    ComplaintCategory.BILLING: "Finance Team",
    ComplaintCategory.OTHER: "Customer Service",
}


def route_complaint(category: ComplaintCategory) -> str:
    return ROUTING_RULES[category]