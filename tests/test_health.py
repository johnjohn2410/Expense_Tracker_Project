import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_check_smoke(client):
    resp = client.get(reverse("health_check"))
    assert resp.status_code in (200, 503)  # healthy or unhealthy
    data = resp.json()
    assert "status" in data
