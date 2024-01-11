from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# Create your views here.
from django.shortcuts import render
from .models import UserProfile
from django.contrib.auth.decorators import login_required

import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render
from django.http import HttpResponse
import nltk
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile

@login_required
def index(request):
    user = request.user
    user_profile = UserProfile.objects.filter(user=user).first()

    if user_profile:
        # Assuming you have a function to get book suggestions using GPT-3
        book_suggestions = get_book_suggestions(user_profile.favorite_author, user_profile.favorite_genre, user_profile.favorite_book)
        
        context = {
            'user_profile': user_profile,
            'book_suggestions': book_suggestions,
        }
        print(book_suggestions)
        return render(request, 'index.html', context)
    else:
        # Handle the case where the user doesn't have a UserProfile
        return render(request, 'index.html')
    
import openai
from django.conf import settings

def get_book_suggestions(favorite_author, favorite_genre, favorite_book):
    openai.api_key = settings.OPENAI_API_KEY
    try:
        prompt = f"suggest me some books related to {favorite_author}, {favorite_book}, {favorite_genre} with some proper html tag as i will fetch the answer in frontend so it should look good use b tag to make book name bold every book should be in new line including first book so use br tag "

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        gpt3_response = response['choices'][0]['message']['content'].strip()
        print(gpt3_response)
        return gpt3_response

    except Exception as e:
        print(f"Error communicating with GPT-3: {e}")
        return redirect('index/')

def signupview(request):
    if request.method=="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('mail')
        password=request.POST.get('password')
        user = User.objects.create_user(username=email, password=password,first_name=first_name,last_name=last_name)
        # user.first_name = first_name
        # user.last_name = last_name
        print(first_name,last_name,email,password)
        user.save()

        # Log in the user
        login(request, user)

        # Redirect to a success page or homepage
        return redirect('/')
    return render(request,'signup.html')

def loginview(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username,password)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')  # Replace 'success_page' with the actual URL name or path
        else:
            return render(request, 'login.html', {'error_message': 'Invalid credentials'})

    return render(request, 'login.html')

@login_required
def profile(request):
    user = request.user
    username = user.first_name
    email = user.username

    # Retrieve or create a UserProfile instance for the user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # If it's a POST request, update the UserProfile with form data
        favgenre = request.POST.get('favgenre')
        favauthor = request.POST.get('favauthor')
        favbook = request.POST.get('favbook')
        print(favauthor,favbook,favgenre)

        # Update UserProfile fields
        user_profile.favorite_genre = favgenre
        user_profile.favorite_author = favauthor
        user_profile.favorite_book = favbook

        # Save the changes
        user_profile.save()
        print('saved')

    # Pass user details and UserProfile to the template
    context = {
        'username': username,
        'email': email,
        'favlist': user_profile,
    }

    return render(request, 'profile.html', context)



# Ensure stopwords are downloaded
# nltk.download('stopwords')

def download_nltk_resources():
    # Download NLTK resources
    nltk.download('punkt')
    nltk.download('stopwords')


def generate_pdf_summary(pdf_content):
    try:
        # Using PyMuPDF to extract text from PDF
        doc = fitz.open(stream=pdf_content, filetype='pdf')
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()

        # Tokenize sentences
        sentences = sent_tokenize(text)

        # Remove stop words
        stop_words = set(stopwords.words("english"))
        sentences = [sentence for sentence in sentences if sentence.lower() not in stop_words]

        # Calculate TF-IDF matrix
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(sentences)

        # Calculate cosine similarity between sentences
        cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Summarize using the sentence with the highest rank
        summary_index = cosine_similarities.sum(axis=1).argmax()
        summary = sentences[summary_index]

        return summary

    except Exception as e:
        # Handle errors, you can log the exception for debugging
        print(f"Error generating summary: {e}")
        return None

def pdf_summary(request):
    if request.method == 'POST' and request.FILES.get('pdfFile'):
        pdf_file = request.FILES['pdfFile']

        # Read the content of the uploaded PDF file
        pdf_content = b""
        try:
            pdf_content = pdf_file.read()
        except Exception as e:
            # Handle errors, you can log the exception for debugging
            print(f"Error reading PDF content: {e}")
        download_nltk_resources()

        # Generate summary
        summary = generate_pdf_summary(pdf_content)

        if summary:
            # If summary is generated successfully, pass it to the template
            return render(request, 'summary.html', {'summary': summary})
        else:
            # If there was an error, render the summary.html without the summary
            return render(request, 'summary.html', {'error': True})

    # If the request method is not POST or no file is uploaded, render the form
    return render(request, 'summary.html')


from django.shortcuts import render
from .models import bookdetails

def booksave(request):
    # Creating instances of the bookdetails class and saving them to the database
    book1 = bookdetails.objects.create(genre='Science Fiction', author='Isaac Asimov', title='Foundation')
    book2 = bookdetails.objects.create(genre='Mystery', author='Agatha Christie', title='Murder on the Orient Express')
    book3 = bookdetails.objects.create(genre='Fantasy', author='J.K. Rowling', title='Harry Potter and the Philosopher\'s Stone')
    book4 = bookdetails.objects.create(genre='Drama', author='F. Scott Fitzgerald', title='The Great Gatsby')
    book5 = bookdetails.objects.create(genre='Thriller', author='Dan Brown', title='The Da Vinci Code')
    book6 = bookdetails.objects.create(genre='Historical Fiction', author='Ken Follett', title='The Pillars of the Earth')
    book7 = bookdetails.objects.create(genre='Romance', author='Jane Austen', title='Pride and Prejudice')
    book8 = bookdetails.objects.create(genre='Adventure', author='Jules Verne', title='Twenty Thousand Leagues Under the Sea')
    book9 = bookdetails.objects.create(genre='Comedy', author='Mark Twain', title='The Adventures of Tom Sawyer')
    book10 = bookdetails.objects.create(genre='Horror', author='Stephen King', title='The Shining')
    
    # Assuming you have an 'index.html' template in the 'templates' folder of your app
    return render(request, 'index.html')
