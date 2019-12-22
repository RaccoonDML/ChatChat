from django.shortcuts import render, HttpResponse,HttpResponse,HttpResponseRedirect, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from chat import models
import json
import time
import queue
import os
from django.views.decorators.csrf import csrf_exempt

GLOBAL_MSG_QUEUES={

}

# Create your views here.
def index(request):
    return render(request, 'chat/index.html')


def user_login_view(request):
    if request.method == 'POST':
        user = authenticate(username = request.POST.get('username'),
                            password = request.POST.get('password'))
        if user is not None:
            login(request,user)
            return redirect('/chat')
        else:
            login_err = 'Wrong username or password'
            return render(request,'chat/login.html',{'login_err':login_err})
    else:
        if request.user.is_authenticated:
            return redirect('/chat')
        else:
            return render(request,'chat/login.html')


def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'chat/dashboard.html')
    else:
        return redirect('/login/')

@csrf_exempt
def send_msg(request):
    if request.user.is_authenticated:
        msg_data = request.POST.get('data')
        if msg_data:
            msg_data = json.loads(msg_data)
            msg_data['timestamp'] = time.time()
            if msg_data['type'] == 'single':
                if not GLOBAL_MSG_QUEUES.get(int(msg_data['to'])):
                    GLOBAL_MSG_QUEUES[int(msg_data['to'])] = queue.Queue()
                GLOBAL_MSG_QUEUES[int(msg_data['to'])].put(msg_data)
            else:
                group_obj = models.Group.objects.get(id = int(msg_data['to']))

                for member in group_obj.members.select_related():
                    if not GLOBAL_MSG_QUEUES.get(member.id):
                        GLOBAL_MSG_QUEUES[member.id] = queue.Queue()
                    if member.id != request.user.userprofile.id:
                        GLOBAL_MSG_QUEUES[member.id].put(msg_data)
        return HttpResponse("---msg recevied---")
    else:
        return redirect('/login/')

@login_required
def get_new_msgs(request):
    # 先判断自己有没有queue,如果是新用户第一次登录就是没有queue
    if request.user.userprofile.id not in GLOBAL_MSG_QUEUES:
        print("no queue for user[%s]"%request.user.userprofile.id,request.user)
        GLOBAL_MSG_QUEUES[request.user.userprofile.id] = queue.Queue() #创建一个queue
    msg_count = GLOBAL_MSG_QUEUES[request.user.userprofile.id].qsize() #获取queue的大小
    q_obj = GLOBAL_MSG_QUEUES[request.user.userprofile.id]
    msg_list = []
    if msg_count > 0:
        for msg in range(msg_count):
            msg_list.append(q_obj.get()) #q_obj.get()不需要指定参数,会找最旧的那一条
        print("new msgs:",msg_list)
    else:#没消息,要挂起
        print(GLOBAL_MSG_QUEUES)
        try:
            msg_list.append(q_obj.get(timeout=1)) #如果有消息,则立刻加入到msg_list列表,如果超时进入except
        except queue.Empty:     #如果列表为空,打印下面消息
            print("\033[41;1mno msg for [%s][%s]\033[0m"%(request.user.userprofile.id,request.user))
    return HttpResponse(json.dumps(msg_list))

@login_required
def file_upload(request):
    file_obj = request.FILES.get('file')
    new_file_name = "uploads/%s" % file_obj.name
    with open(new_file_name,"wb+") as new_file_obj:
        for chunk in file_obj.chunks():
            new_file_obj.write(chunk)

    print(file_obj)
    return HttpResponse('--upload success--')


def user_logout_view(request):
    logout(request)
    return redirect('/login')


@login_required
@csrf_exempt
def vedio_chat(request):
    if request.method == 'POST':
        id = request.POST['contact_id']
        type = request.POST['contact_type']
        if len(id) == 0:
            id = request.user.id
            type = 'single'
        return render(request, 'chat/vedio_chat.html', {'contact_id':id, 'contact_type': type})
    else:
        return render(request, 'chat/vedio_chat.html')
    # return render(request, 'chat/vedio_chat.html')


def download(request, name):
    filepath = 'uploads/' + name
    if os.path.exists(filepath):
        print(filepath)
        file = open(filepath, 'rb')
        response = HttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
        response['Content-Disposition'] = 'attachment;filename="%s"' % name
        return response
    else:
        return HttpResponse("Sorry but Not Found the File")
