from django import forms


class SearchForm(forms.Form):
    ROOM_STYLE = (
        ('standard', 'Standard'),
        ("delux", "Delux"),
        ("family", "Family Suite"),
        ("business", "Business Suite")
    )
    check_in = forms.DateField()
    check_out = forms.DateField()
    room_type = forms.ChoiceField(choices=ROOM_STYLE)