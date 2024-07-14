from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404

from .models import *
from .utils import *


def index(request: HttpRequest):
    auctions = Auction.objects.all().order_by('-created')

    for auction in auctions:
        if auction.bids.exists():
            highest_bid = auction.bids.order_by("-amount").first().amount
        else:
            highest_bid = 0

        auction.highest_bid = highest_bid

    return render(
        request,
        "auctions/index.html",
        {
            "auctions": auctions,
        },
    )


def closed_auctions(request):
    closed_auctions = Auction.objects.filter(status="closed")

    for auction in closed_auctions:
        if auction.bids.exists():
            highest_bid = auction.bids.order_by("-amount").first().amount
            auction.highest_bid = highest_bid

    return render(
        request,
        "auctions/closed-auctions.html",
        {"closed_auctions": closed_auctions},
    )


@login_required
def create_listing(request: HttpRequest):
    if request.method == "POST":
        title = request.POST.get("title")
        starting_bid = request.POST.get("starting_bid")
        image_url = request.POST.get("image_url")
        category = request.POST.get("category")
        description = request.POST.get("description")

        if not (title or starting_bid or description):
            messages.error(request, "Please fill out the required fields")
            return redirect("createListing")

        if image_url == "":
            image_url = "https://img.freepik.com/premium-vector/default-image-icon-vector-missing-picture-page-website-design-mobile-app-no-photo-available_87543-11093.jpg"

        if category:
            category_object = Category.objects.get_or_create(name=category)[0]
        else:
            category_object = None

        item = Item(
            title=title,
            description=description,
            image_url=image_url,
            category=category_object,
        )
        item.save()

        auction = Auction(user=request.user, item=item, starting_bid=starting_bid)
        auction.save()

        return redirect("listingPage", auction_id=auction.id)

    categories = Category.objects.all()
    for category in categories:
        print(category)

    return render(request, "auctions/create-listing.html", {"categories": categories})


def listing_page(request: HttpRequest, auction_id: int):
    auction = get_object_or_404(Auction, pk=auction_id)
    current_users_bid = None
    highest_bid = None
    number_of_bids = 0

    if auction.bids.exists():
        current_user_bids = auction.bids.filter(bidder=request.user)
        if current_user_bids.exists():
            current_users_bid = current_user_bids.first()
        highest_bid = auction.bids.order_by("-amount").first()
        number_of_bids = auction.bids.count()
    item_in_watchlist = check_auction_in_watchlist(request.user, auction)

    if auction.status == "closed":
        bids = auction.bids.all()
        if bids.exists():
            winner = auction.bids.order_by("-amount").first().bidder
            if request.user == winner:
                messages.info(request, "You have won this auction!")
            else:
                messages.info(request, f"{winner} has won this auction")

    return render(
        request,
        "auctions/listing-page.html",
        {
            "auction": auction,
            "highest_bid": highest_bid,
            "item_in_watchlist": item_in_watchlist,
            "current_users_bid": current_users_bid,
            "number_of_bids": number_of_bids,
        },
    )


def view_categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})


def view_category(request, name: str):
    category = get_object_or_404(Category, name=name)
    auctions = Auction.objects.filter(item__category=category)

    print(auctions)
    return render(
        request, "auctions/category.html", {"auctions": auctions, "category": name}
    )


@login_required
def close_auction(request: HttpRequest, auction_id: int):
    auction = get_object_or_404(Auction, pk=auction_id)
    action = request.POST.get("action")

    if action == "sell":
        auction.status = "closed"
        auction.save()
    else:
        auction.delete()
        messages.warning(request, "Auction was deleted")
        return redirect("index")

    messages.success(request, "Auction is now closed")
    return redirect("listingPage", auction_id=auction_id)


@login_required
def watchlist(request: HttpRequest):
    watchlist = Watchlist.objects.get_or_create(user=request.user)[0]
    return render(
        request, "auctions/watchlist.html", {"watchlist": watchlist.items.all()}
    )


@login_required
def add_to_watchlist(request: HttpRequest, auction_id: int):
    auction = get_object_or_404(Auction, pk=auction_id)
    watchlist = Watchlist.objects.get_or_create(user=request.user)

    if not check_auction_in_watchlist(request.user, auction):
        watchlist[0].items.add(auction)

    return redirect("listingPage", auction.id)


@login_required
def remove_from_watchlist(request: HttpRequest, auction_id: int):
    auction = get_object_or_404(Auction, pk=auction_id)
    watchlist = Watchlist.objects.get(user=request.user)

    if check_auction_in_watchlist(request.user, auction):
        watchlist.items.remove(auction)

    return redirect("listingPage", auction.id)


@login_required
def place_bid(request: HttpRequest, auction_id: int):
    auction = get_object_or_404(Auction, pk=auction_id)
    bid_amount = request.POST.get("bid_amount")

    try:
        bid_amount = float(bid_amount)
    except Exception:
        messages.error(request, "Invalid Bid")
        return redirect("listingPage", auction_id=auction_id)

    validate = validate_bid(bid_amount, auction_id)
    if not validate["success"]:
        messages.error(request, validate["body"])
        return redirect("listingPage", auction_id=auction_id)

    exsisting_bid = auction.bids.filter(bidder=request.user).first()

    if exsisting_bid:
        exsisting_bid.amount = bid_amount
        exsisting_bid.save()
    else:
        with transaction.atomic():
            bid = Bid(bidder=request.user, amount=bid_amount)
            bid.save()
            auction.bids.add(bid)
            auction.save()

    messages.success(request, validate["body"])
    return redirect("listingPage", auction_id=auction_id)


@login_required
def add_comment(request, auction_id: int):
    comment = request.POST.get("comment")

    if comment == "":
        messages.error("can not post empty comment")
        return redirect("listingPage", auction_id)

    comment_obj = Comment(user=request.user, body=comment)
    comment_obj.save()

    auction = get_object_or_404(Auction, pk=auction_id)
    auction.comments.add(comment_obj)
    auction.save()

    return redirect("listingPage", auction_id)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
