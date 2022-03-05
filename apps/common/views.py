from pyexpat.errors import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import * 
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.core.mail import EmailMessage
import threading

# Create your views here.
def index(request):
    all_group = BloodGroup.objects.annotate(total=Count('donor'))
    print(all_group)
    return render(request, "index.html", {'all_group':all_group})

def request_blood(request):
    if request.user.is_authenticated:
        username = request.user.username
        loggedIn = True
    else:
        loggedIn = False
        username = ''
           
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
    return render(request, "request_blood.html", {'loggedIn' : loggedIn, 'username' : username})


def see_all_request(request):
    requests = RequestBlood.objects.filter(status="pending")
    
    # check date validity
    current_date = datetime.datetime.now().date()
    for req in requests:
        print(req.status)
        request_date = datetime.datetime.strptime(req.date, '%Y-%m-%d').date()
        if request_date < current_date:
            req.status = 'expired'
            req.save()
            print('request expired')
    
    requests = RequestBlood.objects.filter(status="pending")
    expired_requests = RequestBlood.objects.filter(status="expired")
    
    if request.method == "POST":
        if 'update_id' in request.POST:
            print(request.POST)
            user_id=request.POST.get('update_id')
            user = RequestBlood.objects.get(id=user_id)
            print(user)
            print('Update: User ', request.POST.get('update_id'))
            return render(request, "see_all_request.html", {'requests':requests, 'priority_requests':priority_list(requests)})
        
        if 'delete_id' in request.POST:
            print(request.POST)
            user_id=request.POST.get('delete_id')
            user = RequestBlood.objects.get(id=user_id)
            print('delete', user)
            user.delete()
            print('Update: User ', request.POST.get('delete_id'))
            
            requests = RequestBlood.objects.filter(status="pending")
            return render(request, "see_all_request.html", {'requests':requests, 'priority_requests':priority_list(requests), 'expired_requests':expired_requests})
        
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
            
            current_date = datetime.datetime.now().date()
            request_date = datetime.datetime.strptime(user.date, '%Y-%m-%d').date()
            
            print('request_date', request_date)
            if request_date >= current_date:
                if user.status == 'expired':
                    user.status = 'pending'
                    user.save()
            
            if request_date < current_date:
                if user.status == 'pending':
                    user.status = 'expired'
                    user.save()
                
            requests = RequestBlood.objects.filter(status="pending")
            expired_requests = RequestBlood.objects.filter(status="expired")
            return render(request, "see_all_request.html", {'requests':requests, 'priority_requests':priority_list(requests), 'expired_requests':expired_requests})
        
        if 'accept' in request.POST:
            user_id=request.POST.get('accept')
            user = RequestBlood.objects.get(id=user_id)
            user.status = "accepted"
            user.save()
            
            # send Email
            email = user.email
            body = f"""
            Dear {user.name},
            We would like to inform you that your (number) units of blood requested on {user.date} have been approved.
            Please be advised to bring {user.units} valid I.D. to claim the requested at our Philippine Red Cross Blood Bank Department, 2nd floor West Wing near the Billing Department.
            Address: 37 EDSA corner Boni Avenue, Barangka-Ilaya, Mandaluyong City 1550. Contact Us: (02) 8790-2300 local 931/932/935
            Email: communication@redcross.org.ph
            Thank you so much, we hope to see you soon!
            Sincerely,
            Philippine National Red Cross
            """
            subject = 'Request Accepted'
            email=EmailMessage(subject=subject,body=body, to=[email])
            sendEmail(email).start()
            
            requests = RequestBlood.objects.filter(status="pending")
            expired_requests = RequestBlood.objects.filter(status="expired")
            return render(request, "see_all_request.html", {'requests':requests, 'priority_requests':priority_list(requests), 'expired_requests':expired_requests})
        
        print(request.POST)    
        
        
    return render(request, "see_all_request.html", {'requests':requests, 'priority_requests':priority_list(requests), 'expired_requests':expired_requests})

def priority_list(requests):
    priority_list = []
    for req in requests:
        email = req.email
        print(email)
        donors = Donor.objects.filter(donor__email=email)
        if donors:
            print('units of blood donated: ', donors[0].units_blood_donated)
            if donors[0].units_blood_donated >= 1:
                priority_list.append(req)
    
    return priority_list

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

def accepted_request(request):
    requests = RequestBlood.objects.filter(status="accepted")
    
    # check date validity
    current_date = datetime.datetime.now().date()
    for req in requests:
        print(req.status)
        request_date = datetime.datetime.strptime(req.date, '%Y-%m-%d').date()
        if request_date < current_date:
            req.status = 'accept_expired'
            req.save()
            print('request expired')
    
    requests = RequestBlood.objects.filter(status="accepted")
    expired_requests = RequestBlood.objects.filter(status="accept_expired")
    closed_requests = RequestBlood.objects.filter(status="closed")
    
    if request.method == "POST":
        if 'delete_id' in request.POST:
            print(request.POST)
            user_id=request.POST.get('delete_id')
            user = RequestBlood.objects.get(id=user_id)
            print('delete', user)
            user.delete()
            print('Update: User ', request.POST.get('delete_id'))
            
            requests = RequestBlood.objects.filter(status="pending")
            return render(request, "accepted_request.html", {'requests':requests, 'priority_requests':priority_list(requests), 'closed_requests':closed_requests, 'expired_requests':expired_requests})
    
        if 'close' in request.POST:
            user_id=request.POST.get('close')
            user = RequestBlood.objects.get(id=user_id)
            user.status = "closed"
            user.save()
            requests = RequestBlood.objects.filter(status="accepted")
            
            # send Email
            email = user.email
            body = f""" 
            Dear {user.name},
            We would like to inform you that your {user.units} units of blood requested on {user.date} transaction is complete.
            Please be advised that we will now close your request. You may always contact us to assist you with your concerns.
            Address: 37 EDSA corner Boni Avenue, Barangka-Ilaya, Mandaluyong City 1550. Contact Us: (02) 8790-2300 local 931/932/935
            Email: communication@redcross.org.ph
            Thank you so much, have a great day!
            Sincerely,
            Philippine National Red Cross
            """
            subject = 'Transaction Complete'
            email=EmailMessage(subject=subject,body=body, to=[email])
            sendEmail(email).start()
            
            
            expired_requests = RequestBlood.objects.filter(status="accept_expired")
            closed_requests = RequestBlood.objects.filter(status="closed")
            return render(request, "accepted_request.html", {'requests':requests, 'priority_requests':priority_list(requests), 'closed_requests':closed_requests, 'expired_requests':expired_requests})
    
    return render(request, "accepted_request.html", {'requests':requests, 'priority_requests':priority_list(requests), 'closed_requests':closed_requests, 'expired_requests':expired_requests})

def become_donor(request):
    if request.user.is_authenticated:
        username = request.user.username
        loggedIn = True
    else:
        loggedIn = False
        username = ''
        
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
        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        donors = Donor.objects.create(donor=user, phone=phone, state=state, city=city, address=address, gender=gender, blood_group=BloodGroup.objects.get(name=blood_group), date_of_birth=date, image=image)
        user.save()
        donors.save()
        return redirect('/login_user/')
        # return render(request, "become_donor.html")
    return render(request, "become_donor.html",{'loggedIn' : loggedIn, 'username' : username})

def home (request):
    if request.user.is_authenticated:
        username = request.user.username
        loggedIn = True
    else:
        loggedIn = False
        username = ''
    return render(request, "home.html", {'loggedIn' : loggedIn, 'username' : username})
 
def about (request):
    if request.user.is_authenticated:
        username = request.user.username
        loggedIn = True
    else:
        loggedIn = False
        username = ''
    return render(request, "about.html", {'loggedIn' : loggedIn, 'username' : username})
 
def blood_group (request):
    all_group = BloodGroup.objects.annotate(total=Count('donor'))
    if request.user.is_authenticated:
        username = request.user.username
        loggedIn = True
    else:
        loggedIn = False
        username = ''
        
    print(all_group)
    return render(request, "blood_group.html", {'all_group':all_group, 'loggedIn' : loggedIn, 'username' : username})
 
def login_user (request):
    if request.user.is_authenticated:
        print('Already login')
        return redirect("/profile/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                print('success')
                return redirect("/profile/")
            else:
                thank = True
                print("Rejected")
                return render(request, "login_user.html", {"thank":thank})
    return render(request, "login_user.html")
    # return render(request, "login_user.html")
 
def donors_list(request, myid):
    donors = Donor.objects.filter(blood_group_id=myid)
    if request.user.is_authenticated:
        username = request.user.username
        loggedIn = True
    else:
        loggedIn = False
        username = ''
           
    print(myid)
    
    for donor in donors:
        print(type(donor))
    return render(request, "donors_list.html", {"donors" : donors, 'loggedIn' : loggedIn, 'username' : username})

def view_donor_details(request):
    print(request.GET.get('donors_id'))
    
    id = request.GET.get('donors_id')
    donor = Donor.objects.get(id=id)
    
    data =  {
        'success' : True,
        'donor' : {
            'username' : donor.donor.username,
            'full_name' : donor.donor.first_name + ' ' + donor.donor.last_name,
            'email' : donor.donor.email,
            'gender' : donor.gender,
            'date_of_birth' : donor.date_of_birth,
            'phone' : donor.phone,
            'address' : donor.address,
            'city' : donor.city,
            'state' : donor.state,
            'ready_to_donate' : donor.ready_to_donate,
            'blood_group' : donor.blood_group.name,
            'image' : donor.image.url,
        }
    }
    return JsonResponse(data)

@login_required(login_url = '/login_user/')
def profile(request):
    if request.method=="POST":
        print(request.POST)
        if "logout" in request.POST:
            logout(request)
            return redirect("/login_user/")
            
    donor_profile = Donor.objects.get(donor=request.user)
    return render(request, "profile.html", {'donor_profile':donor_profile, 'loggedIn' : True, 'username' : request.user.username})

@login_required(login_url = '/login_user/')
def edit_profile(request):
    donor_profile = Donor.objects.get(donor=request.user)
    if request.method == "POST":
        donor_profile = Donor.objects.get(donor=request.user)
        print(request.POST)
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']

        donor_profile.donor.email = email
        donor_profile.phone = phone
        donor_profile.state = state
        donor_profile.city = city
        donor_profile.address = address
        donor_profile.save()
        donor_profile.donor.save()

        if('image' not in request.POST):
            try:
                image = request.FILES['image']
                donor_profile.image = image
                donor_profile.save()
            except:
                pass
            alert = True
        else:
            print('no image uploaded')
            
        return redirect('/profile/')
        # return render(request, "edit_profile.html", {'alert':alert})
    return render(request, "edit_profile.html", {'donor_profile':donor_profile, 'loggedIn' : True, 'username' : request.user.username})
    
def change_status(request):
    donor_profile = Donor.objects.get(donor=request.user)
    
    if donor_profile.ready_to_donate:
        donor_profile.ready_to_donate = False
        donor_profile.save()
    else:
        donor_profile.ready_to_donate = True
        donor_profile.save()
    
    return redirect('/profile/')

def blood_sched (request):
     return render(request, "blood_sched.html")
        
def logout_user(request):
    logout(request)
    return JsonResponse({'success' : True})

def contact (request):
    return render(request, "contact.html")
 
def admin_base (request):
    return render(request, "admin_base.html")
 
def home_admin (request):
    return render(request, "home_admin.html")
 
def donate_form (request):
    if request.method == "POST":
        try:
            user = User.objects.get(email = request.POST['email'])
            donor = Donor.objects.get(donor = user)
            
            # save data
            full_name = request.POST['full_name']
            email = request.POST['email']
            branch = request.POST['branch']
            date = request.POST['date']
            units = request.POST['units']
            
            donor.units_blood_donated = int(donor.units_blood_donated) + int(units)
            donor.save()
            
            donate = donation_history.objects.create(donor=user,name=full_name,email=email,branch=branch,donation_date=date,units_blood_donated=units)
            donate.save()
            
            print('Valid Email')
            body = f"""
            Dear {full_name},
            Greetings!
            We admire and thank you for donating blood. You are a hero. A successful blood donation is the result of community partnerships. Volunteers like you help to ensure that those needing blood and blood produces receive thrive.
            In behalf of the Philippine National Red Cross, we have been touched by your efforts, we offer our thanks. You made a significant difference in building a stronger blood system for Filipinos.
            You may always contact us to assist you with your concerns.
            Address: 37 EDSA corner Boni Avenue, Barangka-Ilaya, Mandaluyong City 1550. Contact Us: (02) 8790-2300 local 931/932/935
            Email: communication@redcross.org.ph
            Thank you so much.
            Sincerely,
            Philippine National Red Cross
            
            note: Please reply to this message with your full name to recieve your certificate.
            """
            subject = 'blood Donation'
            email=EmailMessage(subject=subject,body=body, to=[email])
            sendEmail(email).start()
            
            return render(request, "donate_form.html",{'success' : True})

        except:
            print('invalid Email')
            inputs = {
               'full_name' : request.POST['full_name'],
               'email' : request.POST['email'],
               'branch' : request.POST['branch'],
               'blood_group' : request.POST['blood_group'],
               'date' : request.POST['date'],
               'units' : request.POST['units'],
            }
            return render(request, "donate_form.html", {'success' : False, 'inputs' : inputs})
        
    return render(request, "donate_form.html")

class sendEmail(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send()

def about_admin (request):
    return render(request, "about_admin.html")
    
    