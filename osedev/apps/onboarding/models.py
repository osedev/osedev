#  Copyright (C) 2017 The OSEDev Authors.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition
from jsonfield import JSONField
from yamlfield.fields import YAMLField
from .steps import widgets, value_widgets


class ApplicationQuerySet(models.QuerySet):

    def available(self, exclude=None):
        result = self.filter(state=Application.LIVE)
        if exclude:
            result = result.exclude(pk__in=exclude)
        return result


class Application(models.Model):

    class Meta:
        verbose_name = "Application Form"
        verbose_name_plural = "Application Forms"
        ordering = ('created',)

    name = models.CharField(max_length=512)
    description = models.TextField()
    position = models.ForeignKey('user.Position', related_name='applications', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(null=True)

    DRAFT = "draft"
    READY = "ready"
    LIVE = "live"

    STATE_CHOICES = (
        (DRAFT, "Draft"),
        (READY, "Ready"),
        (LIVE, "Live"),
    )

    state = FSMField(default=DRAFT, choices=STATE_CHOICES)

    objects = ApplicationQuerySet.as_manager()

    @transition(field=state, source=[DRAFT], target=READY)
    def approve(self):
        pass

    @transition(field=state, source=[READY], target=LIVE)
    def publish(self):
        self.published = timezone.now()

    def __str__(self):
        return self.name


class ApplicationInstance(models.Model):

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        ordering = ('updated',)

    application = models.ForeignKey(Application, related_name='instances', on_delete=models.PROTECT)
    applicant = models.ForeignKey('user.User', related_name='applications', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    submitted = models.DateTimeField(null=True)
    reviewed = models.DateTimeField(null=True)  # approved/declined

    updated = models.DateTimeField(auto_now=True)

    CREATED = "created"
    STARTED = "started"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DECLINED = "declined"

    STATE_CHOICES = (
        (CREATED, "Not Started"),
        (STARTED, "Started"),
        (SUBMITTED, "Submitted"),
        (APPROVED, "Approved"),
        (DECLINED, "Declined"),
    )

    state = FSMField(default=CREATED, choices=STATE_CHOICES)

    def create_values(self):
        for step in self.application.steps.all():
            StepValue.objects.create(application_instance=self, step=step)

    def prepare_values(self, request):
        for value in self.values.all():
            value.widget.prepare(request)

    @transition(field=state, source=[CREATED], target=STARTED)
    def start(self):
        self.started = timezone.now()

    @transition(field=state, source=[STARTED], target=SUBMITTED)
    def submit(self):
        self.submitted = timezone.now()

    @transition(field=state, source=[SUBMITTED], target=APPROVED)
    def approve(self):
        self.reviewed = timezone.now()

    @transition(field=state, source=[SUBMITTED], target=DECLINED)
    def decline(self):
        self.reviewed = timezone.now()

    @property
    def is_readonly(self):
        return bool(self.submitted) or bool(self.reviewed)


class Step(models.Model):
    application = models.ForeignKey(Application, related_name='steps', on_delete=models.PROTECT)

    number = models.PositiveIntegerField(db_index=True)
    title = models.CharField(max_length=512)
    instructions = models.TextField(blank=True)
    widget_type = models.CharField(
        'Widget Type', default='Questions', max_length=128,
        choices=[(key, key) for key in widgets]
    )
    widget_conf = YAMLField('Widget Configuration', blank=True)

    class Meta:
        ordering = ('number',)

    def __str__(self):
        return '#{} {}'.format(self.number, self.title)

    @property
    def widget(self):
        if not hasattr(self, '_widget'):
            self._widget = widgets[self.widget_type](self)
        return self._widget

    def clean(self):
        self.widget.clean_instructions()
        self.widget.clean_widget_conf()


class StepValue(models.Model):
    application_instance = models.ForeignKey(ApplicationInstance, related_name='values', on_delete=models.CASCADE)
    step = models.ForeignKey(Step, related_name='values', on_delete=models.PROTECT)
    value = JSONField(null=True)
    is_acceptable = models.BooleanField(default=False)

    class Meta:
        ordering = ('step__number',)

    @property
    def widget(self):
        if not hasattr(self, '_widget'):
            self._widget = value_widgets[self.step.widget_type](self)
        return self._widget
