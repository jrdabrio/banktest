from rest_framework import routers

from .api.viewsets import AccountViewSet

app_name = "bank"

router = routers.DefaultRouter()
router.register(r"accounts", AccountViewSet, basename="account")

urlpatterns = router.urls
