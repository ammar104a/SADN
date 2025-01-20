from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Example view
    path('login/', views.login_view, name='login'),
    path('checkin-toggle/', views.checkin_toggle, name='checkin_toggle'),
    path('company/<int:company_id>/', views.dialer_view, name='company_detail'),
    path('autodialer/', views.dialer_view, name='dialer_view'),
    path('dialer/company/<int:company_id>/', views.dialer_view, name='company_detail'),
    path('dialer/company/<int:company_id>/outcome/', views.record_call_outcome, name='record_call_outcome'),
    # No company_id: will default to the first company
    path('dialer/', views.dialer_view, name='dialer_view_no_id'),

    # With company_id: user can navigate among specific companies
    path('dialer/<int:company_id>/', views.dialer_view, name='dialer_view'),
    path('logout/', views.logout_view, name='logout'),
    path('company/<int:company_id>/comment/', views.add_company_comment, name='add_company_comment'),
    path('start-call/<int:company_id>/', views.start_call, name='start_call'),
# urls.py
path('api/llama-chat/', views.llama_chat, name='llama_chat'),

]
