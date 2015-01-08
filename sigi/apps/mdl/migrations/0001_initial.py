# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cohort',
            fields=[
            ],
            options={
                'db_table': 'mdl_cohort',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CohortMembers',
            fields=[
            ],
            options={
                'db_table': 'mdl_cohort_members',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Context',
            fields=[
            ],
            options={
                'db_table': 'mdl_context',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
            ],
            options={
                'ordering': ['sortorder'],
                'db_table': 'mdl_course',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseCategories',
            fields=[
            ],
            options={
                'ordering': ['sortorder'],
                'db_table': 'mdl_course_categories',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseCompletions',
            fields=[
            ],
            options={
                'db_table': 'mdl_course_completions',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseStats',
            fields=[
            ],
            options={
                'db_table': 'sigi_course_stats',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Enrol',
            fields=[
            ],
            options={
                'ordering': ['sortorder'],
                'db_table': 'mdl_enrol',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'db_table': 'mdl_user',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserEnrolments',
            fields=[
            ],
            options={
                'db_table': 'mdl_user_enrolments',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
