from django.db.models import Max

from .models import *


def check_auction_in_watchlist(user, auction):
    try:
        watchlist = Watchlist.objects.get(user=user)
        if watchlist.items.filter(id=auction.id).exists():
            return True
        else:
            return False
    except Watchlist.DoesNotExist:
        return False


def validate_bid(bid_amount: int, auction_id) -> dict:
    auction = Auction.objects.get(pk=auction_id)

    if auction.bids.exists():
        highest_bid = float(auction.bids.order_by("-amount").first().amount)
    else:
        highest_bid = 0

    if highest_bid > 0 and bid_amount <= highest_bid:
        return {
            "body": "Your bid must be at least larger than the current bid",
            "success": False,
        }

    if bid_amount < auction.starting_bid:
        return {
            "body": "Your bid must be at least larger than the starting bid",
            "success": False,
        }

    return {"body": "Your bid was placed", "success": True}
