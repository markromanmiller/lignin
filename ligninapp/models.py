import rules
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as gtl
from rules.contrib.models import RulesModel


@rules.predicate
def view_question(user, question):
    if question is None:
        return True
    try:
        q_perm = QuestionPermission.objects.get(user=user.lignin_user, question=question)
        return q_perm.permission in ['VIEW', 'PROP', 'MOD', 'ADMIN']
        # otherwise, go to the default.
    except QuestionPermission.DoesNotExist:
        return question.default_permission in ['VIEW', 'PROP', 'MOD', 'ADMIN']


class LigninUser(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lignin_user')

    def __str__(self):
        return self.owner.username


class PermissionEnum(models.TextChoices):
    NONE = 'NONE', gtl('None') # do nothing (for defaults)
    VIEW = 'VIEW', gtl('View') # see stuff
    PROPOSE = 'PROP', gtl('Propose') # suggest stuff
    MODERATE = 'MOD', gtl('Moderate') # approve, edit directly
    ADMIN = 'ADMIN', gtl('Administrate') # edit permissions, etc. (don't think too hard yet)


class QuestionPermission(models.Model):
    user = models.ForeignKey(LigninUser, on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    permission = models.CharField(choices=PermissionEnum.choices, max_length=5)

class Paper(RulesModel):
    ssPaperID = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500)
    faln = models.CharField(max_length=100)
    references = models.TextField()
    citations = models.TextField()
    year = models.IntegerField()
    url = models.URLField()
    default_subpaper = models.ForeignKey("Subpaper", null=True, on_delete=models.SET_NULL, related_name="default_of")

    def __str__(self):
        return f"{self.faln} ({self.year}) {self.title[:20]}..."


class Subpaper(RulesModel):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        if self.description:
            return f"{self.paper}, {self.description}"
        else:
            return f"{self.paper}"


class Column(RulesModel):
    name = models.CharField(max_length=200)
    default_permission = models.CharField(choices=PermissionEnum.choices, max_length=5)

    def __str__(self):
        return self.name


class Question(RulesModel):
    question_text = models.CharField(max_length=200)
    columns = models.ManyToManyField(Column, blank=True)
    papers = models.ManyToManyField(Subpaper, blank=True)
    rejected_papers = models.TextField(blank=True)
    default_permission = models.CharField(choices=PermissionEnum.choices, max_length=5)

    def __str__(self):
        return f'{self.question_text}'


rules.add_perm('ligninapp', rules.always_allow)
rules.add_perm('ligninapp.add_question', rules.is_authenticated)
rules.add_perm('ligninapp.view_question', view_question)
rules.add_perm('ligninapp.change_question', view_question)


class Value(RulesModel):
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    paper = models.ForeignKey(Subpaper, on_delete=models.CASCADE)
    creator = models.ForeignKey(LigninUser, null=True, on_delete=models.SET_NULL)
    value = models.CharField(max_length=1000)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.column} for {self.paper}: {self.value}"
