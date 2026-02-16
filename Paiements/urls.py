from django.urls import path
from .import views

urlpatterns = [
    path('liste_paiements/', views.PaiementListView.as_view(), name='Liste_paiements'),
    path('detail_paiement/<int:pk>/', views.PaiementDetailView.as_view(), name='detail_paiement'),
    path('tombola_list/', views.TombolaListView.as_view(), name='liste_tombola'),

    path('scanner/<str:reference>/', views.scanner_qr_code, name='scanner_qr_code'),
    path('<int:paiement_id>/gratter/', views.gratter_reduction, name='gratter_reduction'),
]