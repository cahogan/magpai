from django.db import models


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
