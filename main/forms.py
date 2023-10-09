from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Student, Instructor, Questionnaire

User = get_user_model()

class StudentRegisterForm(UserCreationForm):
  email = forms.EmailField(required=True)
  role = forms.CharField(disabled=True, initial='Student')
  first_name = forms.CharField(required=True)
  last_name = forms.CharField(required=True)

  class Meta:
    model = User
    fields = ["role", "username", "email", "first_name", "last_name", "password1", "password2"]
    
class SectionForm(forms.ModelForm):
  class Meta:
    model = Student
    fields = ["section"]

class InstructorRegisterForm(UserCreationForm):
  email = forms.EmailField(required=True)
  role = forms.CharField(disabled=True, initial='Instructor')
  first_name = forms.CharField(required=True)
  last_name = forms.CharField(required=True)

  class Meta:
    model = User
    fields = ["role", "username", "email", "first_name", "last_name", "password1", "password2"]

class InstructorForm(forms.ModelForm):
  class Meta:
    model = Instructor
    fields = ["department", "access_lvl"]

class UpdateUserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ["email", "first_name", "last_name", "image"]

class UpdateQuestionnaire(forms.ModelForm):
  category = forms.CharField(disabled=True)
  question = forms.CharField(widget=forms.Textarea(attrs={"rows":5}), required=True)

  class Meta:
    model = Questionnaire
    fields = ["category", "question"]

