from django.db.models.fields import Field as DefaultField

class Field(DefaultField):
  def __init__(self, verbose_name=None, name=None, db_comment=None, **kwargs):
    # comment to be added in database schema
    self.db_comment = db_comment
    super(Field, self).__init__(verbose_name, name, **kwargs)
