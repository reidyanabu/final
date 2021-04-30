from django.shortcuts import render, redirect
from .models import User, Message, Comment, Video, VideoRating
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse
import bcrypt
from django.core.mail import send_mail

def show_login(request):
    # remove previous session .. this is my prerogative :)
    if 'user_first_name' in request.session:
        del request.session['user_first_name']
        del request.session['user_id']

    return render(request, "login.html")


def register_user(request):

    # validate users input
    errors = User.objects.create_user_data_validator(request.POST)

    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        return redirect('/')
    else:
        post_data = request.POST
        # register the new user
        first_name_in = post_data['first_name']
        last_name_in  = post_data['last_name']
        email_in      = post_data['email']
       # birthday_in   = datetime.strptime(post_data['birthday'], "%Y-%m-%d")
        password_in   = post_data['password']
        pw_hash       = bcrypt.hashpw(password_in.encode(), bcrypt.gensalt()).decode() 
        # we use bcryot to generate a salt, and use it to bcrypt hash the password, which is stored in the db
        
        #user = User.objects.create(first_name=first_name_in,last_name=last_name_in,email=email_in,birthday=birthday_in,password=pw_hash)
        user = User.objects.create(first_name=first_name_in,last_name=last_name_in,email=email_in,password=pw_hash)

        # create a user session and place user in it
        request.session['user_first_name'] = user.first_name
        request.session['user_id'] = user.id
    
        return redirect("/home")


def process_login(request):

    errors = User.objects.user_login_validator(request.POST)

    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        return redirect('/')
    
    # no validation errors
    user = User.objects.get(email=request.POST['login_email'])
    request.session['user_first_name'] = user.first_name
    request.session['user_id'] = user.id

    return redirect("/home")


def show_success(request):
    # get the user from the session and pass to view
    if 'user_id' in request.session:
        
        return render(request, "home.html")
    else:
        # not logged in
        return redirect("/")


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_first_name']
        del request.session['user_id']
    return redirect("/")

# AJAX call which takes an email string and compares it to values in the database and returns a JsonResponse object
def email_exists(request):

    email = request.GET['email']

    email_exists = User.objects.filter(email=email).exists()
    data = {
        'email_exists': email_exists
    }
    return JsonResponse(data)

def wall(request):
    if 'user_id' not in request.session:
        return redirect("/")
    # get user
    #user_id = request.session['user_id']

    # get messages
    messages = Message.objects.all().order_by('-created_at')

    context = {
        "messages": messages
    }

    return render(request, "wall.html", context)


def post_message(request):

    message_txt = request.POST['message']
    if len(message_txt) > 0:
        # get user
        user_id = int(request.session['user_id'])
        user    = User.objects.get(id=user_id)
    
        # create message for given user with entered text
        message = Message.objects.create(message=message_txt,user=user)

    return redirect('/wall')


def post_comment(request):

    comment_txt = request.POST['comment']
    if len(comment_txt) > 0:
        # get user and message
        user_id    = int(request.session['user_id'])
        message_id = int(request.POST['message_id'])

        user       = User.objects.get(id=user_id)
        message    = Message.objects.get(id=message_id)

        # create comment for given user with entered text
        comment = Comment.objects.create(comment=comment_txt,user=user,message=message)

    return redirect('/wall')

def delete_message(request):
    # get message
    message_id = int(request.GET['message_id'])
    Message.objects.get(id=message_id).delete()

    return redirect('/wall')

def delete_comment(request):
    # get comment
    comment_id = int(request.GET['comment_id'])
    # delete it
    Comment.objects.get(id=comment_id).delete()

    return redirect('/wall')

def weather(request):

    return render(request,'weather.html')

def youtube(request):

    return render(request, "youtube.html")

def get_video(video_id_in):
    video_id = video_id_in
    try:
        video = Video.objects.get(video_id=video_id)
    except Video.DoesNotExist:
        # does not exist yet, just use defaults
        video = Video.objects.create(video_id=video_id,title='',desc='',img_url='')
    return video

def get_video_pref_info(request):
    print("Getting video prefs ..")
    # get the user
    user_id = int(request.session['user_id'])
    user    = User.objects.get(id=user_id)
    print("Got user: " + user.first_name)
    # get selected video id
    video_id = request.GET['video_id']
    print("Got video, id = " + video_id)
    # check to see if the video is a favorite
    video = get_video(video_id)
    in_favorites = Video.objects.filter(is_favorite__id=user.id).exists()
    # try:  
    #     u = video.is_favorite.get(is_favorite=user.id)
    #     in_favorites = True
    # except User.DoesNotExist:
    #     in_favorites = False
    print(f'get .. in favorites? = {in_favorites}')

    # get rating if it exists for this video/user combination
    try:
        rated_video = VideoRating.objects.get(video=video,user=user)
    except VideoRating.DoesNotExist:
        # does not exist yet, create default '0'
        print("Could not find rating for video .. creating one")
        rated_video = VideoRating.objects.create(user=user,video=video,rating=0)
    rating = rated_video.rating
    print(f"Returning is_favorite = {in_favorites}, rating = {rating}")
    data = {
        'is_favorite' : in_favorites,
        'rating' : rating
    }

    return JsonResponse(data)

def add_favorite_video(request):
    # get the user
    user_id = int(request.session['user_id'])
    user    = User.objects.get(id=user_id)
    # get selected video id
    video_id = request.GET['video_id']

    # check to see if the video is a favorite
    video = get_video(video_id)
    

    #if (not video.is_favorite.filter(is_favorite=user_id).exists()):
    if (not Video.objects.filter(is_favorite__id=user.id).exists()):
        print("adding as favorite")
        video.is_favorite.add(user)
        video.save()





        print("test ..")
        exists = Video.objects.filter(is_favorite__id=user.id).exists()

        print(f'in favorites? = {exists}')




    data = {
        'is_favorite' : True
    }

    return JsonResponse(data)

def delete_favorite_video(request):
    # get the user
    user_id = int(request.session['user_id'])
    user    = User.objects.get(id=user_id)
    # get selected video id
    video_id = request.GET['video_id']

    # check to see if the video is a favorite
    video = get_video(video_id)

    print("in remove!!!!!")
    in_favorites = Video.objects.filter(is_favorite__id=user.id).exists()
    # try:  
    #     u = video.is_favorite.get(is_favorite=user.id)
    #     in_favorites = True
    # except User.DoesNotExist:
    #     in_favorites = False
    # print(f'in favorites? = {in_favorites}')

    if (in_favorites):
        print("removing as favorite")
        video.is_favorite.remove(user)
        video.save()

    data = {
        'is_favorite' : False
    }

    return JsonResponse(data)


def update_video_rating(request):
    # get the user
    user_id = int(request.session['user_id'])
    user    = User.objects.get(id=user_id)
    # get selected video id
    video_id = request.GET['video_id']
    video = get_video(video_id)
    # get the chosen rating
    rating = int(request.GET['rating'])
    
    print(f"got video_id={video_id}, rating={rating}, user_id={user_id}")
    # get rating if it exists for this video/user combination
    try:
        rated_video = VideoRating.objects.get(video=video,user=user)
        rated_video.rating = rating
        rated_video.save()

    except VideoRating.DoesNotExist:
        # does not exist yet, create it
        print("Creating new video rating")
        rated_video = VideoRating.objects.create(user=user,video=video,rating=rating)

    data = {
        'rating' : rated_video.rating
    }

    return JsonResponse(data)
