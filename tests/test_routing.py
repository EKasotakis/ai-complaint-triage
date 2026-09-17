from app.routing import route_complaint
from app.schemas import ComplaintCategory


def test_technical_routing():
    team = route_complaint(ComplaintCategory.TECHNICAL)
    assert team == "Technical Support"


def test_product_quality_routing():
    team = route_complaint(ComplaintCategory.PRODUCT_QUALITY)
    assert team == "Quality Team"


def test_delivery_routing():
    team = route_complaint(ComplaintCategory.DELIVERY)
    assert team == "Logistics Team"


def test_billing_routing():
    team = route_complaint(ComplaintCategory.BILLING)
    assert team == "Finance Team"


def test_other_routing():
    team = route_complaint(ComplaintCategory.OTHER)
    assert team == "Customer Service"