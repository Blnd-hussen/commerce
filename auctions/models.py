from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=45, null=False, blank=False)

    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField(max_length=45, null=False, blank=False)
    description = models.TextField()
    category = models.ForeignKey(
        "Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="items",
    )
    image_url = models.URLField(
        max_length=300,
        blank=True,
        default="https://img.freepik.com/premium-vector/default-image-icon-vector-missing-picture-page-website-design-mobile-app-no-photo-available_87543-11093.jpg",
    )

    def __str__(self):
        return f"""
            {{
                title: {self.title},
                description: {self.description},
                category: {self.category},
                image_url: {self.image_url}
            }}
        """


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)


class Auction(models.Model):
    STATUS_CHOICES = [("open", "Open"), ("closed", "Closed")]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_auctions",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="auctions",
    )
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default="open")
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    bids = models.ManyToManyField(Bid, related_name="auctions")
    comments = models.ManyToManyField(Comment)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Auction for {self.item.title} by {self.user.username} is {self.status}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    items = models.ManyToManyField(Auction, related_name="watchlist")

    def __str__(self):
        return f"{self.user}'s Watchlist"
