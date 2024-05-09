from django.db import models


class Game(models.Model):
    """
    Represents a single scavenger hunt game.
    """

    id = models.AutoField(primary_key=True)
    
    # Attributes
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} (#{self.id})"
