from django.db import models


class Game(models.Model):
    """
    Represents a single scavenger hunt game.
    """

    id = models.AutoField(primary_key=True)
    
    # Relationships
    current_judge = models.ForeignKey("Judge", on_delete=models.CASCADE, blank=True, null=True)

    # Attributes
    intro = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=100)
    prize = models.CharField(max_length=100)
    outro = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (#{self.id})"


class Judge(models.Model):
    """
    Represents a judge in a game.
    """

    id = models.AutoField(primary_key=True)
    
    # Attributes
    name = models.CharField(max_length=100)
    personality_string = models.TextField()
    profile_image = models.ImageField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} (#{self.id})"
