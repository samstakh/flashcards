from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('viewDecks/', views.viewDecks, name='viewDecks'),
    path('addCard/', views.addCard, name='addCard'),
    path('addDeck/', views.addDeck, name='addDeck'),
    path('viewDeck/<int:deck_id>/', views.viewDeck, name='viewDeck'),
    path('addCard/<int:deck_id>/', views.addCard, name='addCard'),
    path('viewCards/<int:deck_id>/', views.viewCards, name='viewCards'),
    path('editCard/<int:card_id>/edit', views.editCard, name='editCard'),
    path('deleteCard/<int:card_id>/delete', views.deleteCard, name='deleteCard'),
    path('study/<int:deck_id>/', views.studyDeck, name='studyDeck'),
    path("set_timezone/", views.set_timezone, name="set_timezone"),
    path("copy/<str:token>/", views.copy_shared_deck, name="copy_shared_deck"),
    path('shared/<str:token>/', views.sharedDeckView, name='shared_deck_view'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]       