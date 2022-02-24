from pyexpat.errors import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import * 
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import authenticate

# Create your views here.
def index(request):
    all_group = BloodGroup.objects.annotate(total=Count('donor'))
    print(all_group)
    return render(request, "index.html", {'all_group':all_group})

def request_blood(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        units = request.POST['units']
        blood_requests = RequestBlood.objects.create(name=name, email=email, phone=phone, state=state, city=city, address=address, blood_group=BloodGroup.objects.get(name=blood_group), date=date, units=units,)
        blood_requests.save()
        # return redirect("index")
    return render(request, "request_blood.html")


def see_all_request(request):
    requests = RequestBlood.objects.all()
    if request.method == "POST":
        if 'update_id' in request.POST:
            print(request.POST)
            user_id=request.POST.get('update_id')
            user = RequestBlood.objects.get(id=user_id)
            print(user)
            print('Update: User ', request.POST.get('update_id'))
            return render(request, "see_all_request.html", {'requests':requests, 'user':user})
        
        if 'delete_id' in request.POST:
            print(request.POST)
            user_id=request.POST.get('delete_id')
            user = RequestBlood.objects.get(id=user_id)
            print('delete', user)
            user.delete()
            print('Update: User ', request.POST.get('delete_id'))
            
            requests = RequestBlood.objects.all()
            return render(request, "see_all_request.html", {'requests':requests})
        
        if 'update' in request.POST:
            user_id=request.POST.get('update')
            user = RequestBlood.objects.get(id=user_id)
            print(user)
            print(request.POST)
            user.name = request.POST['name']
            user.email = request.POST['email']
            user.phone = request.POST['phone']
            user.state = request.POST['state']
            user.city = request.POST['city']
            user.address = request.POST['address']
            user.blood_group = BloodGroup.objects.get(name=request.POST['blood_group'])
            user.date = request.POST['date']
            user.units = request.POST['units']
            user.save()
            
            requests = RequestBlood.objects.all()
            return render(request, "see_all_request.html", {'requests':requests})
        print(request.POST)    
        
        
    return render(request, "see_all_request.html", {'requests':requests})

def get_request_data(request):
    print(request.GET)
    user_id=request.GET.get('request_id')
    user = RequestBlood.objects.get(id=user_id)
    print(user)
    print('Update: User ', request.GET.get('request_id'))
    
    data =  {
        'success' : True,
        'request' : {
            'name' : user.name,
            'email' : user.email,
            'phone' : user.phone,
            'state' : user.state,
            'city' : user.city,
            'address' : user.address,
            'blood_group' : user.blood_group.name,
            'date' : user.date,
            'units' : user.units,
        }
    }
    return JsonResponse(data)

def become_donor(request):
    if request.method=="POST":   
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        gender = request.POST['gender']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        image = request.FILES['image']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
 
        # if password != confirm_password:
        #     messages.error(request, "Passwords do not match.")
        #     return redirect('/become_donor')
        print('registered')
        # user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        # donors = Donor.objects.create(donor=user, phone=phone, state=state, city=city, address=address, gender=gender, blood_group=BloodGroup.objects.get(name=blood_group), date_of_birth=date, image=image)
        # user.save()
        # donors.save()
        return render(request, "become_donor.html")
    return render(request, "become_donor.html")

def home (request):
     return render(request, "home.html")
 
def about (request):
     return render(request, "about.html")
 
def blood_group (request):
     return render(request, "blood_group.html")
 
 
def login_user (request):
    if request.user.is_authenticated:
        print('Already login')
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login_user(request, user)
                print('success')
                return redirect("/profile")
            else:
                thank = True
                print("Rejected")
                return render(request, "login_user.html", {"thank":thank})
    return render(request, "login_user.html")
    # return render(request, "login_user.html")
 
 



    
    