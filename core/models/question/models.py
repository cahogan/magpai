from django.db import models
from django.conf import settings


class Question(models.Model):
    """
    Represents a question (a single clue/answer step) in a
    specific scavenger hunt game.
    """

    id = models.AutoField(primary_key=True)

    # Relationships
    game = models.ForeignKey("Game", on_delete=models.CASCADE)

    # Attributes
    name = models.CharField(max_length=100)
    clue = models.TextField(blank=True, null=True)
    answer = models.CharField(max_length=100)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.name} (#{self.id})"


class QuestionResponse(models.Model):
    """
    Represents a single response to a question in a game.
    """

    id = models.AutoField(primary_key=True)

    # Relationships
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Attributes
    response = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Response to {self.question} by {self.user} (#{self.id})"

