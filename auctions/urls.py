from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("closed_auctions", views.closed_auctions, name="closedAuctions"),
    path("create_listing", views.create_listing, name="createListing"),
    path("categories", views.view_categories, name="categories"),
    path("category/<str:name>", views.view_category, name="category"),
    path("listing_page/<int:auction_id>", views.listing_page, name="listingPage"),
    path("close_auction/<int:auction_id>", views.close_auction, name="closeAuction"),
    path("watchlist", views.watchlist, name="watchlist"),
    path(
        "add_to_watchlist/<int:auction_id>",
        views.add_to_watchlist,
        name="addToWatchlist",
    ),
    path(
        "remove_from_watchlist/<int:auction_id>",
        views.remove_from_watchlist,
        name="removeFromWatchlist",
    ),
    path("place_bid/<int:auction_id>", views.place_bid, name="placeBid"),
    path("add_comment/<int:auction_id>", views.add_comment, name="addComment"),
]
