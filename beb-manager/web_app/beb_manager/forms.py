import datetime

from beb_lib.domain_entities.supporting import Priority
import beb_lib.model.exceptions as beb_exceptions
from beb_lib.model.model import Model
from colorful.forms import RGBColorField
from colorful.widgets import ColorFieldWidget
from django import forms
from django.contrib.auth.models import User
from tempus_dominus.widgets import DateTimePicker

from web_app import settings

MODEL = Model(settings.BEB_LIB_DATABASE_PATH)


class SingleInputForm(forms.Form):
    name = forms.CharField(max_length=100)
    can_read = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), required=False)
    can_write = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), required=False)


class CardForm(forms.Form):
    def __init__(self, user_id, board_id, *args, **kwargs):
        super(CardForm, self).__init__(*args, **kwargs)
        try:
            tags = MODEL.tag_read()
        except beb_exceptions.TagDoesNotExistError:
            tags = []
        tags_tuple = [(tag.unique_id, tag.name) for tag in tags]
        tags_tuple.insert(0, ('', 'n.s.'))

        try:
            cards = MODEL.get_cards_in_board(board_id, user_id)
        except beb_exceptions.CardDoesNotExistError:
            cards = []
        
        card_lists = MODEL.list_read(board_id, request_user_id=user_id)

        cards_tuple = [(card.unique_id, card.name) for card in cards]
        cards_tuple.insert(0, ('', 'n.s.'))

        lists_tuple = [(card_list.unique_id, card_list.name) for card_list in card_lists]

        self.fields['tags'] = forms.MultipleChoiceField(choices=tags_tuple, required=False)
        self.fields['card_list'] = forms.ChoiceField(choices=lists_tuple, required=False)
        self.fields['children_cards'] = forms.MultipleChoiceField(choices=cards_tuple, required=False)

    name = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Card title'}))
    description = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Card description'}))
    tags = forms.MultipleChoiceField()
    card_list = forms.ChoiceField()
    priority = forms.ChoiceField(choices=[(p.value, Priority(p).name) for p in Priority], required=False)
    expiration_date = forms.DateTimeField(widget=DateTimePicker(options={'minDate': (datetime.date.today() +
                                                                                     datetime.timedelta(
                                                                                         days=1)).strftime('%Y-%m-%d'),
                                                                         'useCurrent': False, }),
                                          required=False)
    children_cards = forms.MultipleChoiceField()
    assignee = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    can_read = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)
    can_write = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)

    interval = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': '5 minutes'}), required=False)
    start_repeat_at = forms.DateTimeField(
        widget=DateTimePicker(options={'minDate': (datetime.date.today()).strftime('%Y-%m-%d'),
                                       'useCurrent': True,
                                       }
                              ),
        required=False
    )


class CardFormWithoutLists(CardForm):
    def __init__(self, *args, **kwargs):
        super(CardFormWithoutLists, self).__init__(*args, **kwargs)
        self.fields.pop('card_list')


class TagForm(forms.Form):
    name = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'placeholder': 'Tag title'}), required=True)
    color = RGBColorField(widget=ColorFieldWidget(colors=['#61BD4F', '#F2D900', '#FFA111', '#EB5942',
                                                          '#C470DF', '#0576BF', '#00C1E1', '#4FEB9A',
                                                          '#FF72CA', '#355163', '#B3BEC4']))
