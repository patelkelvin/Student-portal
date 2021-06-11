from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import AdminData, StudentData, Resources, Clubs, Event, Placements


# Create your views here.

def login_view(request):
    if request.method == "GET":
        try:
            if request.session['user']:
                return HttpResponseRedirect(reverse("student:index"))
            else:
                return render(request, "student/login.html")
        except:
            return render(request, "student/login.html")

    if request.method == "POST":
        user = request.POST["username"]
        enroll = request.POST["enroll_no"]
        passwd = request.POST["password"]
        role = request.POST["role"]
        dept = request.POST["dept_id"]

        if role == "admin":
            try:
                AdminData.objects.get(
                    username=user, password=passwd, dept_id=dept, enroll_no=enroll)
                request.session['user'] = enroll
                request.session['admin'] = True
                return HttpResponseRedirect(reverse("student:index"))
            except:
                return render(request, "student/login.html", {
                    "message": "Invalid Credentials"
                })
        elif role == "student":
            try:
                StudentData.objects.get(
                    username=user, password=passwd, dept_id=dept, enroll_no=enroll)
                request.session['user'] = enroll
                request.session['admin'] = False
                return HttpResponseRedirect(reverse("student:index"))
            except:
                return render(request, "student/login.html", {
                    "messageAlert": "Invalid Credentials"
                })
    return render(request, "student/login.html")


def index(request):
    if request.method == "GET":
        try:
            if request.session['user']:
                flag = request.session['admin']
                if flag == True:
                    return render(request, "faculty/index.html")
                else:
                    return render(request, "student/index.html")
        except:
            return HttpResponseRedirect(reverse("student:login"))


def logout_view(request):
    try:
        del request.session['user']
        del request.session['admin']
        return HttpResponseRedirect(reverse("student:login"))
    except:
        return HttpResponseRedirect(reverse("student:login"))


def templates(request, search):
    if request.method == "GET":
        try:
            if request.session['user']:
                user = request.session['user']
                flag = request.session['admin']
                resources = Resources.objects.all()
                clubs = Clubs.objects.all()
                placements = Placements.objects.all()
                event = Event.objects.all()
                if flag == True:
                    data = AdminData.objects.get(enroll_no=user)
                    return render(request, f"faculty/{search}.html", {
                        "data": data,
                        "resources" : resources,
                        'clubs' : clubs,
                        'placements' : placements,
                        "event" : event
                    })
                else:
                    data = StudentData.objects.get(enroll_no=user)
                    return render(request, f"student/{search}.html", {
                        "data": data,
                        "resources" : resources,
                        'clubs' : clubs,
                        'placements' : placements,
                        "event" : event
                    })
        except:
            return HttpResponseRedirect(reverse("student:login"))
    if request.method == "POST":
        try:
            if request.session['user']:
                user = request.POST["username"]
                enroll = request.POST["enroll_no"]
                passwd = request.POST["password"]
                dept = request.POST["dept_id"]
                role = request.POST["role"]
                if role == "admin":
                    try:
                        form = AdminData(
                            username=user, password=passwd, dept_id=dept, enroll_no=enroll)
                        form.save()
                        return render(request, "faculty/register.html", {
                            "messageSuccess": "Admin Created"
                        })
                    except:
                        return render(request, "faculty/register.html", {
                            "messageAlert": "User Already Exist"
                        })
                elif role == "student":
                    
                    try:
                        form = StudentData(
                            username=user, password=passwd, dept_id=dept,enroll_no=enroll)
                        form.save()
                        return render(request, "faculty/register.html", {
                            "messageSuccess": "User Created"
                        })
                    except:
                        return render(request, "faculty/register.html", {
                            "messageAlert": "User Already Exist"
                        })
        except:
            HttpResponse(500)
            return render(request, "student/login.html", {
                    "message": "Please Login Again"
                })

def setting(request):
    if request.method == "POST":
        try:
            if request.session['user']:
                role = request.session['admin']
                enroll = request.session['user']
                passwd = request.POST['currPassword']
                newPasswd = request.POST['newPassword']

                if role:
                    try:
                        form = AdminData.objects.get(enroll_no=enroll, password =passwd)
                        form.password = newPasswd
                        form.save()
                        HttpResponseRedirect("/admin/settings")
                        return render(request, "faculty/settings.html", {
                            "messageSuccess": "Password Updated"
                        })
                    except:
                        HttpResponseRedirect("/admin/settings")
                        return render(request, "faculty/settings.html", {
                            "messageAlert": "Wrong Password"
                        })
                else:
                    try:
                        form = StudentData.objects.get(enroll_no=enroll,password=passwd)
                        form.password = newPasswd
                        form.save()

                        HttpResponseRedirect("/app/settings")
                        return render(request, "student/settings.html", {
                            "messageSuccess": "Password Updated"
                        })
                    except:
                        HttpResponseRedirect("/app/settings")
                        return render(request, "student/settings.html", {
                            "messageAlert": "Wrong Password"
                        })
        except:
            HttpResponse(500)
            return render(request, "student/login.html", {
                    "message": "Please Login Again"
                })


def handleFileUpload(request, fileName):
    if request.method == "POST":
        title = request.POST["title"]
        details = request.POST["details"]
        try:
            resource = request.FILES["resource"]
            fs = FileSystemStorage()
            filename = fs.save(resource.name, resource)
            url = fs.url(filename)
        except:
            resource = None
            url = None
            
        if fileName == "resources":
            dept = request.POST["dept_id"]
            type = request.POST["type"]
            form = Resources(title=title, details=details, type=type, dept_id=dept, file_name=resource, file_link=url)
            form.save()

        # Placements
        if fileName == 'placement':
            link = request.POST['applyForm']
            form = Placements(company=title, details=details, document=resource, documentUrl = url , form_link=link)
            form.save()

        # Clubs
        if fileName == "clubs":
            form = Clubs(title=title, details=details, file_name=resource.name, file_link=url)
            form.save()
        
        # Events 
        if fileName == "event":
            form = Event(title=title, details=details, file_name=resource.name, file_link=url)
            form.save()
        
        return HttpResponseRedirect(f"/admin/{fileName}")
    else:
        return HttpResponse(400) 
