from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, validators, HiddenField
from app.modules.dataset.forms import BaseDataSetForm


class ImageForm(FlaskForm):
    title = StringField("Title", [validators.Optional(), validators.Length(max=120)])
    desc = StringField("Description", [validators.Optional(), validators.Length(max=1000)])
    filename = HiddenField("Filename", [validators.DataRequired()])

    class Meta:
        csrf = False


class ImageDatasetForm(BaseDataSetForm):
    images = FieldList(FormField(ImageForm), min_entries=1)

    def get_images(self):
        return self.images
