
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.exceptions import ValidationError
from .forms import UploadFileForm
from django.http import JsonResponse
# import openpyxl
import csv
import requests
import pandas as pd
import json

API_BASE_URL = "http://127.0.0.1:8000/api/auth/" 

def home(request):
        return render(request, 'frontend/home.html')


def send_otp_email(otp, email):
    subject = "Verify your Email - {}".format(email)
    print(otp)
    message = "Your 4-digit OTP to verify your account is : " + str(otp) + ". Please don't share it with anyone else"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def send_psw_email(otp, email):
    subject = "Reset your Password - {}".format(email)
    print(otp)
    message = "Your 4-digit OTP to reset your password is : " + str(otp) + ". Please don't share it with anyone else"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def Register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']
        # Interact with register API
        response = requests.post(API_BASE_URL + 'register/', data={
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': confirm_password
        })
        if response.status_code == 201:
            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = response.json().get('password')
            request.session['otp'] = response.json().get('otp')
            messages.success(request, "OTP is sent to your email. Please enter it.")
            return render(request, 'frontend/otp.html')  # Redirect to login page after successful registration
           
        else:
            error_message = response.json().get('error', 'Registration failed')
            messages.error(request, error_message)
            return render(request, 'frontend/register.html', {'error':error_message})

    return render(request, 'frontend/register.html')



def Login(request):
    request.session['otp_attempts'] = 0
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Interact with login API
        response = requests.post(API_BASE_URL + 'login/', data={'username': username, 'password': password})
        if response.status_code == 200:
            request.session['username'] = username
            request.session['login'] = "True"
            # messages.success(request, "User created succesfully. Log in now")
            # return render(request,'frontend/home.html', {'username': username, 'login': 'True'})  # Redirect to some home page after successful login
            return redirect('home')
        else:
            errorData = response.json().get('error')
            # messages.error(request, errorData)
            return render(request, 'frontend/index.html', {'error': errorData})
    else:
        print("Printing view")
        return render(request, 'frontend/index.html')
    
def FpEmail(request):
    if request.method == "POST":
        email = request.POST['email'].lower()
        print(f"Received email: {email}")  # Debugging line
        response = requests.post(API_BASE_URL + 'verify-email/', data = {'email':email})

        if response.status_code == 201:
            request.session['email'] = email
            request.session['otp'] = response.json().get("otp")
            messages.success(request, "OTP is sent to your email. Please enter it.")
            return render(request, "frontend/reset_password_otp.html")
        
        else:   
            error_message = response.json().get('error')
            messages.error(request, error_message)
            return render(request, 'frontend/register.html', {'error':error_message})
    else:
        return render(request, "frontend/forgot_password.html")


def Logout(request):
    if 'username' in request.session:
        print("here i am ")
        del request.session['username']
    
        return redirect("login")
    else:
        return redirect("login")


def VerifyOTPPage(request):
    return render(request, "frontend/otp.html")


def FpEmailPage(request):
    return render(request, "frontend/forgot_password.html")


def FpOTP(request):
    if request.method == "POST":
        email = request.session.get('email').lower()

        mainotp = request.POST['otp']

      

        try:
            if int(request.session.get('otp')) == int(mainotp):
                
                request.session['email'] = email
                del request.session['otp']
                messages.success(request, "Reset password link activated")
                return render(request, "frontend/reset_password.html")
            else:
                messages.error(request, "Invalid OTP. Please try again")
                return render(request, "frontend/reset_password_otp.html")
        except:
            messages.error(request, "OTP must be a numeric value. Please enter a valid OTP.")
        
        return render(request, 'frontend/otp.html')



def FpPassword(request):
    if request.method == "POST":
        email = request.session.get("email")
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        print(email)
        if password == confirm_password:
            response = requests.post(API_BASE_URL + 'reset-password/', data = {'email':email, 'password':password})

            if response.status_code == 205:
                del request.session["email"]
                messages.success(request, "Password resetted successfully")
                return redirect("login")
            else:
                error_message = response.json().get('error', 'Registration failed')
                return render(request, 'frontend/reset_password.html', {'error':error_message})

        else: 
            return render(request, 'frontend/reset_password.html', {'error':"Passwords do not match"})



# def handle_uploaded_csv(f):
#     # Check file size (limit to 5MB)
#     if f.size > 5 * 1024 * 1024:
#         raise ValidationError("File size should be under 5MB")
#     print(f"Uploading file: {f.name}")
#     # Check file format
#     if not f.name.endswith('.csv'):
#         raise ValidationError("Unsupported file format. Please upload a CSV file.")

#     # Handle CSV file
#     try:
#         reader = csv.reader(f.read().decode('utf-8').splitlines())
#         for row in reader:
#             # Process each row
#             # print(row)
#             print(f"Processing row: {row}")
#             print("CSV file processed successfully")
#     except Exception as e:
#         print(f"Error processing CSV file: {e}")
#         raise ValidationError("Corrupted CSV file")

# def handle_uploaded_excel(f):
#     # Check file size (limit to 5MB)
#     print(f"Uploading file: {f.name}")
#     if f.size > 5 * 1024 * 1024:
#         raise ValidationError("File size should be under 5MB")
#     print("File size is within the limit")
#     # Check file format
#     if not (f.name.endswith('.xlsx') or f.name.endswith('.xls')):
#         raise ValidationError("Unsupported file format. Please upload an Excel file.")
#     print("File format is Excel")
#     # Handle Excel file
#     try:
#         wb = openpyxl.load_workbook(f)
#         sheet = wb.active
#         for row in sheet.iter_rows(values_only=True):
#             # Process each row
#             # print(row)
#             print(f"Processing row: {row}")
#             print("Excel file processed successfully")
#     except Exception as e:
#         print(f"Error processing Excel file: {e}")
#         raise ValidationError("Corrupted Excel file")


# def upload_csv(request):
#     csv_content = []
#     if request.method == 'POST':
#         csv_file = request.FILES.get('csvfile')


#         try:
#             decode_file = csv_file.read().decode('utf-8').splitlines()
#             reader = csv.reader(decode_file)
#             csv_content = []
#             header = next(reader)  # Get the header row

#             if any(h.strip() == '' for h in header):
#                 messages.error(request, 'CSV file contains empty header fields.')
#                 return render(request, 'frontend/home.html', {'error': 'CSV file contains empty header fields.'})
#                 # return JsonResponse({'error': 'CSV file contains empty header fields.'}, status=400)
#             num_columns = len(header)
#             for row in reader:
#                 if len(row) != num_columns:
#                     messages.error(request, 'CSV file is not in proper format. Number of columns do not match.')
#                     return JsonResponse({'error': 'CSV file is not in proper format. Number of columns do not match.'}, status=400)
#                     # return render(request, 'frontend/home.html', {'error': 'CSV file is not in proper format. Number of columns do not match.'})
#                 csv_content.append(', '.join(row))

#             return render(request, 'frontend/home.html', {'csv_content': '\n'.join(csv_content)})
#             # return JsonResponse({'success': True, 'csv_content': csv_content})

#         except UnicodeDecodeError as e:
#             # Handle encoding errors
#             messages.error(request, f'Encoding error: {e}. Please ensure the file is UTF-8 encoded.')
#             # return JsonResponse({'error': 'Encoding error: Please ensure the file is UTF-8 encoded.'}, status=500)
#             return render(request, 'frontend/home.html', {'error': f'Encoding error: Please ensure the file is UTF-8 encoded.'})

#         except csv.Error as e:
#             # Handle CSV-specific parsing errors
#             messages.error(request, f'CSV parsing error: {e}')
#             return render(request, 'frontend/home.html', {'error': f'CSV parsing error: {e}'})
#             # return JsonResponse({'error': f'CSV parsing error: {e}'}, status=500)

#         except Exception as e:
#             # Catch any other exceptions
#             print("General error processing file:", e)
#             messages.error(request, f'Error processing file: {e}')
#             return render(request, 'frontend/home.html')

#     return render(request, 'frontend/home.html')
#     # return JsonResponse({'error': 'Invalid request method.'}, status=405)


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csvfile')
        
        if not csv_file:
            return JsonResponse({'error': 'No file uploaded.'}, status=400)

        try:
            decode_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decode_file)
            header = next(reader)  # Get the header row

            if any(h.strip() == '' for h in header):
                print("here")
                return JsonResponse({'error': 'CSV file contains empty header fields.'}, status=400)

            num_columns = len(header)
            csv_content = []
            for row in reader:
                if len(row) != num_columns:
                    return JsonResponse({'error': 'CSV file is not in proper format. Number of columns do not match.'}, status=400)
                if any(r.strip() == '' for r in row):
                    print("here")
                    return JsonResponse({'error': 'CSV file contains empty fields.'}, status=400)
                csv_content.append(', '.join(row))

            return JsonResponse({'message': 'CSV uploaded successfully!', 'csv_content': '\n'.join(csv_content)})

        except UnicodeDecodeError as e:
            return JsonResponse({'error': f'Encoding error: {e}. Please ensure the file is UTF-8 encoded.'}, status=500)

        except csv.Error as e:
            return JsonResponse({'error': f'CSV parsing error: {e}'}, status=500)

        except Exception as e:
            return JsonResponse({'error': f'Error processing file: {e}'}, status=500)
    

    return JsonResponse({'error': 'Invalid request method.'}, status=405)




def upload_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excelfile')
        print(excel_file)
        try:
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(excel_file)


            unnamed_count = df.columns.str.contains('^Unnamed').sum()
            if unnamed_count > 0:
                # return render(request, 'frontend/home.html', {'error': "There are blank headers in the Excel file."})
                return JsonResponse({'error': "There are blank headers in the Excel file."})

            excel_content = df.to_string(index=False)
            # Additional checks can be done here, like data type validation if needed

            return JsonResponse({'message': 'Excel file uploaded successfully!', 'excel_content': excel_content})

        except Exception as e:
            # Handle any errors that arise while processing the file
            messages.error(request, f'Error processing file: {e}')
            return JsonResponse({'error': f'Error processing file: {e}'})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def ChatHistoryPage(request):
    return render(request, "frontend/chat_history.html")



def VerifyOTP(request):
    if request.method == "POST":
        print(request.session.get('username'))
        mainotp = request.POST['otp']

        if request.session.get('otp_blocked', False):
            messages.error(request, "You have exceeded the maximum OTP attempts. Please reset the OTP.")
            return redirect('reset-otp')


        if 'otp_attempts' not in request.session:
            request.session['otp_attempts'] = 0
        print(request.session['otp_attempts'])
        try:
            # Convert OTP to integer for comparison
            if int(mainotp) == int(request.session.get('otp')):
                request.session['otp_attempts'] = 0  # Reset attempts on success
                response = requests.post(API_BASE_URL + 'create-user/', data={
                    'username': request.session.get('username'),
                    'email': request.session.get('email'),
                    'password': request.session.get('password'),    
                    'otp': mainotp
                })
                if response.status_code == 201:
                    messages.success(request, "User created successfully. Log in now")
                    return redirect('login')
            else:
                # request.session['otp_blocked'] == "True"
                request.session['otp_attempts'] += 1
                if request.session['otp_attempts'] >= 3:
                    messages.error(request, "Maximum attempts reached. Please reset OTP.")
                    # Pass a flag to the frontend to block input
                    return render(request, 'frontend/otp.html', {'block_input': True})
                else:
                    messages.error(request, f"Invalid OTP. You have {3 - request.session['otp_attempts']} attempts left.")
        
        except ValueError:
            # Handle the case where the OTP is not a valid number
            messages.error(request, "OTP must be a numeric value. Please enter a valid OTP.")
        
        return render(request, 'frontend/otp.html', {'block_input': False})

    else:
        print("Old request" + str(request))
        return render(request, "frontend/otp.html")


def ResendOTP(request):

    email = request.session.get('email')
    otp = random.randint(1000,9999)
    request.session['otp_attempts'] = 0
    send_otp_email(otp, email)
    messages.success(request, "OTP is sent to your email. Please enter it.")
    return render(request, 'frontend/otp.html')


def Generate(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from request.body
            data = json.loads(request.body)

            prompt = data.get('prompt')
            username = data.get('username')
            sqlServer = data.get('database')
            file = data.get('fileUploaded')

            # Print to confirm data reception
            response = requests.post(API_BASE_URL + 'generate-sql/', data={
                'prompt': prompt,
                'username':username,
                'sqlServer':sqlServer,
                'file':file
            })
            if response.status_code == 200:
                sql_generated = response.json().get('sql_generated')
                return JsonResponse({"message": "Query generated successfully!" , "sql_generated": sql_generated}) 
            else:
                return JsonResponse({"error":"Server issue"})

            # Simulate response (You can replace this with actual logic)

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
        # response = requests.post(API_BASE_URL + 'generate-sql/', data={'prompt':prompt})

        # if response.status_code == 200:
        #     messages.success(request, "HELLO")
        #     return render(request, "frontend/home.html")
        # else:
        #     messages.error(request, "Not working")
        #     return render(request, "frontend/home.html")