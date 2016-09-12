# -*- coding: utf-8 -*-
#
#    EAV-Django is a reusable Django application which implements EAV data model
#    Copyright © 2009—2010  Andrey Mikhaylenko
#
#    This file is part of EAV-Django.
#
#    EAV-Django is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    EAV-Django is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with EAV-Django.  If not, see <http://gnu.org/licenses/>.
"""
Models
~~~~~~
"""

# django
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.db.models import (BooleanField, CharField, DateField, FloatField,
                              ForeignKey, IntegerField, Model, NullBooleanField,
                              TextField)
from django.utils.translation import ugettext_lazy as _

# 3rd-party
from autoslug.fields import AutoSlugField
from autoslug.settings import slugify
#from view_shortcuts.decorators import cached_property

# this app
from managers import BaseEntityManager


__all__ = ['BaseAttribute', 'BaseChoice', 'BaseEntity', 'BaseSchema']


def slugify_attr_name(name):
    return slugify(name.replace('_', '-')).replace('-', '_')


def get_entity_lookups(entity):
    ctype = ContentType.objects.get_for_model(entity)
    return {'entity_type': ctype, 'entity_id': entity.pk}


class BaseSchema(Model):
    """
    Metadata for an attribute.
    """
    TYPE_TEXT    = 'text'
    TYPE_FLOAT   = 'float'
    TYPE_DATE    = 'date'
    TYPE_BOOLEAN = 'bool'
    TYPE_ONE     = 'one'
    TYPE_MANY    = 'many'
    TYPE_RANGE   = 'range'

    DATATYPE_CHOICES = (
        (TYPE_TEXT,    _('text')),
        (TYPE_FLOAT,   _('number')),
        (TYPE_DATE,    _('date')),
        (TYPE_BOOLEAN, _('boolean')),
        (TYPE_ONE,     _('choice')),
        (TYPE_MANY,    _('multiple choices')),
        (TYPE_RANGE,   _('numeric range')),
    )

    title    = CharField(_('title'), max_length=250, help_text=_('user-friendly attribute name'))
    name     = AutoSlugField(_('name'), max_length=250, populate_from='title',
                             editable=True, blank=True, slugify=slugify_attr_name)
    help_text = CharField(_('help text'), max_length=250, blank=True,
                          help_text=_('short description for administrator'))
    datatype = CharField(_('data type'), max_length=5, choices=DATATYPE_CHOICES)

    required = BooleanField(_('required'), default=False)
    searched = BooleanField(_('include in search'), default=False)  # i.e. full-text search? mb for text only
    filtered = BooleanField(_('include in filters'), default=False)
    sortable = BooleanField(_('allow sorting'), default=False)

    class Meta:
        abstract = True
        verbose_name, verbose_name_plural = _('schema'), _('schemata')
        ordering = ['title']

    def __unicode__(self):
        return u'%s (%s)%s' % (self.title, self.get_datatype_display(),
                                u' %s'%_('required') if self.required else '')

    def get_choices(self):
        """
        Returns a queryset of choice objects bound to this schema.
        """
        return self.choices.all()

    def get_attrs(self, entity):
        """
        Returns available attributes for given entity instance.
        Handles many-to-one relations transparently.
        """
        return self.attrs.filter(**get_entity_lookups(entity))

    def save_attr(self, entity, value):
        """
        Saves given EAV attribute with given value for given entity.

        If schema is not a choice, the value is saved to the corresponding
        Attr instance (which is created or updated).

        If schema is an cvhoice (one-to-one or many-to-one), the value is
        processed thusly:

        * if value is iterable, all Attr instances for corresponding managed choice
          schemata are updated (those with names from the value list are set to
          True, others to False). If a list item is not in available choices,
          ValueError is raised;
        * if the value is None, all corresponding Attr instances are reset to False;
        * if the value is neither a list nor None, it is wrapped into a list and
          processed as above (i.e. "foo" --> ["foo"]).
        """

        if self.datatype in (self.TYPE_ONE, self.TYPE_MANY):
            self._save_choice_attr(entity, value)
        else:
            self._save_single_attr(entity, value)

    def _save_single_attr(self, entity, value=None, schema=None,
                          create_nulls=False, extra={}):
        """
        Creates or updates an EAV attribute for given entity with given value.

        :param schema: schema for attribute. Default it current schema instance.
        :param create_nulls: boolean: if True, even attributes with value=None
            are created (by default they are skipped).
        :param extra: dict: additional data for Attr instance (e.g. title).
        """
        # If schema is not many-to-one, the value is saved to the corresponding
        # Attr instance (which is created or updated).

        schema = schema or self
        lookups = dict(get_entity_lookups(entity), schema=schema, **extra)
        try:
            attr = self.attrs.get(**lookups)
        except self.attrs.model.DoesNotExist:
            attr = self.attrs.model(**lookups)
        if create_nulls or value != attr.value:
            attr.value = value
            for k,v in extra.items():
                setattr(attr, k, v)
            attr.save()

    def _save_choice_attr(self, entity, value):
        """
        Creates or updates BaseChoice(s) attribute(s) for given entity.
        """

        # value can be None to reset choices from schema
        if value == None:
            value = []

        if not hasattr(value, '__iter__'):
            value = [value]

        if self.datatype == self.TYPE_ONE and len(value) > 1:
            raise TypeError('Cannot assign multiple values "%s" to TYPE_ONE '
                            'must be only one BaseChoice instance.'
                            % value)

        if not all(isinstance(x, BaseChoice) for x in value):
            raise TypeError('Cannot assign "%s": "Attr.choice" '
                            'must be a BaseChoice instance.'
                            % value)

        # drop all attributes for this entity/schema pair
        self.get_attrs(entity).delete()

        # Attr instances for corresponding managed choice schemata are updated
        for choice in value:
            self._save_single_attr(
                entity,
                schema = self,
                create_nulls = True,
                extra = {'choice': choice}
            )


class BaseEntity(Model):
    """
    Entity, the "E" in EAV. This model is abstract and must be subclassed.
    See tests for examples.
    """

    objects = BaseEntityManager()

    class Meta:
        abstract = True

    def save(self, force_eav=False, **kwargs):
        """
        Saves entity instance and creates/updates related attribute instances.

        :param eav: if True (default), EAV attributes are saved along with entity.
        """
        # save entity
        super(BaseEntity, self).save(**kwargs)

        # TODO: think about use cases; are we doing it right?
        #if not self.check_eav_allowed():
        #    import warnings
        #    warnings.warn('EAV attributes are going to be saved along with entity'
        #                  ' despite %s.check_eav_allowed() returned False.'
        #                  % type(self), RuntimeWarning)


        # create/update EAV attributes
        for schema in self.get_schemata():
            value = getattr(self, schema.name, None)
            schema.save_attr(self, value)

    def __getattr__(self, name):
        if not name.startswith('_'):
            if name in self.get_schema_names():
                schema = self.get_schema(name)
                attrs = schema.get_attrs(self)
                if schema.datatype == schema.TYPE_MANY:
                    return [a.value for a in attrs if a.value]
                else:
                    return attrs[0].value if attrs else None
        raise AttributeError('%s does not have attribute named "%s".' %
                             (self._meta.object_name, name))

    def __iter__(self):
        "Iterates over non-empty EAV attributes. Normal fields are not included."
        for attr in self.attrs.select_related():
            if getattr(self, attr.schema.name, None):
                yield attr

    @classmethod
    def get_schemata_for_model(cls):
        return NotImplementedError('BaseEntity subclasses must define method '
                                   '"get_schemata_for_model" which returns a '
                                   'QuerySet for a BaseSchema subclass.')

    def get_schemata_for_instance(self, qs):
        return qs

    def get_schemata(self):
        if hasattr(self, '_schemata_cache') and self._schemata_cache is not None:
            return self._schemata_cache
        all_schemata = self.get_schemata_for_model().select_related()
        self._schemata_cache = self.get_schemata_for_instance(all_schemata)
        self._schemata_cache_dict = dict((s.name, s) for s in self._schemata_cache)
        return self._schemata_cache

    def get_schema_names(self):
        if not hasattr(self, '_schemata_cache_dict'):
            self.get_schemata()
        return self._schemata_cache_dict.keys()

    def get_schema(self, name):
        if not hasattr(self, '_schemata_cache_dict'):
            self.get_schemata()
        return self._schemata_cache_dict[name]

    def get_schema_by_id(self, schema_id):
        for schema in self.get_schemata():
            if schema.pk == schema_id:
                return schema

    def check_eav_allowed(self):
        """
        Returns True if entity instance allows EAV attributes to be attached.

        Can be useful if some external data is required to determine available
        schemata and that data may be missing. In such cases this method should
        be overloaded to check whether the data is available.
        """
        return True

    def is_valid(self):
        "Returns True if attributes and their values conform with schema."

        raise NotImplementedError()

        '''
        schemata = self.rubric.schemata.all()
        return all(x.is_valid for x in self.attributes)
        # 1. check if all required attributes are present
        for schema in schemata:
            pass
        # 2. check if all attributes have appropriate values
        for schema in schemata:
            pass
        return True
        '''


class BaseChoice(Model):
    """ Base class for choices.  Concrete choice class must overload the
    `schema` attribute.
    """
    title = CharField(max_length=100)
    schema = NotImplemented

    class Meta:
        abstract = True
        ordering = ('title',)

    def __unicode__(self):
        return self.title   #u'%s "%s"' % (self.schema.title, self.title)


class BaseAttribute(Model):
    """ Base class for choices.  Concrete choice class must overload the
    `schema` and `choice` attributes.
    """
    entity_type = ForeignKey(ContentType)
    entity_id = IntegerField()
    entity = fields.GenericForeignKey(ct_field="entity_type", fk_field='entity_id')

    value_text = TextField(blank=True, null=True)
    value_float = FloatField(blank=True, null=True)
    value_date = DateField(blank=True, null=True)
    value_bool = NullBooleanField(blank=True)    # TODO: ensure that form invalidates null booleans (??)
    value_range_min = FloatField(blank=True, null=True)
    value_range_max = FloatField(blank=True, null=True)

    schema = NotImplemented    # must be FK
    choice = NotImplemented    # must be nullable FK

    class Meta:
        abstract = True
        verbose_name, verbose_name_plural = _('attribute'), _('attributes')
        ordering = ['entity_type', 'entity_id', 'schema']
        unique_together = ('entity_type', 'entity_id', 'schema', 'choice')

    def __unicode__(self):
        return u'%s: %s "%s"' % (self.entity, self.schema.title, self.value)

    def _get_value(self):
        if self.schema.datatype in (self.schema.TYPE_ONE, self.schema.TYPE_MANY):
            return self.choice
        if self.schema.datatype == self.schema.TYPE_RANGE:
            names = ('value_range_%s' % x for x in ('min', 'max'))
            value = tuple(getattr(self, x, None) for x in names)
            return None if value == (None, None) else value
        return getattr(self, 'value_%s' % self.schema.datatype)

    def _set_value(self, new_value):
        if self.schema.datatype == self.schema.TYPE_RANGE:
            new_value = new_value or (None, None)

            # validate range value -- expecting a tuple of two numbers
            try:
                validate_range_value(new_value)
            except (TypeError, ValueError):
                raise

            for k,v in zip('min max'.split(), new_value):
                v = v if v is None else float(v)
                setattr(self, 'value_range_%s' % k, v)
        else:
            setattr(self, 'value_%s' % self.schema.datatype, new_value)

    value = property(_get_value, _set_value)


def validate_range_value(value):
    """
    Validates given value against `Schema.TYPE_RANGE` data type. Raises
    TypeError or ValueError if something is wrong. Returns None if everything
    is OK.
    """
    if value == (None, None):
        return

    if not hasattr(value, '__iter__'):
        raise TypeError('Range value must be an iterable, got "%s".' % value)
    if not 2 == len(value):
        raise ValueError('Range value must consist of two elements, got %d.' %
                         len(value))
    if not all(isinstance(x, (int,float)) for x in value):
        raise TypeError('Range value must consist of two numbers, got "%s" '
                        'and "%s" instead.' % value)
    if not value[0] <= value[1]:
        raise ValueError('Range must consist of min and max values (min <= '
                         'max) but got "%s" and "%s" instead.' % value)
    return


# xxx catch signal Attr.post_save() --> update attr.item.attribute_cache (JSONField or such)
