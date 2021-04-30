from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from datetime import datetime
from datetime import timedelta
import bcrypt
import re

class UserManager(models.Manager):

    # form validation for user login
    def user_login_validator(self,post_data):

        EMAIL_REGEX = re.compile('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')

        errors = {}
        check_password = True
        login_email = ''
        password = ''

        if 'login_email' in post_data:
            login_email = post_data['login_email']
            if not EMAIL_REGEX.match(login_email):
                errors["login_email"] = "Invalid email address entered"
        else:
            check_password = False
            errors['login_email'] = 'No email address entered. Please enter a password.'

        if 'login_password' in post_data:
            password = post_data['login_password']
            if (len(password)<8):
                errors['login_password'] = "Invalid password entered, must be at least 8 characters"
        else:
            check_password = False
            errors['login_password'] = 'No password entered. Please enter a password.'

        
        if (check_password):
            # if we got here the email and password were in a valid format
            try:
                user = User.objects.get(email=login_email)

                if not bcrypt.checkpw(password.encode(), user.password.encode()):
                    # passwords did not match!
                    errors['login_password'] = "The login credentials not found"
            except ObjectDoesNotExist:
                print("user not found")
                errors["login_email"] = "The login credentials not found"

        return errors


    # form validation for user account creation
    def create_user_data_validator(self,post_data):

        DATE_REGEX  = re.compile('(\d{4})[/.-](\d{2})[/.-](\d{2})$')
        EMAIL_REGEX = re.compile('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        CHARS_ONLY  = re.compile(r'^[a-zA-Z]+$')
        NUMS_ONLY   = re.compile(r'^[a-z0-9]+$')

        errors = {}
        
        # fields
        first_name = post_data['first_name']
        last_name  = post_data['last_name']
        city       = post_data['city']
        state      = post_data['state']
        zip        = post_data['zip']

        if (len(first_name) < 3):
            errors["first_name"] = "First name should be at least 2 characters"

        if (len(last_name) < 3):
            errors["last_name"] = "Last name should be at least 2 characters"
        if (not CHARS_ONLY.match(first_name)) or (not CHARS_ONLY.match(last_name)):
            errors["first_name"] = "Names should contain characters only"

        if (len(city) < 3):
            errors['city'] = "City needs to be at least 3 characters"

        if (len(state) < 2):
            errors['state'] = "Please enter state"

        if ((len(zip) < 5) or (not NUMS_ONLY.match(zip))):
            errors['zip'] = "Please enter a valid zip code"

        # email
        if ('email' in post_data):
            email_in = post_data['email']
            if not EMAIL_REGEX.match(email_in):
                errors["email"] = "Invalid email address entered"
            else:
                # format was valid .. now we check to see if value already exists ..
                # if inserting/updating to new value check might not 
                # need to be here .. but in the views logic
                email_exists = User.objects.filter(email=email_in).count()
                if email_exists > 0:
                    errors['email'] = "Email already exists in system, use another one"
        else:
            # we should not get here due to front end validation .. but check anyways
            errors['email'] = 'No email address entered'

        password = post_data['password']
        confirm_password = post_data['confirm_password']

        if (len(password)>8) and (len(confirm_password)>8):
            
            # both were entered .. check to see if they match
            if (password != confirm_password):
                errors['password'] = 'Password and confirmation passwords need to match'
        else:
            errors['password'] = 'Password and confirmation passwords need to be at least 8 characters long'

        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name  = models.CharField(max_length=255)
    email      = models.CharField(max_length=255)
    password   = models.CharField(max_length=255)
    city       = models.CharField(max_length=255)
    state      = models.CharField(max_length=255)
    zip        = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # favorites = Video[] .. a user may have many favorites
    # rating = Video[] .. a User may rate many different Videos
    # messages = Message[] .. a User may have many Messages
    # comments = Comment[] .. a User may have many Comments
    # books_uploaded = Book[] .. a User may upload books
    # liked_books = Book[] .. a User may like any number of different Books
    # adding manager to handle validation
    objects = UserManager()

class Message(models.Model):
    message = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE) # a User can have many messages
    # comments = Comment[] .. a Message may have many Comments

class Comment(models.Model):
    comment = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE) # a User can have many comments
    message = models.ForeignKey(Message, related_name='comments', on_delete=models.CASCADE) # a Message can have many comments

class Video(models.Model):
    video_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    is_favorite = models.ManyToManyField(User, related_name="is_favorite") # a User can have many favorite videos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# a User may rate many different videos, a video may be rated by many different Users
class VideoRating(models.Model):
    video = models.ForeignKey(Video, related_name='video', on_delete=models.CASCADE) # a rating requires a video
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE) # a rating requires a user
    rating = models.PositiveSmallIntegerField(default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)