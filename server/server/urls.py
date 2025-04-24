from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("insights/", include("ai_insights.urls")),
    path("core/", include("core.urls")),
    path("odds/", include("odds.urls")),
    path("arbitrage/", include("odds.arbitrage.urls")),
]
