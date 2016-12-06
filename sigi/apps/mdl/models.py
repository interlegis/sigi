# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class CourseStats(models.Model):
    # databaseview: (postgresql dialect):
    # -- View: sigi_course_stats
    #
    # DROP VIEW sigi_course_stats;
    #
    # CREATE OR REPLACE VIEW sigi_course_stats AS
    #  SELECT cc.id AS categoryid, c.id AS courseid,
    #         CASE
    #             WHEN e.enrol = 'ilbeadtutorado' AND ue.status = 1 THEN 'N' -- Rejeitada
    #             WHEN e.enrol = 'ilbead' AND ue.timeend > date_part('epoch', now()) THEN 'C' -- Em curso
    #             WHEN e.enrol = 'ilbead' and ue.timeend < date_part('epoch', now()) and co.timecompleted is null and gg.finalgrade is null then 'L' -- Abandono
    #             WHEN (co.timestarted = 0 OR co.timestarted IS NULL) AND gg.finalgrade IS NOT NULL THEN 'R' -- Reprovada
    #             WHEN co.timestarted = 0 OR co.timestarted IS NULL THEN 'L' -- Abandono
    #             WHEN co.timestarted > 0 AND co.timecompleted IS NULL THEN 'R' -- Reprovado
    #             WHEN co.timecompleted IS NOT NULL THEN 'A' -- Aprovado
    #             ELSE 'I' -- Indeterminado
    #         END AS completionstatus, count(ue.id) AS usercount, avg(gg.finalgrade) as gradeaverage
    #    FROM mdl_course_categories cc
    #    JOIN mdl_course c ON c.category = cc.id
    #    JOIN mdl_enrol e ON e.courseid = c.id
    #    JOIN mdl_user_enrolments ue ON ue.enrolid = e.id
    #    JOIN mdl_grade_items gi ON gi.courseid = c.id AND gi.itemtype = 'course'
    #    LEFT JOIN mdl_grade_grades gg ON gg.itemid = gi.id AND gg.userid = ue.userid
    #    LEFT JOIN mdl_course_completions co ON co.userid = ue.userid AND co.course = c.id
    #   GROUP BY cc.id, c.id, completionstatus;

    COMPLETIONSTATUS_CHOICES = (
        ('N', u'Matrículas rejeitadas'),
        ('C', u'Em curso'),
        ('R', u'Reprovação'),
        ('L', u'Abandono'),
        ('A', u'Aprovação'),
        ('I', u'Indeterminado'),)

    category = models.ForeignKey('CourseCategories', db_column='categoryid')
    course = models.ForeignKey('Course', db_column='courseid')
    completionstatus = models.CharField(max_length=1, choices=COMPLETIONSTATUS_CHOICES)
    usercount = models.IntegerField()
    gradeaverage = models.FloatField()

    class Meta:
        managed = False
        db_table = 'sigi_course_stats'

    def __unicode__(self):
        return '%s - %s: %s' % (self.category.name, self.course.fullname, self.usercount)


class Cohort(models.Model):
    id = models.BigIntegerField(primary_key=True)
    context = models.ForeignKey('Context', db_column='contextid')
    name = models.CharField(max_length=254)
    idnumber = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField()
    component = models.CharField(max_length=100)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    visible = models.SmallIntegerField()
    # Manytomany
    members = models.ManyToManyField('User', through='CohortMembers')

    class Meta:
        managed = False
        db_table = 'mdl_cohort'

    def __unicode__(self):
        return self.name


class CohortMembers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    cohort = models.ForeignKey('Cohort', db_column='cohortid')
    user = models.ForeignKey('User', db_column='userid')
    timeadded = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_cohort_members'


class Context(models.Model):
    CONTEXT_SYSTEM = 10  # System context level - only one instance in every system
    CONTEXT_USER = 30  # User context level - one instance for each user describing what others can do to user
    CONTEXT_COURSECAT = 40  # Course category context level - one instance for each category
    CONTEXT_COURSE = 50  # Course context level - one instances for each course
    CONTEXT_MODULE = 70  # Course module context level - one instance for each course module
    CONTEXT_BLOCK = 80  # Block context level - one instance for each block, sticky blocks are tricky
    # because ppl think they should be able to override them at lower contexts.
    # Any other context level instance can be parent of block context.

    id = models.BigIntegerField(primary_key=True)
    contextlevel = models.BigIntegerField()
    instanceid = models.BigIntegerField()
    path = models.CharField(max_length=255, blank=True)
    depth = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_context'

    def __unicode__(self):
        return self.path


class Course(models.Model):
    id = models.BigIntegerField(primary_key=True)
    category = models.ForeignKey('CourseCategories', db_column='category', related_name='courses')
    sortorder = models.BigIntegerField()
    fullname = models.CharField(max_length=254)
    shortname = models.CharField(max_length=255)
    idnumber = models.CharField(max_length=100)
    summary = models.TextField(blank=True)
    format = models.CharField(max_length=21)
    showgrades = models.SmallIntegerField()
    newsitems = models.IntegerField()
    startdate = models.BigIntegerField()
    marker = models.BigIntegerField()
    maxbytes = models.BigIntegerField()
    showreports = models.SmallIntegerField()
    visible = models.SmallIntegerField()
    groupmode = models.SmallIntegerField()
    groupmodeforce = models.SmallIntegerField()
    lang = models.CharField(max_length=30)
    theme = models.CharField(max_length=50)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    requested = models.SmallIntegerField()
    defaultgroupingid = models.BigIntegerField()
    enrolmax = models.BigIntegerField()
    enablecompletion = models.SmallIntegerField()
    legacyfiles = models.SmallIntegerField()
    summaryformat = models.SmallIntegerField()
    completionnotify = models.SmallIntegerField()
    visibleold = models.SmallIntegerField()
    calendartype = models.CharField(max_length=30)
    cacherev = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_course'
        ordering = ['sortorder', ]

    def __unicode__(self):
        return self.fullname

    def total_alunos(self):
        return sum(e.user_enrolments.count() for e in self.enrols.all())

    def total_ativos(self):
        return sum(e.user_enrolments.filter(status=0).count() for e in self.enrols.all())

    def get_matriculas(self):
        q = UserEnrolments.objects.none()
        for e in self.enrols.all():
            q = q | e.user_enrolments.all()
        return q


class CourseCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('CourseCategories', db_column='parent', related_name='children')
    sortorder = models.BigIntegerField()
    coursecount = models.BigIntegerField()
    visible = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    depth = models.BigIntegerField()
    path = models.CharField(max_length=255)
    theme = models.CharField(max_length=50, blank=True)
    descriptionformat = models.SmallIntegerField()
    visibleold = models.SmallIntegerField()
    idnumber = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_categories'
        ordering = ['sortorder', ]

    def __unicode__(self):
        return self.name

    def context(self):
        return Context.objects.get(instanceid=self.id, contextlevel=Context.CONTEXT_COURSECAT)

    def total_turmas(self):
        return self.coursecount + sum([c.coursecount for c in self.children.all()])

    def total_alunos(self):
        total = 0
        total = total + sum(c.total_alunos() for c in self.courses.all())
        total = total + sum(c.total_alunos() for c in self.children.all())
        return total

    def cohortids(self):
        cids = [c.pk for c in self.context().cohort_set.all()]
        for c in self.children.all():
            cids = cids + c.cohortids()
        return cids

    def total_alunos_cohort(self):
        return sum([c.members.distinct().count() for c in Cohort.objects.filter(pk__in=self.cohortids())])

    def get_all_courses(self, only_visible=False):
        if only_visible:
            q = self.courses.filter(visible=1)
        else:
            q = self.courses.all()
        for c in self.children.all():
            q = q | c.get_all_courses(only_visible=only_visible)
        return q


class CourseCompletions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey('User', db_column='userid')
    course = models.ForeignKey('Course', db_column='course')
    timeenrolled = models.BigIntegerField()
    timestarted = models.BigIntegerField()
    timecompleted = models.BigIntegerField(blank=True, null=True)
    reaggregate = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_course_completions'


class Enrol(models.Model):
    id = models.BigIntegerField(primary_key=True)
    enrol = models.CharField(max_length=20)
    status = models.BigIntegerField()
    course = models.ForeignKey('Course', db_column='courseid', related_name='enrols')
    sortorder = models.BigIntegerField()
    name = models.CharField(max_length=255, blank=True)
    enrolperiod = models.BigIntegerField(blank=True, null=True)
    enrolstartdate = models.BigIntegerField(blank=True, null=True)
    enrolenddate = models.BigIntegerField(blank=True, null=True)
    expirynotify = models.SmallIntegerField(blank=True, null=True)
    expirythreshold = models.BigIntegerField(blank=True, null=True)
    notifyall = models.SmallIntegerField(blank=True, null=True)
    password = models.CharField(max_length=50, blank=True)
    cost = models.CharField(max_length=20, blank=True)
    currency = models.CharField(max_length=3, blank=True)
    roleid = models.BigIntegerField(blank=True, null=True)
    customint1 = models.BigIntegerField(blank=True, null=True)
    customint2 = models.BigIntegerField(blank=True, null=True)
    customint3 = models.BigIntegerField(blank=True, null=True)
    customint4 = models.BigIntegerField(blank=True, null=True)
    customchar1 = models.CharField(max_length=255, blank=True)
    customchar2 = models.CharField(max_length=255, blank=True)
    customdec1 = models.DecimalField(max_digits=12, decimal_places=7, blank=True, null=True)
    customdec2 = models.DecimalField(max_digits=12, decimal_places=7, blank=True, null=True)
    customtext1 = models.TextField(blank=True)
    customtext2 = models.TextField(blank=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    customint5 = models.BigIntegerField(blank=True, null=True)
    customint6 = models.BigIntegerField(blank=True, null=True)
    customint7 = models.BigIntegerField(blank=True, null=True)
    customint8 = models.BigIntegerField(blank=True, null=True)
    customchar3 = models.CharField(max_length=1333, blank=True)
    customtext3 = models.TextField(blank=True)
    customtext4 = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_enrol'
        ordering = ['sortorder', ]

    def __unicode__(self):
        if not self.name:
            return self.enrol
        return self.name


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    auth = models.CharField(max_length=20)
    confirmed = models.SmallIntegerField()
    policyagreed = models.SmallIntegerField()
    deleted = models.SmallIntegerField()
    mnethostid = models.BigIntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    emailstop = models.SmallIntegerField()
    icq = models.CharField(max_length=15)
    skype = models.CharField(max_length=50)
    yahoo = models.CharField(max_length=50)
    aim = models.CharField(max_length=50)
    msn = models.CharField(max_length=50)
    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20)
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=2)
    lang = models.CharField(max_length=30)
    theme = models.CharField(max_length=50)
    timezone = models.CharField(max_length=100)
    firstaccess = models.BigIntegerField()
    lastaccess = models.BigIntegerField()
    lastlogin = models.BigIntegerField()
    currentlogin = models.BigIntegerField()
    lastip = models.CharField(max_length=45)
    secret = models.CharField(max_length=15)
    picture = models.BigIntegerField()
    url = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    mailformat = models.SmallIntegerField()
    maildigest = models.SmallIntegerField()
    maildisplay = models.SmallIntegerField()
    autosubscribe = models.SmallIntegerField()
    trackforums = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    trustbitmask = models.BigIntegerField()
    imagealt = models.CharField(max_length=255, blank=True)
    idnumber = models.CharField(max_length=255)
    descriptionformat = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    suspended = models.SmallIntegerField()
    lastnamephonetic = models.CharField(max_length=255, blank=True)
    firstnamephonetic = models.CharField(max_length=255, blank=True)
    middlename = models.CharField(max_length=255, blank=True)
    alternatename = models.CharField(max_length=255, blank=True)
    calendartype = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'mdl_user'

    def __unicode__(self):
        return u'%s %s' % (self.firstname, self.lastname)


class UserEnrolments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    status = models.BigIntegerField()
    enrol = models.ForeignKey('Enrol', db_column='enrolid', related_name='user_enrolments')
    user = models.ForeignKey('User', db_column='userid', related_name='Enrolments')
    timestart = models.BigIntegerField()
    timeend = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_user_enrolments'
