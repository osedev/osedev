#  Copyright (C) 2017 Lex Berezhny <lex@damoti.com>.
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

from datetime import timedelta, date
from django.forms import BooleanField, ValidationError
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.db.models.aggregates import Count
from .models import User, Position, UserPosition, Term
from allauth.account.models import EmailAddress


class UserChangeForm(BaseUserChangeForm):
    verify_email = BooleanField(label=_("Send verification email?"), initial=False, required=False)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email and EmailAddress.objects.filter(email__iexact=email).exclude(user=self.instance).exists():
            raise ValidationError(_("This email is already associated with another user."))
        return email


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'verify_email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_osedev', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')

    def save_model(self, request, user, form, change):
        super().save_model(request, user, form, change)
        if user.email:
            EmailAddress.objects.filter(user=user).update(primary=False)
            email = EmailAddress.objects.filter(email__iexact=user.email).first()
            if not email:
                EmailAddress.objects.create(
                    user=user, email=user.email, primary=True, verified=False
                )
            elif not email.primary:
                email.primary = True
                email.save()
        else:
            EmailAddress.objects.filter(user=user).delete()


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass


class TermInline(admin.TabularInline):
    model = Term


@admin.register(UserPosition)
class UserPositionAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'term', 'terms_count')
    inlines = (TermInline,)
    fields = ('user', 'position')

    def get_readonly_fields(self, request, obj=None):
        return self.fields if obj else ((),)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user_position = form.instance
        user_position.term = user_position.terms.order_by('-start').first()
        user_position.save()

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(terms_count=Count('terms'))

    def terms_count(self, obj):
        return obj.terms_count
    terms_count.short_description = 'Terms Served'

    def add_term(self, request, queryset):
        terms_extended = 0
        for user_position in queryset:
            start_term = user_position.term
            if start_term:
                new_start = start_term.end + timedelta(days=1)
            else:
                new_start = date.today()
            new_end = new_start + timedelta(days=user_position.position.weeks * 7)
            user_position.term = Term.objects.create(
                user_position=user_position,
                start=new_start, end=new_end
            )
            user_position.save()
            terms_extended += 1
        self.message_user(request, "{} successfully linked.".format(terms_extended))
    add_term.short_description = "Extend selected user positions with new terms"

    actions = [add_term]
