from pyexpat.errors import messages
from django.shortcuts import redirect, render
from .models import * 
from django.db.models import Q, Count

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
        blood_requests = RequestBlood.objects.create(name=name, email=email, phone=phone, state=state, city=city, address=address, blood_group=BloodGroup.objects.get(name=blood_group), date=date)
        blood_requests.save()
        return redirect("index")
    return render(request, "request_blood.html")


def see_all_request(request):
    requests = RequestBlood.objects.all()
    return render(request, "see_all_request.html", {'requests':requests})

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
 
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')
 
        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        donors = Donor.objects.create(donor=user, phone=phone, state=state, city=city, address=address, gender=gender, blood_group=BloodGroup.objects.get(name=blood_group), date_of_birth=date, image=image)
        user.save()
        donors.save()
        return render(request, "index.html")
    return render(request, "become_donor.html")

def home (request):
     return render(request, "home.html")


    
    