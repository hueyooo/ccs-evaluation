from django.urls import path
from . import views

urlpatterns = [
  path("", views.home, name="home"),
  path('login/', views.loginuser, name='login'),
  path('logout/', views.logoutuser, name='logout'),
  path('home/', views.home, name='home'),
  path('sign-up/<str:role>', views.sign_up, name='sign_up'),
  path('sign-up/', views.role, name='role'),
  path('profile/update', views.update_profile, name='update_profile'),
  path('evaluation/', views.evaluation_select, name='evaluation_select'),
  path('evaluation/<int:evaluated>', views.questionnaire, name='questionnaire'),
  path('evaluation/edit_questionnaire', views.edit_questionnaire, name='edit_questionnaire'),
  path('evaluation/edit_questionnaire/<int:id>', views.update_questionnaire, name='update_questionnaire'),
  path('evaluation/edit_questionnaire/add_<str:category>', views.add_questionnaire, name='add_questionnaire'),
  path('evaluation/edit_questionnaire/delete_<int:id>', views.delete_questionnaire, name='delete_questionnaire'),
  path('evaluation/view', views.view_responses, name='view_responses'),
  path('evaluation/view/completion-chart', views.view_completion_chart, name='view_completion_chart'),
  path('evaluation/view/instructor-chart', views.view_instructor_chart, name='view_instructor_chart'),
  path('evaluation/view/instructor-chart/<str:section>', views.view_instructor_chart_per_section, name='view_instructor_chart_per_section'),
  path('evaluation/view/instructor-chart/<str:section>/<int:id>', views.view_instructor_chart_id, name='view_instructor_chart_id'),
  path('evaluation/edit-instructor', views.edit_instructor, name='edit_instructor'),
  path('evaluation/edit-instructor/<str:section>', views.edit_instructor_per_section, name='edit_instructor_per_section'),
  path('evaluation/edit-instructor/<str:section>/<int:id>', views.edit_instructor_per_id, name='edit_instructor_per_id'),
  path('evaluation/edit-instructor/<str:section>/<int:id>/delete', views.delete_instructor_per_id, name='delete_instructor'),
  path('evaluation/edit-instructor/<str:section>/add', views.add_instructor, name='add_instructor'),
  path('settings', views.settings, name='settings'),
]