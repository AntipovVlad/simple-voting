import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .models import *

const = '/traveler'

def index(request):
    context = {}
    context['user_fv'] = User.objects.filter().count()
    context['vote_fv'] = Voting.objects.filter().count()
    context['mega_fv'] = MegaData.objects.filter().count()

    return render(request, 'index.html', context)

def traveler(request):
    return render(request, 'traveler.html')

def statistics(request, num):
    context = {}
    context['answers'] = []

    count = Option.objects.filter(voting=num).count()
    persons = MegaData.objects.filter(question=num).count()

    l = list(Option.objects.filter(voting=num).values_list('id'))

    for i in range(count):
        answer = str(l[i])[1:-2]
        q = Option.objects.filter(id=answer).values_list('text')
        n = MegaData.objects.filter(answer=answer, question=num).count()

        context['answers'].append((str(list(q)[0])[2:-3], n, int(n / persons * 100)))

    return context


def exit(request):
    logout(request)

    return redirect('/')


def check(request, q):
    if MegaData.objects.filter(user=request.user.id, question=q):
        return True
    else:
        return False


@login_required
def createVoting(request):
    if request.method == "GET":
        r = render(request, 'create_voting.html')

        return r
    elif request.method == "POST":
        q = Voting()

        q.question = request.POST.get('question')
        q.date = datetime.datetime.now()
        q.user_id = request.user.id
        q.vote_type = request.POST.get('type')

        count = int(request.POST.get('count'))
        q.save()

        for i in range(1, count + 1):
            o = Option()
            o.text = request.POST.get('option' + str(i))
            o.voting = str(Voting.objects.filter(pk=Voting.objects.filter().count()).values_list('id')[0])[1:-2]

            o.save()

        return success(request)


def showVoting(request, number):
    if request.method == "GET":
        if check(request, number):
            return show_statistic(request, number)

        v_t = str(list(Voting.objects.filter(pk=number).values_list('vote_type'))[0])[1:-2]

        context = {}

        context['id'] = number
        context['question'] = str(Voting.objects.filter(pk=number).values_list('question')[0])[2:-3]
        context['voting'] = list(Option.objects.filter(voting=str(number)).values_list('id', 'text', 'voting'))
        context['count'] = len(context['voting'])

        context['auth'] = Voting.objects.filter(id=number).values_list('question')
        u = str(list(Voting.objects.filter(id=number).values_list('user_id'))[0])[1:-2]
        context['author'] = str(list(User.objects.filter(id=int(u)).values_list('username'))[0])[2:-3]

        x = str(list(Voting.objects.filter(id=number).values_list('date'))[0])[1:-4].split('datetime.datetime(')[
            1].split(',')
        x = "Creation date: " + x[0] + '-' + x[1][1:] + '-' + x[2][1:] + ' ' + x[3][1:] + ':' + x[4][1:] + ':' + x[5][
                                                                                                                 1:]
        context['date'] = x

        context['current_num'] = number
        context['start_id'] = context['voting'][0][0]
        if v_t == '1':
            return render(request, 'showvoting.html', context)
        elif v_t == '2':
            return render(request, 'showvoting2.html', context)
    elif request.method == "POST":
        v = request.POST.get("chosen_values")

        if v != None and v != [] and v != "" :
            v_t = str(list(Voting.objects.filter(pk=number).values_list('vote_type'))[0])[1:-2]

            if v_t == '1':
                md = MegaData()
                md.question = number
                md.answer = int(v)
                md.user = int(request.user.id)

                count = int(str(Voting.objects.filter(pk=number).values_list('count')[0])[2:-3]) + 1
                Voting.objects.filter(pk=number).update(count=count)

                md.save()
            elif v_t == '2':
                c_v = request.POST.get('chosen_values').split()
                for i in c_v:
                    md = MegaData()
                    md.question = number
                    md.answer = int(i)
                    md.user = int(request.user.id)

                    md.save()

                count = int(str(Voting.objects.filter(pk=number).values_list('count')[0])[2:-3]) + 1
                Voting.objects.filter(pk=number).update(count=count)
                count = int(str(list(UserData.objects.filter(pk=int(request.user.id)).values_list('answered'))[0])[1:-2]) + 1
                UserData.objects.filter(pk=number).update(answered=count)

            return redirect("/voting/" + str(number))
        else:
            return redirect("/voting/" + str(number))


def show_statistic(request, num):
    context = statistics(request, num)

    context['question'] = str(list(Voting.objects.filter(id=num).values_list('question'))[0])[2:-3]
    u = str(list(Voting.objects.filter(id=num).values_list('user_id'))[0])[1:-2]
    context['author'] = str(list(User.objects.filter(id = int(u)).values_list('username'))[0])[2:-3]

    x = str(list(Voting.objects.filter(id=num).values_list('date'))[0])[1:-4].split('datetime.datetime(')[1].split(',')
    x = "Creation date: " + x[0] + '-' + x[1][1:] + '-' + x[2][1:] + ' ' + x[3][1:] + ':' + x[4][1:] + ':' + x[5][1:]
    context['date'] = x

    return render(request, 'show_statistic.html', context)


def votingList(request):
    context = {}

    q = list(Voting.objects.values_list('question', 'id', 'date', 'user_id', 'count'))
    context['data'] = []
    logins = []

    for i in q:
        logins.append(str(list(User.objects.filter(pk=i[3]).values_list('username'))[0])[2:-3])
    
    for i in range(len(q)):
        count = str(q[i][4])
        if count == "none":
            count = '0'
        context['data'].append((str(q[i][0]), str(q[i][1]), str(logins[i]), str(q[i][2]).split('.')[0], str(q[i][3]), count))

    context['data'].reverse()

    return render(request, 'voting_list.html', context)


def registration(request):
    context = {}
    form = RegisterForm()
    context['form'] = form

    if request.method == "GET":
        return render(request, 'registration.html', context)
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.data['email']
            user.save()

            u = UserData()
            u.bio = ""
            u.pic_url = "../static/img/icon.png"
            u.save()

            return redirect("/login/")
        else:
            return HttpResponse("Некорректные данные!")


def auth(request):
    context = {}
    if request.method == "GET":
        form = AuthForm()
        context['form'] = form
        return render(request, 'login.html', context)
    elif request.method == "POST":
        form = AuthForm(request.POST)

        if form.is_valid():
            username = form.data['login']
            password = form.data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                return HttpResponse("Некорректные данные!")
        else:
            return render(request, 'login.html', context)


@login_required
def profile(request, login):
    cur_id = int(str(list(User.objects.filter(username=login).values_list('id'))[0])[1:-2])

    if request.method == "GET":
        context = {}

        if cur_id == int(request.user.id):
            context['me'] = True
        else:
            context['me'] = False

        context['username'] = str(list(User.objects.filter(pk=cur_id).values_list('username'))[0])[2:-3]
        s = list(UserData.objects.filter(pk=cur_id).values_list('bio'))
        if len(s) != 0:
            context['bio'] = str(s[0])[2:-3]
        else:
            context['bio'] = "There is nothing about me."
        s = list(User.objects.filter(pk=cur_id).values_list('first_name'))

        if len(s) != 0:
            context['first_name'] = str(s[0])[2:-3]
        else:
            context['first_name'] = "None"

        s = list(User.objects.filter(pk=cur_id).values_list('last_name'))
        if len(s) != 0:
            context['last_name'] = str(s[0])[2:-3]
        else:
            context['last_name'] = "None"

        x = str(list(User.objects.filter(pk=cur_id).values_list('date_joined'))[0])[1:-4].split('datetime.datetime(')[1].split(',')
        x = "Joined: " + x[0] + '-' + x[1][1:] + '-' + x[2][1:]
        context['joined'] = x

        context['count'] = Voting.objects.filter(user_id=cur_id).count()

        s = list(UserData.objects.filter(pk=cur_id).values_list('answered'))
        if len(s) != 0:
            context['answered'] = str(s[0])[1:-2]
        else:
            context['answered'] = 0


        #ПОКАЗ СВОИХ ОПРОСОВ
        context["your_voting"] = []
        your_q_id = list(Voting.objects.filter(user_id=cur_id).values_list('id'))
        your_q_nane = list(Voting.objects.filter(user_id=cur_id).values_list('question'))

        for i in range(len(your_q_id)):
            context["your_voting"].append((str(your_q_id[i])[1:-2], str(your_q_nane[i])[2:-3]))
        #ПОКАЗ СВОИХ ОПРОСОВ


        #ПОКАЗ НЕ СВОИХ ОПРОСОВ
        context["all_voting"] = []

        all_q_id = []
        q_id_tmp = list(MegaData.objects.filter(user=cur_id).values_list('question'))
        for i in range(len(q_id_tmp)):
            all_q_id.append(int(str(q_id_tmp[i])[1:-2]))
        all_q_id = list(set(all_q_id))


        all_q_nane = []
        for i in range(len(all_q_id)):
            all_q_nane.append(str(list(Voting.objects.filter(id=int(all_q_id[i])).values_list('question'))[0])[2:-3])


        for i in range(len(all_q_id)):
            context["all_voting"].append((all_q_id[i], all_q_nane[i]))
        #ПОКАЗ НЕ СВОИХ ОПРОСОВ

        context["casted_votes"] = len(all_q_id)

        #ССЫЛКА НА ФОТО
        context["pic_url"] = str(list(UserData.objects.filter(pk=cur_id).values_list('pic_url')))[3:-4]

        return render(request, 'profile.html', context)
    elif request.method == "POST":
        User.objects.filter(pk=int(request.user.id)).update(first_name=request.POST.get('Name'), last_name=request.POST.get('Surname'))
        UserData.objects.filter(pk=int(request.user.id)).update(bio=request.POST.get('Bio'))
        if request.POST.get('pic_url') != None and request.POST.get('pic_url') != "":
            UserData.objects.filter(pk=int(request.user.id)).update(pic_url=request.POST.get('pic_url'))

        return redirect("/profile/" + login)

def success(request):
    return render(request, 'success.html')
