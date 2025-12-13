from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, HiddenField, StringField, validators

from app.modules.dataset.forms import BaseDataSetForm


class AudioForm(FlaskForm):
    title = StringField("Title", [validators.Optional(), validators.Length(max=120)])
    desc = StringField("Description", [validators.Optional(), validators.Length(max=1000)])
    filename = HiddenField("Filename", [validators.DataRequired()])

    class Meta:
        csrf = False


class AudioDatasetForm(BaseDataSetForm):
    audios = FieldList(FormField(AudioForm), min_entries=1)

    def get_audios(self):
        return self.audios
