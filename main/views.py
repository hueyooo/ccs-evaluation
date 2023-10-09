from django.shortcuts import render, redirect
from .forms import StudentRegisterForm, SectionForm, InstructorRegisterForm, InstructorForm, UpdateUserForm, UpdateQuestionnaire
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Questionnaire, Student, Instructor, EvaluatedDetails, QuestionnaireScore, Comment, Subjects
from django.contrib.auth import get_user_model, authenticate, login, logout
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .decorators import unauthenticated_user, authenticated_user_admin, authenticated_user_eval

User = get_user_model()

#Sign in
@unauthenticated_user
def loginuser(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
      login(request, user)
      return redirect('/home')
    else:
      messages.success(request, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
      return redirect('/login')
  else:
    return render(
      request, 
      'registration/login.html',
    )

#Sign Out
@login_required(login_url="/login")
def logoutuser(request):
  logout(request)
  return redirect('login')

#Home
@login_required(login_url="/login")
def home(request):
  return render(
    request, 
    'main/home.html'
  )

#Sign Up
@login_required(login_url="/login")
@authenticated_user_admin
def role(request):
  getrole = 'Student'
  getrole2 = 'Instructor'
  
  return render(
    request, 
    ('registration/role.html'), 
    {"roles":getrole, 
     "rolei":getrole2
    }
  )

@login_required(login_url="/login")
@authenticated_user_admin
def sign_up(request, role):
  if role == 'Student':
    if request.method == 'POST':
      form = StudentRegisterForm(request.POST)
      form2 = SectionForm(request.POST)
      if form.is_valid() and form2.is_valid():
        print(form.cleaned_data)
        print(form2.cleaned_data)
        form.save()
        usern = form.cleaned_data['username']
        users = User.objects.all()
        for user in users:
          if user.username == usern:
            user_id = user.id
        
        sec = form2.cleaned_data['section']
        stud = Student(
          user_id=user_id,
          section=sec
        )
        stud.save()
        
        return redirect('/sign-up')
    else:
      form = StudentRegisterForm()
      form2 = SectionForm()
  elif role == 'Instructor':
    if request.method == 'POST':
      form = InstructorRegisterForm(request.POST)
      form2 = InstructorForm(request.POST)
      if form.is_valid() and form2.is_valid():
        print(form.cleaned_data)
        print(form2.cleaned_data)
        form.save()
        usern = form.cleaned_data['username']
        users = User.objects.all()
        for user in users:
          if user.username == usern:
            user_id = user.id
        
        dept = form2.cleaned_data['department']
        al = form2.cleaned_data['access_lvl']
        inst = Instructor(
          user_id=user_id, 
          department=dept, 
          access_lvl=al
        )
        inst.save()
        
        return redirect('/sign-up')
    else:
      form = InstructorRegisterForm()
      form2 = InstructorForm()

  return render(
    request, 
    'registration/sign_up.html', 
    {"form": form, 
     "form2": form2}
  )

#Profile
@login_required(login_url="/login")
def update_profile(request):
  if request.method == "POST":
    form = UpdateUserForm(
      request.POST, 
      request.FILES,
      instance=request.user
    )
    if form.is_valid():
      form.save()
      return redirect('update_profile')
  else:
    form = UpdateUserForm(instance=request.user)

  return render(
    request, 
    'main/updt_profile.html', 
    {"form": form}
  )

#Evaluation
@login_required(login_url="/login")
def evaluation_select(request):
  check_completed = Comment.objects.all()
  to_eval = []
  if request.user.role == "Student":
    to_evaluate = EvaluatedDetails.objects.all()
    for evaluate in to_evaluate:
      if request.user.student.section == evaluate.section:
        to_eval.append(evaluate)
  elif request.user.role == "Instructor":
    to_evaluate = Instructor.objects.all()
    for evaluate in to_evaluate:
      if request.user.instructor.department == evaluate.department:
        to_eval.append(evaluate)

  if request.user.is_superuser:
    return render(
      request,
      'main/admin_evaluation.html',
      {
        "evaluate": to_eval,
        "completed": check_completed,
      }
    )
  else:
    return render(
      request,
      'main/evaluation.html',
      {
        "evaluate": to_eval,
        "completed": check_completed,
      }
    )
  

#Evaluation questionnaire submit
@login_required(login_url="/login")
@authenticated_user_eval
def questionnaire(request, evaluated):
  questions = Questionnaire.objects.all()
  check_completed = QuestionnaireScore.objects.all()
  check_sub = EvaluatedDetails.objects.all()
  check_dept = Instructor.objects.all()

  if request.method == 'POST':
    for question in questions:
      get_question_id = str(question.id)
      get_question_id_value = request.POST[get_question_id]
      converted_value = int(get_question_id_value)
      question_score = QuestionnaireScore(
        score = converted_value,
        author_id = request.user.id,
        question_id = question.id,
        evaluated_id = evaluated
      )
      question_score.save()

    comment = request.POST['comment']
    sentiment_analyzer = SentimentIntensityAnalyzer()
    comment_sentiment = sentiment_analyzer.polarity_scores(comment)
    if comment_sentiment['compound'] > 0.0:
      cs = 'Positive'
    elif comment_sentiment['compound']  == 0:
      cs = 'Neutral'
    elif comment_sentiment['compound']  < 0:
      cs = 'Negative'

    user_comment = Comment(
      comment = comment,
      sentiment = cs,
      author_id = request.user.id,
      evaluated_id = evaluated
    )
    user_comment.save()

    return redirect('/evaluation')
  
  for check in check_completed:
    if check.author.id == request.user.id and check.evaluated.user.id == evaluated:
      return redirect('/evaluation')
    
  checked = False
  if request.user.role == 'Student':
    for sub in check_sub:
      if request.user.student.section == sub.section:
        if sub.inst.user.id == evaluated:
          checked = True
          break
  elif request.user.role == 'Instructor':
    for dept in check_dept:
      if request.user.instructor.department == dept.department:
        if dept.user.id == evaluated:
          checked = True
          break
  
  if checked == False:
    return redirect('/evaluation')

  return render(
    request, 
    'main/questionnaire.html', 
    {"questions": questions}
  )

# Edit Questionnaire
@login_required(login_url="/login")
@authenticated_user_admin
def edit_questionnaire(request):
  questions = Questionnaire.objects.all()

  return render(
    request, 
    'main/edit_questionnaire.html', 
    {"questions": questions}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def update_questionnaire(request, id):
  questions = Questionnaire.objects.all()
  for question in questions:
    if question.id == id:
      upd_question = question
      break

  if request.method == "POST":
    form = UpdateQuestionnaire(
      request.POST, 
      request.FILES,
      instance=upd_question
    )
    if form.is_valid():
      form.save()
      return redirect('edit_questionnaire')
  else:
    form = UpdateQuestionnaire(instance=upd_question)

  return render(
    request,
    'main/update_questionnaire.html',
    {"question": upd_question,
     "form": form}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def add_questionnaire(request, category):
  if request.method == "POST":
    add_questionnaire = Questionnaire(
      category = category,
      question = request.POST['question']
    )
    add_questionnaire.save()
    return redirect('edit_questionnaire')

  return render(
    request,
    'main/add_questionnaire.html',
    {"category": category}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def delete_questionnaire(request, id):
  question = Questionnaire.objects.get(id=id)
  question.delete()
  
  return redirect('edit_questionnaire')

#View Responses
@login_required(login_url="/login")
@authenticated_user_admin
def view_responses(request):
  return render(
    request,
    'main/view_responses.html'
  )

@login_required(login_url="/login")
@authenticated_user_admin
def view_completion_chart(request):
  sort_sec = sort_section()

  users = User.objects.all()
  eval_deets = EvaluatedDetails.objects.all()
  students = Student.objects.all()
  evaluated = QuestionnaireScore.objects.all()
  get_evaluated_true = []
  get_evaluated_total = []

  for user in users:
    if user.role == 'Student':
      get_to_eval = []
      for student in students:
        if user == student.user:       
          for eval in eval_deets:
            if student.section == eval.section:
              get_to_eval.append(eval.inst.user.id)

      check_completed = False
      for get in get_to_eval:
        is_evaluated = False
        for check in evaluated:
          if user == check.author and get == check.evaluated.user.id:
            is_evaluated = True
            break
        
        if is_evaluated == False:
          check_completed = False
          break
        else:
          check_completed = True
      
      if check_completed:
        get_evaluated_true.append(user.student.section)
      get_evaluated_total.append(user.student.section)

  y=[]
  for get_sec_value in get_evaluated_true:
    if not y:
      x = get_evaluated_true.count(get_sec_value)
      y.append({'section': get_sec_value, 'count': x})
    else:
      for z in y:
        x = get_evaluated_true.count(get_sec_value)
        if z['section'] != get_sec_value:
          y.append({'section': get_sec_value, 'count': x})
    
  a=[]
  for get_sec_value in get_evaluated_total:
    if not a:
      b = get_evaluated_total.count(get_sec_value)
      a.append({'section': get_sec_value, 'count': b})
    else:
      for c in a:
        b = get_evaluated_total.count(get_sec_value)
        if c['section'] != get_sec_value:
          a.append({'section': get_sec_value, 'count': b}) 
        
  return render(
    request,
    'main/view_completion_chart.html',
    {'section': sort_sec,
     'value': y,
     'total': a}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def view_instructor_chart(request):
  sort_sec = sort_section()

  return render(
    request,
    'main/view_instructor_chart.html',
    {'section': sort_sec}
  )

def sort_section():
  sections = Student.objects.all()
  section_array = []

  for section in sections:
    is_found = False
    for check in section_array:
      if section.section == check:
        is_found = True
        break
    
    if is_found == False:
      section_array.append(section.section)

  course = ['IT','IS','CS','ACT']
  year = ['1','2','3','4']
  sect = ['A','B','C','D','E','F','G','H','I','J']
  sort_section = []

  for crs in course:
    for yr in year:
      for sec in sect:
        check_var = crs + "-" + yr + sec
        is_found = False
        for section in section_array:
          if section == check_var:
            is_found = True
            break
        
        if is_found == True:
          sort_section.append(check_var)
  
  return sort_section


@login_required(login_url="/login")
@authenticated_user_admin
def view_instructor_chart_per_section(request, section):
  inst_per_sec = EvaluatedDetails.objects.all()
  instructors = []

  for inst in inst_per_sec:
    if inst.section == section:
      instructors.append(inst)

  return render(
    request,
    'main/view_instructor_per_sec.html',
    {'instructor': instructors,
     'section':section}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def view_instructor_chart_id(request, section, id):
  instructor = Instructor.objects.get(user_id=id)
  questions = Questionnaire.objects.all()
  scores = QuestionnaireScore.objects.all()
  comments = Comment.objects.all()
  subject = EvaluatedDetails.objects.all()
  question_average = []

  for sub in subject:
    if sub.section == section and sub.inst.user.id == id:
      instruct_id = sub.inst.user.id 
      instruct_sub = sub.subj
      break

  for question in questions:
    question_score = 0
    question_score_total_eval = 0
    for score in scores:
      if instruct_id == score.evaluated_id and score.question == question:
        question_score += score.score
        question_score_total_eval += 1
    average = question_score/question_score_total_eval
    ave = "{:.2f}".format(average)
    question_average.append({'category': question.category, 'question': question.question, 'average': ave})

  return render(
    request,
    'main/view_instructor_per_id.html',
    {'instructor': instructor,
     'average': question_average,
     'section': section,
     'subject': instruct_sub}
  )

#Edit Instructor per Section
@login_required(login_url="/login")
@authenticated_user_admin
def edit_instructor(request):
  sort_sec = sort_section()

  return render(
    request,
    'main/edit_instructor.html',
    {'section': sort_sec}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def edit_instructor_per_section(request, section):
  inst_per_sec = EvaluatedDetails.objects.all()
  instructors = []

  for inst in inst_per_sec:
    if inst.section == section:
      instructors.append(inst)

  return render(
    request,
    'main/edit_instructor_per_sec.html',
    {'instructor': instructors,
     'section':section}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def edit_instructor_per_id(request, section, id):
  instructor = EvaluatedDetails.objects.all()
  instructors = Instructor.objects.all()
  subjects = Subjects.objects.all()

  for inst in instructor:
    if inst.section == section and inst.inst.user.id == id:
      instance = inst
      break

  if request.method == 'POST':
    get_instructor = EvaluatedDetails.objects.get(id=inst.id)
    get_instructor_id = int(request.POST['instructor'])
    get_sub_id = int(request.POST['subject'])
    get_instructor.inst_id = get_instructor_id
    get_instructor.subj_id = get_sub_id
    get_instructor.save()
    return redirect('edit_instructor_per_section', section=section)

  return render(
    request,
    'main/edit_instructor_per_id.html',
    {'instructor': instance,
     'instructors': instructors,
     'subjects': subjects,
     'section':section}
  )

@login_required(login_url="/login")
@authenticated_user_admin
def delete_instructor_per_id(request, id, section):
  intructor_per_sub = EvaluatedDetails.objects.get(id=id)
  intructor_per_sub.delete()
  
  return redirect('edit_instructor_per_section', section=section)

@login_required(login_url="/login")
@authenticated_user_admin
def add_instructor(request, section):
  instructors = Instructor.objects.all()
  subjects = Subjects.objects.all()

  if request.method == "POST":
    add_instructor_per_sub = EvaluatedDetails(
      section = section,
      subj_id = int(request.POST['subject']),
      inst_id = int(request.POST['instructor'])
    )
    add_instructor_per_sub.save()
    return redirect('edit_instructor_per_section', section=section)

  return render(
    request,
    'main/add_instructor.html',
    { 'instructors': instructors,
      'subjects': subjects,
      'section': section }
  )

#Settings
def settings(request):
  return render(
    request,
    'main/settings.html'
  )

def evaluationstatus(request):
  pass
