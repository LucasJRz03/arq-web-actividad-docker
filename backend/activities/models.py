import uuid

from django.db import models  # type: ignore[reportMissingModuleSource]


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)

    def __str__(self):
        return self.name

class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)
    starts_at = models.DateTimeField()
    capacity = models.PositiveIntegerField()

    class Meta:
        ordering = ("starts_at",)
        verbose_name_plural = "activities"

    def __str__(self):
        return self.title

    @property
    def available_slots(self) -> int: 
        """Contar inscripciones y compararlas con capacity."""
        enrolled_count = self.enrollments.count()
        return max(0, self.capacity - enrolled_count)

class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = models.ForeignKey(
        Participant, 
        on_delete=models.CASCADE, 
        related_name="enrollments"
        )
    activity = models.ForeignKey(
        Activity, 
        on_delete=models.CASCADE, 
        related_name="enrollments"
        )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # No se puede inscribir a un participante en la misma actividad más de una vez.
        constraints: list[models.UniqueConstraint] = [  # noqa: RUF012
            models.UniqueConstraint(fields=["participant", "activity"], name="unique_participant_activity")
        ]
        ordering = ("-enrolled_at",)

    def __str__(self):
        return f"{self.participant.name} -> {self.activity.title}"

        
