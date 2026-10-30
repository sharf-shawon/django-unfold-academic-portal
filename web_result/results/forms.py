from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Student


class ResultSearchForm(forms.Form):
    student_id = forms.CharField(
        label=_("Student ID"),
        max_length=255,
        required=True,
    )
    date_of_birth = forms.DateField(
        label=_("Date of Birth"),
        required=True,
        input_formats=["%Y-%m-%d"],
    )

    def clean_student_id(self) -> str:
        student_id = self.cleaned_data["student_id"].strip()
        if not Student.objects.filter(student_id=student_id).exists():
            msg = _("The selected student id is invalid.")
            raise forms.ValidationError(msg)
        return student_id
