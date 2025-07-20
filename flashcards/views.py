
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout 
from django.contrib.auth import authenticate, login as auth_login
from .models import Deck, Card
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import random


User = get_user_model()

@login_required
def index(request):
    decks = Deck.objects.filter(owner=request.user)
    return render(request, 'flashcards/index.html', {'decks': decks})


def login(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        # login in account exists
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
        
    return render(request, "flashcards/login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):

    if request.method == "POST":
        
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")
        
        # show error if passwords dont match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")


        # check is account already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Username already exists.")
            return render(request, "flashcards/register.html")
        
        # otherwise create account
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account Created!")
        return redirect('login')
    

    return render(request, "flashcards/register.html")




def viewDecks(request): 
    return redirect('index')


def addCard(request):
    return render(request, "flashcards/index.html")


def addDeck(request):
    
    if request.method == "POST":

        name = request.POST.get('deck_name')
        description = request.POST.get('deck_description')

        if not name:
            messages.error(request, "Deck name is required")
            return redirect('index')
        
        Deck.objects.create(
            name=name,
            description = description,
            owner=request.user,
            last_reviewed = None
        )

        messages.success(request, "Deck Created")
        return redirect('index')
    

    return redirect('index')


@login_required
def viewDeck(request, deck_id):

    deck = get_object_or_404(Deck, id=deck_id, owner=request.user)
    cards = Card.objects.filter(deck=deck)

    share_url = request.build_absolute_uri(deck.get_share_url())
    return render(request, 'flashcards/deck.html', {
        "deck": deck, 
        "cards": cards,
        "share_url": share_url,
    })



@login_required
def viewCards(request, deck_id):

    deck = get_object_or_404(Deck, id=deck_id, owner=request.user)
    cards = Card.objects.filter(deck=deck)
    return render(request, 'flashcards/viewCards.html', {
        "deck": deck,
        "cards": cards,
    })




@login_required
def addCard(request, deck_id):

    deck = get_object_or_404(Deck, id=deck_id, owner=request.user)

    if request.method == "POST":

        question = request.POST.get('card_question')
        answer = request.POST.get('card_answer')


        if not question or not answer: 
            messages.error(request, 'Question and Answer cant be empty')
        
        else:
            card = Card.objects.create(deck=deck, front=question, back=answer)
            return redirect('viewCards', deck_id=deck_id)

    return render(request, 'flashcards/addCard.html', {
        'deck_id': deck_id
    })



def editCard(request, card_id):


    card = get_object_or_404(Card, id=card_id, deck__owner=request.user)

    if request.method == "POST":

        card.front = request.POST.get('card_question')
        card.back = request.POST.get('card_answer')
        card.save()
        return redirect('viewCards', deck_id=card.deck.id)
    
    return render(request, 'flashcards/editCard.html', {"card": card, "deck_id": card.deck.id})



def deleteCard(request, card_id):

    card = get_object_or_404(Card, id=card_id, deck__owner=request.user)
    deck_id = card.deck.id
    card.delete()
    return redirect('viewCards', deck_id=deck_id)




def studyDeck(request, deck_id):


    # get deck and its cards
    deck = get_object_or_404(Deck, id=deck_id, owner=request.user)
    allCards = deck.card.all().order_by('last_reviewed', 'created_at')


    # cache fixed card order
    if 'study_card_ids' not in request.session or not request.session['study_card_ids']:
        request.session['study_card_ids'] = list(allCards.values_list('id', flat=True))
        request.session['study_index'] = 0


    # get card's index, default to 0
    card_ids = request.session['study_card_ids']
    cardIndex = request.session.get('study_index', 0)
    

    # finish deck if user finished all cards
    if cardIndex >= len(card_ids):
        request.session['study_index'] = 0
        request.session['study_card_ids'] = []
        if request.headers.get("x-request-with") == "XMLHttpRequest":
            return JsonResponse({'done': True})
    
        return redirect('viewDeck', deck_id=deck.id)

    # get current card's position
    card_id = card_ids[cardIndex]
    card = get_object_or_404(Card, id=card_id, deck=deck)
    
    if request.method == "POST":

        difficulty = request.POST.get('difficulty', 'medium')
        card.difficulty = difficulty
        card.last_reviewed = timezone.now()
        card.save() 

        # stay on current card if user clicks again
        if difficulty.lower() == 'again':
            pass 
        
        # otherwise move onto the next
        else:
            request.session['study_index'] = cardIndex + 1

            if difficulty.lower() in ['hard', 'medium']:
                # avoid duplicates
                if card_id in card_ids[cardIndex+1:]:
                    card_ids.remove(card_id)


                # reinsert card randomy after the next card
                remaining = card_ids[cardIndex+1:]
                insertOffset = random.randint(2, len(remaining)) if len(remaining) >= 3 else len(remaining)
                newIndex = cardIndex + 1 + insertOffset
                card_ids.insert(newIndex, card_id)
                request.session['study_card_ids'] = card_ids
            
        # get next card
        next_index = request.session.get('study_index', 0)
        if next_index >= len(card_ids):
            return JsonResponse({'done': True})
        next_card_id = card_ids[next_index]
        next_card = get_object_or_404(Card, id=next_card_id, deck=deck)
            
        return JsonResponse({
            'done': False,
            'front': next_card.front,
            'back': next_card.back
        })

    deck.last_reviewed = timezone.now()
    deck.save()
    return render(request, 'flashcards/study.html', {
        "deck": deck,
        "card": card
    })
    

@csrf_exempt
def set_timezone(request):
    if request.method == "POST":
        tzname = request.POST.get("timezone")
        if tzname:
            request.session["django_timezone"] = tzname
            timezone.activate(tzname)
    return HttpResponse("Timezone set")



def sharedDeckView(request, token):
    deck = get_object_or_404(Deck, share_token = token)
    cards = Card.objects.filter(deck=deck)
    return render(request, 'flashcards/sharedDeck.html', {
        "deck": deck,
        "cards": cards
    })



@login_required
@require_POST
def copy_shared_deck(request, token):
    original_deck = get_object_or_404(Deck, share_token=token)

    # Duplicate the deck for the current user
    new_deck = Deck.objects.create(
        name=original_deck.name + " (Copy)",
        description=original_deck.description,
        owner=request.user
    )

    # Duplicate all cards in the deck
    original_cards = Card.objects.filter(deck=original_deck)
    for card in original_cards:
        Card.objects.create(
            deck=new_deck,
            front=card.front,
            back=card.back,
            difficulty=card.difficulty
        )

    messages.success(request, "Deck copied to your account!")
    return redirect("viewDeck", deck_id=new_deck.id)