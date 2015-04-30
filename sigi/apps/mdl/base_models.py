# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AdodbLogsql(models.Model):
    id = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    sql0 = models.CharField(max_length=250)
    sql1 = models.TextField(blank=True)
    params = models.TextField(blank=True)
    tracer = models.TextField(blank=True)
    timer = models.DecimalField(max_digits=16, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'adodb_logsql'


class BackupRoleAssignments(models.Model):
    id = models.BigIntegerField()
    roleid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    userid = models.BigIntegerField()
    hidden = models.SmallIntegerField()
    timestart = models.BigIntegerField()
    timeend = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    enrol = models.CharField(max_length=20)
    sortorder = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'backup_role_assignments'


class BkpLista(models.Model):
    id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bkp_lista'


class IbgeMunicipio(models.Model):
    codigo_ibge = models.IntegerField()
    nome = models.CharField(max_length=50)
    uf_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ibge_municipio'


class IbgeUnidadefederativa(models.Model):
    codigo_ibge = models.IntegerField()
    nome = models.CharField(max_length=25)
    sigla = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ibge_unidadefederativa'


class MdlAssign(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    introformat = models.SmallIntegerField()
    alwaysshowdescription = models.SmallIntegerField()
    nosubmissions = models.SmallIntegerField()
    submissiondrafts = models.SmallIntegerField()
    sendnotifications = models.SmallIntegerField()
    sendlatenotifications = models.SmallIntegerField()
    duedate = models.BigIntegerField()
    allowsubmissionsfromdate = models.BigIntegerField()
    grade = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    requiresubmissionstatement = models.SmallIntegerField()
    completionsubmit = models.SmallIntegerField()
    cutoffdate = models.BigIntegerField()
    teamsubmission = models.SmallIntegerField()
    requireallteammemberssubmit = models.SmallIntegerField()
    teamsubmissiongroupingid = models.BigIntegerField()
    blindmarking = models.SmallIntegerField()
    revealidentities = models.SmallIntegerField()
    attemptreopenmethod = models.CharField(max_length=10)
    maxattempts = models.IntegerField()
    markingworkflow = models.SmallIntegerField()
    markingallocation = models.SmallIntegerField()
    sendstudentnotifications = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assign'


class MdlAssignGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    grader = models.BigIntegerField()
    grade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    attemptnumber = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assign_grades'


class MdlAssignPluginConfig(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    plugin = models.CharField(max_length=28)
    subtype = models.CharField(max_length=28)
    name = models.CharField(max_length=28)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_assign_plugin_config'


class MdlAssignSubmission(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    status = models.CharField(max_length=10, blank=True)
    groupid = models.BigIntegerField()
    attemptnumber = models.BigIntegerField()
    latest = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assign_submission'


class MdlAssignUserFlags(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    assignment = models.BigIntegerField()
    locked = models.BigIntegerField()
    mailed = models.SmallIntegerField()
    extensionduedate = models.BigIntegerField()
    workflowstate = models.CharField(max_length=20, blank=True)
    allocatedmarker = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assign_user_flags'


class MdlAssignUserMapping(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    userid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assign_user_mapping'


class MdlAssignfeedbackComments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    grade = models.BigIntegerField()
    commenttext = models.TextField(blank=True)
    commentformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignfeedback_comments'


class MdlAssignfeedbackEditpdfAnnot(models.Model):
    id = models.BigIntegerField(primary_key=True)
    gradeid = models.BigIntegerField()
    pageno = models.BigIntegerField()
    x = models.BigIntegerField(blank=True, null=True)
    y = models.BigIntegerField(blank=True, null=True)
    endx = models.BigIntegerField(blank=True, null=True)
    endy = models.BigIntegerField(blank=True, null=True)
    path = models.TextField(blank=True)
    type = models.CharField(max_length=10, blank=True)
    colour = models.CharField(max_length=10, blank=True)
    draft = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignfeedback_editpdf_annot'


class MdlAssignfeedbackEditpdfCmnt(models.Model):
    id = models.BigIntegerField(primary_key=True)
    gradeid = models.BigIntegerField()
    x = models.BigIntegerField(blank=True, null=True)
    y = models.BigIntegerField(blank=True, null=True)
    width = models.BigIntegerField(blank=True, null=True)
    rawtext = models.TextField(blank=True)
    pageno = models.BigIntegerField()
    colour = models.CharField(max_length=10, blank=True)
    draft = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignfeedback_editpdf_cmnt'


class MdlAssignfeedbackEditpdfQuick(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    rawtext = models.TextField()
    width = models.BigIntegerField()
    colour = models.CharField(max_length=10, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_assignfeedback_editpdf_quick'


class MdlAssignfeedbackFile(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    grade = models.BigIntegerField()
    numfiles = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignfeedback_file'


class MdlAssignment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    introformat = models.SmallIntegerField()
    assignmenttype = models.CharField(max_length=50)
    resubmit = models.SmallIntegerField()
    preventlate = models.SmallIntegerField()
    emailteachers = models.SmallIntegerField()
    var1 = models.BigIntegerField(blank=True, null=True)
    var2 = models.BigIntegerField(blank=True, null=True)
    var3 = models.BigIntegerField(blank=True, null=True)
    var4 = models.BigIntegerField(blank=True, null=True)
    var5 = models.BigIntegerField(blank=True, null=True)
    maxbytes = models.BigIntegerField()
    timedue = models.BigIntegerField()
    timeavailable = models.BigIntegerField()
    grade = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignment'


class MdlAssignmentSubmissions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    numfiles = models.BigIntegerField()
    data1 = models.TextField(blank=True)
    data2 = models.TextField(blank=True)
    grade = models.BigIntegerField()
    submissioncomment = models.TextField()
    format = models.SmallIntegerField()
    teacher = models.BigIntegerField()
    timemarked = models.BigIntegerField()
    mailed = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignment_submissions'


class MdlAssignmentUpgrade(models.Model):
    id = models.BigIntegerField(primary_key=True)
    oldcmid = models.BigIntegerField()
    oldinstance = models.BigIntegerField()
    newcmid = models.BigIntegerField()
    newinstance = models.BigIntegerField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignment_upgrade'


class MdlAssignsubmissionFile(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    submission = models.BigIntegerField()
    numfiles = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignsubmission_file'


class MdlAssignsubmissionOnlinetext(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    submission = models.BigIntegerField()
    onlinetext = models.TextField(blank=True)
    onlineformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assignsubmission_onlinetext'


class MdlAttendance(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255, blank=True)
    grade = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_attendance'


class MdlAttendanceLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    sessionid = models.BigIntegerField()
    studentid = models.BigIntegerField()
    statusid = models.BigIntegerField()
    statusset = models.CharField(max_length=100, blank=True)
    timetaken = models.BigIntegerField()
    takenby = models.BigIntegerField()
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_attendance_log'


class MdlAttendanceSessions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    attendanceid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    sessdate = models.BigIntegerField()
    duration = models.BigIntegerField()
    lasttaken = models.BigIntegerField(blank=True, null=True)
    lasttakenby = models.BigIntegerField()
    timemodified = models.BigIntegerField(blank=True, null=True)
    description = models.TextField()
    descriptionformat = models.SmallIntegerField()
    studentscanmark = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_attendance_sessions'


class MdlAttendanceStatuses(models.Model):
    id = models.BigIntegerField(primary_key=True)
    attendanceid = models.BigIntegerField()
    acronym = models.CharField(max_length=2)
    description = models.CharField(max_length=30)
    grade = models.SmallIntegerField()
    visible = models.SmallIntegerField()
    deleted = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_attendance_statuses'


class MdlBackupControllers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    backupid = models.CharField(unique=True, max_length=32)
    type = models.CharField(max_length=10)
    itemid = models.BigIntegerField()
    format = models.CharField(max_length=20)
    interactive = models.SmallIntegerField()
    purpose = models.SmallIntegerField()
    userid = models.BigIntegerField()
    status = models.SmallIntegerField()
    execution = models.SmallIntegerField()
    executiontime = models.BigIntegerField()
    checksum = models.CharField(max_length=32)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    controller = models.TextField()
    operation = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'mdl_backup_controllers'


class MdlBackupCourses(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField(unique=True)
    laststarttime = models.BigIntegerField()
    lastendtime = models.BigIntegerField()
    laststatus = models.CharField(max_length=1)
    nextstarttime = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_backup_courses'


class MdlBackupLogs(models.Model):
    id = models.BigIntegerField(primary_key=True)
    backupid = models.CharField(max_length=32)
    loglevel = models.SmallIntegerField()
    message = models.TextField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_backup_logs'


class MdlBadge(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    usercreated = models.BigIntegerField()
    usermodified = models.BigIntegerField()
    issuername = models.CharField(max_length=255)
    issuerurl = models.CharField(max_length=255)
    issuercontact = models.CharField(max_length=255, blank=True)
    expiredate = models.BigIntegerField(blank=True, null=True)
    expireperiod = models.BigIntegerField(blank=True, null=True)
    type = models.SmallIntegerField()
    courseid = models.BigIntegerField(blank=True, null=True)
    message = models.TextField()
    messagesubject = models.TextField()
    attachment = models.SmallIntegerField()
    notification = models.SmallIntegerField()
    status = models.SmallIntegerField()
    nextcron = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_badge'


class MdlBadgeBackpack(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    email = models.CharField(max_length=100)
    backpackurl = models.CharField(max_length=255)
    backpackuid = models.BigIntegerField()
    autosync = models.SmallIntegerField()
    password = models.CharField(max_length=50, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_badge_backpack'


class MdlBadgeCriteria(models.Model):
    id = models.BigIntegerField(primary_key=True)
    badgeid = models.BigIntegerField()
    criteriatype = models.BigIntegerField(blank=True, null=True)
    method = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_badge_criteria'


class MdlBadgeCriteriaMet(models.Model):
    id = models.BigIntegerField(primary_key=True)
    issuedid = models.BigIntegerField(blank=True, null=True)
    critid = models.BigIntegerField()
    userid = models.BigIntegerField()
    datemet = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_badge_criteria_met'


class MdlBadgeCriteriaParam(models.Model):
    id = models.BigIntegerField(primary_key=True)
    critid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_badge_criteria_param'


class MdlBadgeExternal(models.Model):
    id = models.BigIntegerField(primary_key=True)
    backpackid = models.BigIntegerField()
    collectionid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_badge_external'


class MdlBadgeIssued(models.Model):
    id = models.BigIntegerField(primary_key=True)
    badgeid = models.BigIntegerField()
    userid = models.BigIntegerField()
    uniquehash = models.TextField()
    dateissued = models.BigIntegerField()
    dateexpire = models.BigIntegerField(blank=True, null=True)
    visible = models.SmallIntegerField()
    issuernotified = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_badge_issued'


class MdlBadgeManualAward(models.Model):
    id = models.BigIntegerField(primary_key=True)
    badgeid = models.BigIntegerField()
    recipientid = models.BigIntegerField()
    issuerid = models.BigIntegerField()
    issuerrole = models.BigIntegerField()
    datemet = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_badge_manual_award'


class MdlBlock(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=40)
    cron = models.BigIntegerField()
    lastcron = models.BigIntegerField()
    visible = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_block'


class MdlBlockCommunity(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    coursename = models.CharField(max_length=255)
    coursedescription = models.TextField(blank=True)
    courseurl = models.CharField(max_length=255)
    imageurl = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_block_community'


class MdlBlockConfigurableReports(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    ownerid = models.BigIntegerField()
    visible = models.SmallIntegerField()
    name = models.CharField(max_length=128)
    summary = models.TextField(blank=True)
    type = models.CharField(max_length=128)
    pagination = models.SmallIntegerField(blank=True, null=True)
    components = models.TextField(blank=True)
    export = models.CharField(max_length=255, blank=True)
    jsordering = models.SmallIntegerField(blank=True, null=True)
    global_field = models.SmallIntegerField(db_column='global', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    lastexecutiontime = models.BigIntegerField(blank=True, null=True)
    cron = models.BigIntegerField(blank=True, null=True)
    remote = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_block_configurable_reports'


class MdlBlockInstances(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pagetypepattern = models.CharField(max_length=64)
    defaultregion = models.CharField(max_length=16)
    configdata = models.TextField(blank=True)
    defaultweight = models.BigIntegerField()
    blockname = models.CharField(max_length=40)
    parentcontextid = models.BigIntegerField()
    showinsubcontexts = models.SmallIntegerField()
    subpagepattern = models.CharField(max_length=16, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_block_instances'


class MdlBlockPositions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    blockinstanceid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    pagetype = models.CharField(max_length=64)
    subpage = models.CharField(max_length=16)
    visible = models.SmallIntegerField()
    region = models.CharField(max_length=16)
    weight = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_block_positions'


class MdlBlockRecentActivity(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    cmid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    userid = models.BigIntegerField()
    action = models.SmallIntegerField()
    modname = models.CharField(max_length=20, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_block_recent_activity'


class MdlBlockRssClient(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    title = models.TextField()
    preferredtitle = models.CharField(max_length=64)
    description = models.TextField()
    shared = models.SmallIntegerField()
    url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_block_rss_client'


class MdlBlogAssociation(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    blogid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_blog_association'


class MdlBlogExternal(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.TextField()
    filtertags = models.CharField(max_length=255, blank=True)
    failedlastsync = models.SmallIntegerField()
    timemodified = models.BigIntegerField(blank=True, null=True)
    timefetched = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_blog_external'


class MdlBook(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    numbering = models.SmallIntegerField()
    customtitles = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    introformat = models.SmallIntegerField()
    revision = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_book'


class MdlBookChapters(models.Model):
    id = models.BigIntegerField(primary_key=True)
    bookid = models.BigIntegerField()
    pagenum = models.BigIntegerField()
    subchapter = models.BigIntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    hidden = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    importsrc = models.CharField(max_length=255)
    contentformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_book_chapters'


class MdlCacheFilters(models.Model):
    id = models.BigIntegerField(primary_key=True)
    filter = models.CharField(max_length=32)
    version = models.BigIntegerField()
    md5key = models.CharField(max_length=32)
    rawtext = models.TextField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_cache_filters'


class MdlCacheFlags(models.Model):
    id = models.BigIntegerField(primary_key=True)
    flagtype = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    timemodified = models.BigIntegerField()
    value = models.TextField()
    expiry = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_cache_flags'


class MdlCapabilities(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    captype = models.CharField(max_length=50)
    contextlevel = models.BigIntegerField()
    component = models.CharField(max_length=100)
    riskbitmask = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_capabilities'


class MdlCertificate(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    emailteachers = models.SmallIntegerField()
    emailothers = models.TextField(blank=True)
    savecert = models.SmallIntegerField()
    reportcert = models.SmallIntegerField()
    delivery = models.SmallIntegerField()
    certificatetype = models.CharField(max_length=50)
    borderstyle = models.CharField(max_length=255)
    bordercolor = models.CharField(max_length=30)
    printwmark = models.CharField(max_length=255)
    printdate = models.BigIntegerField()
    datefmt = models.BigIntegerField()
    printnumber = models.SmallIntegerField()
    printgrade = models.BigIntegerField()
    gradefmt = models.BigIntegerField()
    printoutcome = models.BigIntegerField()
    printhours = models.CharField(max_length=255, blank=True)
    printteacher = models.BigIntegerField()
    customtext = models.TextField(blank=True)
    printsignature = models.CharField(max_length=255)
    printseal = models.CharField(max_length=255)
    timemodified = models.BigIntegerField()
    introformat = models.SmallIntegerField()
    orientation = models.CharField(max_length=10)
    requiredtime = models.BigIntegerField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_certificate'


class MdlCertificateIssues(models.Model):
    id = models.BigIntegerField(primary_key=True)
    certificateid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    code = models.CharField(max_length=40, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_certificate_issues'


class MdlChat(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    keepdays = models.BigIntegerField()
    studentlogs = models.SmallIntegerField()
    chattime = models.BigIntegerField()
    schedule = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    introformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_chat'


class MdlChatMessages(models.Model):
    id = models.BigIntegerField(primary_key=True)
    chatid = models.BigIntegerField()
    userid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    system = models.SmallIntegerField()
    message = models.TextField()
    timestamp = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_chat_messages'


class MdlChatMessagesCurrent(models.Model):
    id = models.BigIntegerField(primary_key=True)
    chatid = models.BigIntegerField()
    userid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    system = models.SmallIntegerField()
    message = models.TextField()
    timestamp = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_chat_messages_current'


class MdlChatUsers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    chatid = models.BigIntegerField()
    userid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    version = models.CharField(max_length=16)
    ip = models.CharField(max_length=45)
    firstping = models.BigIntegerField()
    lastping = models.BigIntegerField()
    lastmessageping = models.BigIntegerField()
    sid = models.CharField(max_length=32)
    course = models.BigIntegerField()
    lang = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'mdl_chat_users'


class MdlChoice(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    introformat = models.SmallIntegerField()
    publish = models.SmallIntegerField()
    showresults = models.SmallIntegerField()
    display = models.SmallIntegerField()
    allowupdate = models.SmallIntegerField()
    showunanswered = models.SmallIntegerField()
    limitanswers = models.SmallIntegerField()
    timeopen = models.BigIntegerField()
    timeclose = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    completionsubmit = models.SmallIntegerField()
    allowmultiple = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_choice'


class MdlChoiceAnswers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    choiceid = models.BigIntegerField()
    userid = models.BigIntegerField()
    optionid = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_choice_answers'


class MdlChoiceOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    choiceid = models.BigIntegerField()
    text = models.TextField(blank=True)
    maxanswers = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_choice_options'


class MdlCohort(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    name = models.CharField(max_length=254)
    idnumber = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField()
    component = models.CharField(max_length=100)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    visible = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_cohort'


class MdlCohortMembers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    cohortid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timeadded = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_cohort_members'


class MdlComments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    commentarea = models.CharField(max_length=255)
    itemid = models.BigIntegerField()
    content = models.TextField()
    format = models.SmallIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_comments'


class MdlConfig(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_config'


class MdlConfigLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    plugin = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    value = models.TextField(blank=True)
    oldvalue = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_config_log'


class MdlConfigPlugins(models.Model):
    id = models.BigIntegerField(primary_key=True)
    plugin = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_config_plugins'


class MdlContext(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextlevel = models.BigIntegerField()
    instanceid = models.BigIntegerField()
    path = models.CharField(max_length=255, blank=True)
    depth = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_context'


class MdlContextTemp(models.Model):
    id = models.BigIntegerField(primary_key=True)
    path = models.CharField(max_length=255)
    depth = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_context_temp'


class MdlCourse(models.Model):
    id = models.BigIntegerField(primary_key=True)
    category = models.BigIntegerField()
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


class MdlCourseCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = models.BigIntegerField()
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


class MdlCourseCompletionAggrMethd(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    criteriatype = models.BigIntegerField(blank=True, null=True)
    method = models.SmallIntegerField()
    value = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_completion_aggr_methd'


class MdlCourseCompletionCritCompl(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    course = models.BigIntegerField()
    criteriaid = models.BigIntegerField()
    gradefinal = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    unenroled = models.BigIntegerField(blank=True, null=True)
    timecompleted = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_completion_crit_compl'


class MdlCourseCompletionCriteria(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    criteriatype = models.BigIntegerField()
    module = models.CharField(max_length=100, blank=True)
    moduleinstance = models.BigIntegerField(blank=True, null=True)
    courseinstance = models.BigIntegerField(blank=True, null=True)
    enrolperiod = models.BigIntegerField(blank=True, null=True)
    timeend = models.BigIntegerField(blank=True, null=True)
    gradepass = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    role = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_completion_criteria'


class MdlCourseCompletions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    course = models.BigIntegerField()
    timeenrolled = models.BigIntegerField()
    timestarted = models.BigIntegerField()
    timecompleted = models.BigIntegerField(blank=True, null=True)
    reaggregate = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_course_completions'


class MdlCourseFormatOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    format = models.CharField(max_length=21)
    sectionid = models.BigIntegerField()
    name = models.CharField(max_length=100)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_format_options'


class MdlCourseModules(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    module = models.BigIntegerField()
    instance = models.BigIntegerField()
    section = models.BigIntegerField()
    added = models.BigIntegerField()
    score = models.SmallIntegerField()
    indent = models.IntegerField()
    visible = models.SmallIntegerField()
    visibleold = models.SmallIntegerField()
    groupmode = models.SmallIntegerField()
    idnumber = models.CharField(max_length=100, blank=True)
    groupingid = models.BigIntegerField()
    completion = models.SmallIntegerField()
    completiongradeitemnumber = models.BigIntegerField(blank=True, null=True)
    completionview = models.SmallIntegerField()
    completionexpected = models.BigIntegerField()
    showdescription = models.SmallIntegerField()
    availability = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_modules'


class MdlCourseModulesCompletion(models.Model):
    id = models.BigIntegerField(primary_key=True)
    coursemoduleid = models.BigIntegerField()
    userid = models.BigIntegerField()
    completionstate = models.SmallIntegerField()
    viewed = models.SmallIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_course_modules_completion'


class MdlCoursePublished(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    timepublished = models.BigIntegerField()
    enrollable = models.SmallIntegerField()
    hubcourseid = models.BigIntegerField()
    status = models.SmallIntegerField(blank=True, null=True)
    timechecked = models.BigIntegerField(blank=True, null=True)
    huburl = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_published'


class MdlCourseRequest(models.Model):
    id = models.BigIntegerField(primary_key=True)
    fullname = models.CharField(max_length=254)
    shortname = models.CharField(max_length=100)
    summary = models.TextField()
    reason = models.TextField()
    requester = models.BigIntegerField()
    password = models.CharField(max_length=50)
    summaryformat = models.SmallIntegerField()
    category = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_course_request'


class MdlCourseSections(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    section = models.BigIntegerField()
    summary = models.TextField(blank=True)
    sequence = models.TextField(blank=True)
    visible = models.SmallIntegerField()
    name = models.CharField(max_length=255, blank=True)
    summaryformat = models.SmallIntegerField()
    availability = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_course_sections'


class MdlData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    comments = models.SmallIntegerField()
    timeavailablefrom = models.BigIntegerField()
    timeavailableto = models.BigIntegerField()
    timeviewfrom = models.BigIntegerField()
    timeviewto = models.BigIntegerField()
    requiredentries = models.IntegerField()
    requiredentriestoview = models.IntegerField()
    maxentries = models.IntegerField()
    rssarticles = models.SmallIntegerField()
    singletemplate = models.TextField(blank=True)
    listtemplate = models.TextField(blank=True)
    listtemplateheader = models.TextField(blank=True)
    listtemplatefooter = models.TextField(blank=True)
    addtemplate = models.TextField(blank=True)
    rsstemplate = models.TextField(blank=True)
    rsstitletemplate = models.TextField(blank=True)
    csstemplate = models.TextField(blank=True)
    jstemplate = models.TextField(blank=True)
    approval = models.SmallIntegerField()
    scale = models.BigIntegerField()
    assessed = models.BigIntegerField()
    defaultsort = models.BigIntegerField()
    defaultsortdir = models.SmallIntegerField()
    editany = models.SmallIntegerField()
    asearchtemplate = models.TextField(blank=True)
    notification = models.BigIntegerField()
    introformat = models.SmallIntegerField()
    assesstimestart = models.BigIntegerField()
    assesstimefinish = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_data'


class MdlDataContent(models.Model):
    id = models.BigIntegerField(primary_key=True)
    fieldid = models.BigIntegerField()
    recordid = models.BigIntegerField()
    content = models.TextField(blank=True)
    content1 = models.TextField(blank=True)
    content2 = models.TextField(blank=True)
    content3 = models.TextField(blank=True)
    content4 = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_data_content'


class MdlDataFields(models.Model):
    id = models.BigIntegerField(primary_key=True)
    dataid = models.BigIntegerField()
    type = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    param1 = models.TextField(blank=True)
    param2 = models.TextField(blank=True)
    param3 = models.TextField(blank=True)
    param4 = models.TextField(blank=True)
    param5 = models.TextField(blank=True)
    param6 = models.TextField(blank=True)
    param7 = models.TextField(blank=True)
    param8 = models.TextField(blank=True)
    param9 = models.TextField(blank=True)
    param10 = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_data_fields'


class MdlDataRecords(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    dataid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    approved = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_data_records'


class MdlEditorAttoAutosave(models.Model):
    id = models.BigIntegerField(primary_key=True)
    elementid = models.CharField(max_length=255)
    contextid = models.BigIntegerField()
    pagehash = models.CharField(max_length=64)
    userid = models.BigIntegerField()
    drafttext = models.TextField()
    draftid = models.BigIntegerField(blank=True, null=True)
    pageinstance = models.CharField(max_length=64)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_editor_atto_autosave'


class MdlEnrol(models.Model):
    id = models.BigIntegerField(primary_key=True)
    enrol = models.CharField(max_length=20)
    status = models.BigIntegerField()
    courseid = models.BigIntegerField()
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


class MdlEnrolFlatfile(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.CharField(max_length=30)
    roleid = models.BigIntegerField()
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField()
    timestart = models.BigIntegerField()
    timeend = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_enrol_flatfile'


class MdlEnrolPaypal(models.Model):
    id = models.BigIntegerField(primary_key=True)
    business = models.CharField(max_length=255)
    receiver_email = models.CharField(max_length=255)
    receiver_id = models.CharField(max_length=255)
    item_name = models.CharField(max_length=255)
    courseid = models.BigIntegerField()
    userid = models.BigIntegerField()
    memo = models.CharField(max_length=255)
    tax = models.CharField(max_length=255)
    option_name1 = models.CharField(max_length=255)
    option_selection1_x = models.CharField(max_length=255)
    option_name2 = models.CharField(max_length=255)
    option_selection2_x = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=255)
    pending_reason = models.CharField(max_length=255)
    reason_code = models.CharField(max_length=30)
    txn_id = models.CharField(max_length=255)
    parent_txn_id = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=30)
    timeupdated = models.BigIntegerField()
    instanceid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_enrol_paypal'


class MdlEvent(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    description = models.TextField()
    format = models.SmallIntegerField()
    courseid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    userid = models.BigIntegerField()
    repeatid = models.BigIntegerField()
    modulename = models.CharField(max_length=20)
    instance = models.BigIntegerField()
    eventtype = models.CharField(max_length=20)
    timestart = models.BigIntegerField()
    timeduration = models.BigIntegerField()
    visible = models.SmallIntegerField()
    uuid = models.CharField(max_length=255)
    sequence = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    subscriptionid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_event'


class MdlEventSubscriptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    url = models.CharField(max_length=255)
    courseid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    userid = models.BigIntegerField()
    pollinterval = models.BigIntegerField()
    lastupdated = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    eventtype = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'mdl_event_subscriptions'


class MdlEventsHandlers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    eventname = models.CharField(max_length=166)
    component = models.CharField(max_length=166)
    handlerfile = models.CharField(max_length=255)
    handlerfunction = models.TextField(blank=True)
    schedule = models.CharField(max_length=255, blank=True)
    status = models.BigIntegerField()
    internal = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_events_handlers'


class MdlEventsQueue(models.Model):
    id = models.BigIntegerField(primary_key=True)
    eventdata = models.TextField()
    stackdump = models.TextField(blank=True)
    userid = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_events_queue'


class MdlEventsQueueHandlers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    queuedeventid = models.BigIntegerField()
    handlerid = models.BigIntegerField()
    status = models.BigIntegerField(blank=True, null=True)
    errormessage = models.TextField(blank=True)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_events_queue_handlers'


class MdlExternalFunctions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=200)
    classname = models.CharField(max_length=100)
    methodname = models.CharField(max_length=100)
    classpath = models.CharField(max_length=255, blank=True)
    component = models.CharField(max_length=100)
    capabilities = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_external_functions'


class MdlExternalServices(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=200)
    enabled = models.SmallIntegerField()
    requiredcapability = models.CharField(max_length=150, blank=True)
    restrictedusers = models.SmallIntegerField()
    component = models.CharField(max_length=100, blank=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField(blank=True, null=True)
    shortname = models.CharField(max_length=255, blank=True)
    downloadfiles = models.SmallIntegerField()
    uploadfiles = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_external_services'


class MdlExternalServicesFunctions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    externalserviceid = models.BigIntegerField()
    functionname = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'mdl_external_services_functions'


class MdlExternalServicesUsers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    externalserviceid = models.BigIntegerField()
    userid = models.BigIntegerField()
    iprestriction = models.CharField(max_length=255, blank=True)
    validuntil = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_external_services_users'


class MdlExternalTokens(models.Model):
    id = models.BigIntegerField(primary_key=True)
    token = models.CharField(max_length=128)
    tokentype = models.SmallIntegerField()
    userid = models.BigIntegerField()
    externalserviceid = models.BigIntegerField()
    sid = models.CharField(max_length=128, blank=True)
    contextid = models.BigIntegerField()
    creatorid = models.BigIntegerField()
    iprestriction = models.CharField(max_length=255, blank=True)
    validuntil = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField()
    lastaccess = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_external_tokens'


class MdlFeedback(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    introformat = models.SmallIntegerField()
    anonymous = models.SmallIntegerField()
    email_notification = models.SmallIntegerField()
    multiple_submit = models.SmallIntegerField()
    autonumbering = models.SmallIntegerField()
    site_after_submit = models.CharField(max_length=255)
    page_after_submit = models.TextField()
    page_after_submitformat = models.SmallIntegerField()
    publish_stats = models.SmallIntegerField()
    timeopen = models.BigIntegerField()
    timeclose = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    completionsubmit = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_feedback'


class MdlFeedbackCompleted(models.Model):
    id = models.BigIntegerField(primary_key=True)
    feedback = models.BigIntegerField()
    userid = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    random_response = models.BigIntegerField()
    anonymous_response = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_feedback_completed'


class MdlFeedbackCompletedtmp(models.Model):
    id = models.BigIntegerField(primary_key=True)
    feedback = models.BigIntegerField()
    userid = models.BigIntegerField()
    guestid = models.CharField(max_length=255)
    timemodified = models.BigIntegerField()
    random_response = models.BigIntegerField()
    anonymous_response = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_feedback_completedtmp'


class MdlFeedbackItem(models.Model):
    id = models.BigIntegerField(primary_key=True)
    feedback = models.BigIntegerField()
    template = models.BigIntegerField()
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    presentation = models.TextField()
    typ = models.CharField(max_length=255)
    hasvalue = models.SmallIntegerField()
    position = models.SmallIntegerField()
    required = models.SmallIntegerField()
    dependitem = models.BigIntegerField()
    dependvalue = models.CharField(max_length=255)
    options = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_feedback_item'


class MdlFeedbackSitecourseMap(models.Model):
    id = models.BigIntegerField(primary_key=True)
    feedbackid = models.BigIntegerField()
    courseid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_feedback_sitecourse_map'


class MdlFeedbackTemplate(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    ispublic = models.SmallIntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_feedback_template'


class MdlFeedbackTracking(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    feedback = models.BigIntegerField()
    completed = models.BigIntegerField()
    tmp_completed = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_feedback_tracking'


class MdlFeedbackValue(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course_id = models.BigIntegerField()
    item = models.BigIntegerField()
    completed = models.BigIntegerField()
    tmp_completed = models.BigIntegerField()
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_feedback_value'


class MdlFeedbackValuetmp(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course_id = models.BigIntegerField()
    item = models.BigIntegerField()
    completed = models.BigIntegerField()
    tmp_completed = models.BigIntegerField()
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_feedback_valuetmp'


class MdlFiles(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contenthash = models.CharField(max_length=40)
    pathnamehash = models.CharField(unique=True, max_length=40)
    contextid = models.BigIntegerField()
    component = models.CharField(max_length=100)
    filearea = models.CharField(max_length=50)
    itemid = models.BigIntegerField()
    filepath = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    userid = models.BigIntegerField(blank=True, null=True)
    filesize = models.BigIntegerField()
    mimetype = models.CharField(max_length=100, blank=True)
    status = models.BigIntegerField()
    source = models.TextField(blank=True)
    author = models.CharField(max_length=255, blank=True)
    license = models.CharField(max_length=255, blank=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    referencefileid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_files'


class MdlFilesReference(models.Model):
    id = models.BigIntegerField(primary_key=True)
    repositoryid = models.BigIntegerField()
    lastsync = models.BigIntegerField(blank=True, null=True)
    reference = models.TextField(blank=True)
    referencehash = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'mdl_files_reference'


class MdlFilterActive(models.Model):
    id = models.BigIntegerField(primary_key=True)
    filter = models.CharField(max_length=32)
    contextid = models.BigIntegerField()
    active = models.SmallIntegerField()
    sortorder = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_filter_active'


class MdlFilterConfig(models.Model):
    id = models.BigIntegerField(primary_key=True)
    filter = models.CharField(max_length=32)
    contextid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_filter_config'


class MdlFolder(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()
    revision = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    display = models.SmallIntegerField()
    showexpanded = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_folder'


class MdlFormatPage(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    nameone = models.CharField(max_length=128, blank=True)
    nametwo = models.CharField(max_length=128, blank=True)
    display = models.BigIntegerField(blank=True, null=True)
    prefleftwidth = models.SmallIntegerField(blank=True, null=True)
    prefcenterwidth = models.SmallIntegerField(blank=True, null=True)
    prefrightwidth = models.SmallIntegerField(blank=True, null=True)
    parent = models.BigIntegerField(blank=True, null=True)
    sortorder = models.SmallIntegerField(blank=True, null=True)
    template = models.SmallIntegerField(blank=True, null=True)
    showbuttons = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_format_page'


class MdlFormatPageItems(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pageid = models.BigIntegerField()
    cmid = models.BigIntegerField()
    blockinstance = models.BigIntegerField()
    position = models.CharField(max_length=3)
    sortorder = models.SmallIntegerField()
    visible = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_format_page_items'


class MdlForum(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    intro = models.TextField()
    assessed = models.BigIntegerField()
    assesstimestart = models.BigIntegerField()
    assesstimefinish = models.BigIntegerField()
    scale = models.BigIntegerField()
    maxbytes = models.BigIntegerField()
    forcesubscribe = models.SmallIntegerField()
    trackingtype = models.SmallIntegerField()
    rsstype = models.SmallIntegerField()
    rssarticles = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    warnafter = models.BigIntegerField()
    blockafter = models.BigIntegerField()
    blockperiod = models.BigIntegerField()
    completiondiscussions = models.IntegerField()
    completionreplies = models.IntegerField()
    completionposts = models.IntegerField()
    maxattachments = models.BigIntegerField()
    introformat = models.SmallIntegerField()
    displaywordcount = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum'


class MdlForumDigests(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    forum = models.BigIntegerField()
    maildigest = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_digests'


class MdlForumDiscussionSubs(models.Model):
    id = models.BigIntegerField(primary_key=True)
    forum = models.BigIntegerField()
    userid = models.BigIntegerField()
    discussion = models.BigIntegerField()
    preference = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_discussion_subs'


class MdlForumDiscussions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    forum = models.BigIntegerField()
    name = models.CharField(max_length=255)
    firstpost = models.BigIntegerField()
    userid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    assessed = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    usermodified = models.BigIntegerField()
    timestart = models.BigIntegerField()
    timeend = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_discussions'


class MdlForumPosts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    discussion = models.BigIntegerField()
    parent = models.BigIntegerField()
    userid = models.BigIntegerField()
    created = models.BigIntegerField()
    modified = models.BigIntegerField()
    mailed = models.SmallIntegerField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    messageformat = models.SmallIntegerField()
    attachment = models.CharField(max_length=100)
    totalscore = models.SmallIntegerField()
    mailnow = models.BigIntegerField()
    messagetrust = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_posts'


class MdlForumQueue(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    discussionid = models.BigIntegerField()
    postid = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_queue'


class MdlForumRead(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    forumid = models.BigIntegerField()
    discussionid = models.BigIntegerField()
    postid = models.BigIntegerField()
    firstread = models.BigIntegerField()
    lastread = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_read'


class MdlForumSubscriptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    forum = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_subscriptions'


class MdlForumTrackPrefs(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    forumid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_forum_track_prefs'


class MdlGlossary(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    allowduplicatedentries = models.SmallIntegerField()
    displayformat = models.CharField(max_length=50)
    mainglossary = models.SmallIntegerField()
    showspecial = models.SmallIntegerField()
    showalphabet = models.SmallIntegerField()
    showall = models.SmallIntegerField()
    allowcomments = models.SmallIntegerField()
    allowprintview = models.SmallIntegerField()
    usedynalink = models.SmallIntegerField()
    defaultapproval = models.SmallIntegerField()
    globalglossary = models.SmallIntegerField()
    entbypage = models.SmallIntegerField()
    editalways = models.SmallIntegerField()
    rsstype = models.SmallIntegerField()
    rssarticles = models.SmallIntegerField()
    assessed = models.BigIntegerField()
    assesstimestart = models.BigIntegerField()
    assesstimefinish = models.BigIntegerField()
    scale = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    introformat = models.SmallIntegerField()
    completionentries = models.IntegerField()
    approvaldisplayformat = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mdl_glossary'


class MdlGlossaryAlias(models.Model):
    id = models.BigIntegerField(primary_key=True)
    entryid = models.BigIntegerField()
    alias = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_glossary_alias'


class MdlGlossaryCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    glossaryid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    usedynalink = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_glossary_categories'


class MdlGlossaryEntries(models.Model):
    id = models.BigIntegerField(primary_key=True)
    glossaryid = models.BigIntegerField()
    userid = models.BigIntegerField()
    concept = models.CharField(max_length=255)
    definition = models.TextField()
    definitionformat = models.SmallIntegerField()
    attachment = models.CharField(max_length=100)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    teacherentry = models.SmallIntegerField()
    sourceglossaryid = models.BigIntegerField()
    usedynalink = models.SmallIntegerField()
    casesensitive = models.SmallIntegerField()
    fullmatch = models.SmallIntegerField()
    approved = models.SmallIntegerField()
    definitiontrust = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_glossary_entries'


class MdlGlossaryEntriesCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    categoryid = models.BigIntegerField()
    entryid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_glossary_entries_categories'


class MdlGlossaryFormats(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    popupformatname = models.CharField(max_length=50)
    visible = models.SmallIntegerField()
    showgroup = models.SmallIntegerField()
    defaultmode = models.CharField(max_length=50)
    defaulthook = models.CharField(max_length=50)
    sortkey = models.CharField(max_length=50)
    sortorder = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mdl_glossary_formats'


class MdlGradeCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    parent = models.BigIntegerField(blank=True, null=True)
    depth = models.BigIntegerField()
    path = models.CharField(max_length=255, blank=True)
    fullname = models.CharField(max_length=255)
    aggregation = models.BigIntegerField()
    keephigh = models.BigIntegerField()
    droplow = models.BigIntegerField()
    aggregateonlygraded = models.SmallIntegerField()
    aggregateoutcomes = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    hidden = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_categories'


class MdlGradeCategoriesHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.BigIntegerField()
    oldid = models.BigIntegerField()
    source = models.CharField(max_length=255, blank=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    loggeduser = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField()
    parent = models.BigIntegerField(blank=True, null=True)
    depth = models.BigIntegerField()
    path = models.CharField(max_length=255, blank=True)
    fullname = models.CharField(max_length=255)
    aggregation = models.BigIntegerField()
    keephigh = models.BigIntegerField()
    droplow = models.BigIntegerField()
    aggregateonlygraded = models.SmallIntegerField()
    aggregateoutcomes = models.SmallIntegerField()
    aggregatesubcats = models.SmallIntegerField()
    hidden = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_categories_history'


class MdlGradeGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    itemid = models.BigIntegerField()
    userid = models.BigIntegerField()
    rawgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    rawgrademax = models.DecimalField(max_digits=10, decimal_places=5)
    rawgrademin = models.DecimalField(max_digits=10, decimal_places=5)
    rawscaleid = models.BigIntegerField(blank=True, null=True)
    usermodified = models.BigIntegerField(blank=True, null=True)
    finalgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    hidden = models.BigIntegerField()
    locked = models.BigIntegerField()
    locktime = models.BigIntegerField()
    exported = models.BigIntegerField()
    overridden = models.BigIntegerField()
    excluded = models.BigIntegerField()
    feedback = models.TextField(blank=True)
    feedbackformat = models.BigIntegerField()
    information = models.TextField(blank=True)
    informationformat = models.BigIntegerField()
    timecreated = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    notacesar = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    aggregationstatus = models.CharField(max_length=10)
    aggregationweight = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_grade_grades'


class MdlGradeGradesHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.BigIntegerField()
    oldid = models.BigIntegerField()
    source = models.CharField(max_length=255, blank=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    loggeduser = models.BigIntegerField(blank=True, null=True)
    itemid = models.BigIntegerField()
    userid = models.BigIntegerField()
    rawgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    rawgrademax = models.DecimalField(max_digits=10, decimal_places=5)
    rawgrademin = models.DecimalField(max_digits=10, decimal_places=5)
    rawscaleid = models.BigIntegerField(blank=True, null=True)
    usermodified = models.BigIntegerField(blank=True, null=True)
    finalgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    hidden = models.BigIntegerField()
    locked = models.BigIntegerField()
    locktime = models.BigIntegerField()
    exported = models.BigIntegerField()
    overridden = models.BigIntegerField()
    excluded = models.BigIntegerField()
    feedback = models.TextField(blank=True)
    feedbackformat = models.BigIntegerField()
    information = models.TextField(blank=True)
    informationformat = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_grades_history'


class MdlGradeImportNewitem(models.Model):
    id = models.BigIntegerField(primary_key=True)
    itemname = models.CharField(max_length=255)
    importcode = models.BigIntegerField()
    importer = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_import_newitem'


class MdlGradeImportValues(models.Model):
    id = models.BigIntegerField(primary_key=True)
    itemid = models.BigIntegerField(blank=True, null=True)
    newgradeitem = models.BigIntegerField(blank=True, null=True)
    userid = models.BigIntegerField()
    finalgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    feedback = models.TextField(blank=True)
    importcode = models.BigIntegerField()
    importer = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_grade_import_values'


class MdlGradeItems(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField(blank=True, null=True)
    categoryid = models.BigIntegerField(blank=True, null=True)
    itemname = models.CharField(max_length=255, blank=True)
    itemtype = models.CharField(max_length=30)
    itemmodule = models.CharField(max_length=30, blank=True)
    iteminstance = models.BigIntegerField(blank=True, null=True)
    itemnumber = models.BigIntegerField(blank=True, null=True)
    iteminfo = models.TextField(blank=True)
    idnumber = models.CharField(max_length=255, blank=True)
    calculation = models.TextField(blank=True)
    gradetype = models.SmallIntegerField()
    grademax = models.DecimalField(max_digits=10, decimal_places=5)
    grademin = models.DecimalField(max_digits=10, decimal_places=5)
    scaleid = models.BigIntegerField(blank=True, null=True)
    outcomeid = models.BigIntegerField(blank=True, null=True)
    gradepass = models.DecimalField(max_digits=10, decimal_places=5)
    multfactor = models.DecimalField(max_digits=10, decimal_places=5)
    plusfactor = models.DecimalField(max_digits=10, decimal_places=5)
    aggregationcoef = models.DecimalField(max_digits=10, decimal_places=5)
    sortorder = models.BigIntegerField()
    hidden = models.BigIntegerField()
    locked = models.BigIntegerField()
    locktime = models.BigIntegerField()
    needsupdate = models.BigIntegerField()
    timecreated = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    display = models.BigIntegerField()
    decimals = models.SmallIntegerField(blank=True, null=True)
    aggregationcoef2 = models.DecimalField(max_digits=10, decimal_places=5)
    weightoverride = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_items'


class MdlGradeItemsHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.BigIntegerField()
    oldid = models.BigIntegerField()
    source = models.CharField(max_length=255, blank=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    loggeduser = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField(blank=True, null=True)
    categoryid = models.BigIntegerField(blank=True, null=True)
    itemname = models.CharField(max_length=255, blank=True)
    itemtype = models.CharField(max_length=30)
    itemmodule = models.CharField(max_length=30, blank=True)
    iteminstance = models.BigIntegerField(blank=True, null=True)
    itemnumber = models.BigIntegerField(blank=True, null=True)
    iteminfo = models.TextField(blank=True)
    idnumber = models.CharField(max_length=255, blank=True)
    calculation = models.TextField(blank=True)
    gradetype = models.SmallIntegerField()
    grademax = models.DecimalField(max_digits=10, decimal_places=5)
    grademin = models.DecimalField(max_digits=10, decimal_places=5)
    scaleid = models.BigIntegerField(blank=True, null=True)
    outcomeid = models.BigIntegerField(blank=True, null=True)
    gradepass = models.DecimalField(max_digits=10, decimal_places=5)
    multfactor = models.DecimalField(max_digits=10, decimal_places=5)
    plusfactor = models.DecimalField(max_digits=10, decimal_places=5)
    aggregationcoef = models.DecimalField(max_digits=10, decimal_places=5)
    sortorder = models.BigIntegerField()
    display = models.BigIntegerField()
    decimals = models.SmallIntegerField(blank=True, null=True)
    hidden = models.BigIntegerField()
    locked = models.BigIntegerField()
    locktime = models.BigIntegerField()
    needsupdate = models.BigIntegerField()
    aggregationcoef2 = models.DecimalField(max_digits=10, decimal_places=5)
    weightoverride = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_items_history'


class MdlGradeLetters(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    lowerboundary = models.DecimalField(max_digits=10, decimal_places=5)
    letter = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_grade_letters'


class MdlGradeOutcomes(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField(blank=True, null=True)
    shortname = models.CharField(max_length=255)
    fullname = models.TextField()
    scaleid = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    timecreated = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    usermodified = models.BigIntegerField(blank=True, null=True)
    descriptionformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_outcomes'


class MdlGradeOutcomesCourses(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    outcomeid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_outcomes_courses'


class MdlGradeOutcomesHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.BigIntegerField()
    oldid = models.BigIntegerField()
    source = models.CharField(max_length=255, blank=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    loggeduser = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField(blank=True, null=True)
    shortname = models.CharField(max_length=255)
    fullname = models.TextField()
    scaleid = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grade_outcomes_history'


class MdlGradeSettings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_grade_settings'


class MdlGradingAreas(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    component = models.CharField(max_length=100)
    areaname = models.CharField(max_length=100)
    activemethod = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_grading_areas'


class MdlGradingDefinitions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    areaid = models.BigIntegerField()
    method = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)
    status = models.BigIntegerField()
    copiedfromid = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField()
    usercreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    usermodified = models.BigIntegerField()
    timecopied = models.BigIntegerField(blank=True, null=True)
    options = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_grading_definitions'


class MdlGradingInstances(models.Model):
    id = models.BigIntegerField(primary_key=True)
    definitionid = models.BigIntegerField()
    raterid = models.BigIntegerField()
    itemid = models.BigIntegerField(blank=True, null=True)
    rawgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    status = models.BigIntegerField()
    feedback = models.TextField(blank=True)
    feedbackformat = models.SmallIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_grading_instances'


class MdlGradingformGuideComments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    definitionid = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_gradingform_guide_comments'


class MdlGradingformGuideCriteria(models.Model):
    id = models.BigIntegerField(primary_key=True)
    definitionid = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    shortname = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)
    descriptionmarkers = models.TextField(blank=True)
    descriptionmarkersformat = models.SmallIntegerField(blank=True, null=True)
    maxscore = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'mdl_gradingform_guide_criteria'


class MdlGradingformGuideFillings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    instanceid = models.BigIntegerField()
    criterionid = models.BigIntegerField()
    remark = models.TextField(blank=True)
    remarkformat = models.SmallIntegerField(blank=True, null=True)
    score = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'mdl_gradingform_guide_fillings'


class MdlGradingformRubricCriteria(models.Model):
    id = models.BigIntegerField(primary_key=True)
    definitionid = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_gradingform_rubric_criteria'


class MdlGradingformRubricFillings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    instanceid = models.BigIntegerField()
    criterionid = models.BigIntegerField()
    levelid = models.BigIntegerField(blank=True, null=True)
    remark = models.TextField(blank=True)
    remarkformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_gradingform_rubric_fillings'


class MdlGradingformRubricLevels(models.Model):
    id = models.BigIntegerField(primary_key=True)
    criterionid = models.BigIntegerField()
    score = models.DecimalField(max_digits=10, decimal_places=5)
    definition = models.TextField(blank=True)
    definitionformat = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_gradingform_rubric_levels'


class MdlGroupings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    timecreated = models.BigIntegerField()
    courseid = models.BigIntegerField()
    configdata = models.TextField(blank=True)
    timemodified = models.BigIntegerField()
    descriptionformat = models.SmallIntegerField()
    idnumber = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mdl_groupings'


class MdlGroupingsGroups(models.Model):
    id = models.BigIntegerField(primary_key=True)
    groupingid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    timeadded = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_groupings_groups'


class MdlGroups(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True)
    enrolmentkey = models.CharField(max_length=50, blank=True)
    picture = models.BigIntegerField()
    hidepicture = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    courseid = models.BigIntegerField()
    descriptionformat = models.SmallIntegerField()
    idnumber = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mdl_groups'


class MdlGroupsMembers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    groupid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timeadded = models.BigIntegerField()
    component = models.CharField(max_length=100)
    itemid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_groups_members'


class MdlHotpot(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    entrytext = models.TextField()
    timeopen = models.BigIntegerField()
    timeclose = models.BigIntegerField()
    sourcelocation = models.SmallIntegerField()
    sourcefile = models.CharField(max_length=255)
    outputformat = models.CharField(max_length=255)
    navigation = models.SmallIntegerField()
    studentfeedback = models.SmallIntegerField()
    studentfeedbackurl = models.CharField(max_length=255)
    reviewoptions = models.BigIntegerField()
    gradeweighting = models.BigIntegerField()
    grademethod = models.SmallIntegerField()
    attemptlimit = models.IntegerField()
    password = models.CharField(max_length=255)
    subnet = models.CharField(max_length=255)
    clickreporting = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    sourcetype = models.CharField(max_length=255)
    configfile = models.CharField(max_length=255)
    configlocation = models.SmallIntegerField()
    entrycm = models.BigIntegerField()
    entrygrade = models.IntegerField()
    entrypage = models.SmallIntegerField()
    entryformat = models.SmallIntegerField()
    entryoptions = models.BigIntegerField()
    exitpage = models.SmallIntegerField()
    exittext = models.TextField()
    exitformat = models.SmallIntegerField()
    exitoptions = models.BigIntegerField()
    exitcm = models.BigIntegerField()
    title = models.IntegerField()
    stopbutton = models.SmallIntegerField()
    stoptext = models.CharField(max_length=255)
    usefilters = models.SmallIntegerField()
    useglossary = models.SmallIntegerField()
    usemediafilter = models.CharField(max_length=255)
    timelimit = models.BigIntegerField()
    delay1 = models.BigIntegerField()
    delay2 = models.BigIntegerField()
    delay3 = models.BigIntegerField()
    discarddetails = models.SmallIntegerField()
    exitgrade = models.IntegerField()
    allowpaste = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_hotpot'


class MdlHotpotAttempts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hotpotid = models.BigIntegerField()
    userid = models.BigIntegerField()
    starttime = models.BigIntegerField()
    endtime = models.BigIntegerField()
    score = models.IntegerField()
    penalties = models.IntegerField()
    attempt = models.IntegerField()
    timestart = models.BigIntegerField()
    timefinish = models.BigIntegerField()
    status = models.SmallIntegerField()
    clickreportid = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_hotpot_attempts'


class MdlHotpotCache(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hotpotid = models.BigIntegerField()
    slasharguments = models.CharField(max_length=1)
    hotpot_enableobfuscate = models.CharField(max_length=1)
    hotpot_enableswf = models.CharField(max_length=1)
    name = models.CharField(max_length=255)
    sourcefile = models.CharField(max_length=255)
    sourcetype = models.CharField(max_length=255)
    sourcelocation = models.SmallIntegerField()
    sourcelastmodified = models.CharField(max_length=255)
    sourceetag = models.CharField(max_length=255)
    configfile = models.CharField(max_length=255)
    configlocation = models.SmallIntegerField()
    configlastmodified = models.CharField(max_length=255)
    configetag = models.CharField(max_length=255)
    navigation = models.SmallIntegerField()
    title = models.IntegerField()
    stopbutton = models.SmallIntegerField()
    stoptext = models.CharField(max_length=255)
    usefilters = models.SmallIntegerField()
    useglossary = models.SmallIntegerField()
    usemediafilter = models.CharField(max_length=255)
    studentfeedback = models.SmallIntegerField()
    studentfeedbackurl = models.CharField(max_length=255)
    timelimit = models.BigIntegerField()
    delay3 = models.BigIntegerField()
    clickreporting = models.SmallIntegerField()
    content = models.TextField()
    timemodified = models.BigIntegerField()
    md5key = models.CharField(max_length=32)
    sourcerepositoryid = models.BigIntegerField()
    configrepositoryid = models.BigIntegerField()
    hotpot_bodystyles = models.CharField(max_length=8)
    allowpaste = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_hotpot_cache'


class MdlHotpotDetails(models.Model):
    id = models.BigIntegerField(primary_key=True)
    attemptid = models.BigIntegerField()
    details = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_hotpot_details'


class MdlHotpotQuestions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    type = models.SmallIntegerField()
    text = models.BigIntegerField()
    hotpotid = models.BigIntegerField()
    md5key = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'mdl_hotpot_questions'


class MdlHotpotResponses(models.Model):
    id = models.BigIntegerField(primary_key=True)
    attemptid = models.BigIntegerField()
    questionid = models.BigIntegerField()
    score = models.IntegerField()
    weighting = models.IntegerField()
    correct = models.CharField(max_length=255)
    wrong = models.CharField(max_length=255)
    ignored = models.CharField(max_length=255)
    hints = models.IntegerField()
    clues = models.IntegerField()
    checks = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_hotpot_responses'


class MdlHotpotStrings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    string = models.TextField()
    md5key = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'mdl_hotpot_strings'


class MdlImscp(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()
    revision = models.BigIntegerField()
    keepold = models.BigIntegerField()
    structure = models.TextField(blank=True)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_imscp'


class MdlJournal(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    introformat = models.SmallIntegerField()
    days = models.IntegerField()
    grade = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_journal'


class MdlJournalEntries(models.Model):
    id = models.BigIntegerField(primary_key=True)
    journal = models.BigIntegerField()
    userid = models.BigIntegerField()
    modified = models.BigIntegerField()
    text = models.TextField()
    format = models.SmallIntegerField()
    rating = models.BigIntegerField(blank=True, null=True)
    entrycomment = models.TextField(blank=True)
    teacher = models.BigIntegerField()
    timemarked = models.BigIntegerField()
    mailed = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_journal_entries'


class MdlLabel(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    timemodified = models.BigIntegerField()
    introformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_label'


class MdlLesson(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    practice = models.SmallIntegerField()
    modattempts = models.SmallIntegerField()
    usepassword = models.SmallIntegerField()
    password = models.CharField(max_length=32)
    dependency = models.BigIntegerField()
    conditions = models.TextField()
    grade = models.BigIntegerField()
    custom = models.SmallIntegerField()
    ongoing = models.SmallIntegerField()
    usemaxgrade = models.SmallIntegerField()
    maxanswers = models.SmallIntegerField()
    maxattempts = models.SmallIntegerField()
    review = models.SmallIntegerField()
    nextpagedefault = models.SmallIntegerField()
    feedback = models.SmallIntegerField()
    minquestions = models.SmallIntegerField()
    maxpages = models.SmallIntegerField()
    timed = models.SmallIntegerField()
    maxtime = models.BigIntegerField()
    retake = models.SmallIntegerField()
    activitylink = models.BigIntegerField()
    mediafile = models.CharField(max_length=255)
    mediaheight = models.BigIntegerField()
    mediawidth = models.BigIntegerField()
    mediaclose = models.SmallIntegerField()
    slideshow = models.SmallIntegerField()
    width = models.BigIntegerField()
    height = models.BigIntegerField()
    bgcolor = models.CharField(max_length=7)
    displayleft = models.SmallIntegerField()
    displayleftif = models.SmallIntegerField()
    progressbar = models.SmallIntegerField()
    highscores = models.SmallIntegerField()
    maxhighscores = models.BigIntegerField()
    available = models.BigIntegerField()
    deadline = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lesson'


class MdlLessonAnswers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lessonid = models.BigIntegerField()
    pageid = models.BigIntegerField()
    jumpto = models.BigIntegerField()
    grade = models.SmallIntegerField()
    score = models.BigIntegerField()
    flags = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    answer = models.TextField(blank=True)
    response = models.TextField(blank=True)
    answerformat = models.SmallIntegerField()
    responseformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lesson_answers'


class MdlLessonAttempts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lessonid = models.BigIntegerField()
    pageid = models.BigIntegerField()
    userid = models.BigIntegerField()
    answerid = models.BigIntegerField()
    retry = models.SmallIntegerField()
    correct = models.BigIntegerField()
    useranswer = models.TextField(blank=True)
    timeseen = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lesson_attempts'


class MdlLessonBranch(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lessonid = models.BigIntegerField()
    userid = models.BigIntegerField()
    pageid = models.BigIntegerField()
    retry = models.BigIntegerField()
    flag = models.SmallIntegerField()
    timeseen = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lesson_branch'


class MdlLessonGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lessonid = models.BigIntegerField()
    userid = models.BigIntegerField()
    grade = models.FloatField()
    late = models.SmallIntegerField()
    completed = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lesson_grades'


class MdlLessonHighScores(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lessonid = models.BigIntegerField()
    userid = models.BigIntegerField()
    gradeid = models.BigIntegerField()
    nickname = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'mdl_lesson_high_scores'


class MdlLessonPages(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lessonid = models.BigIntegerField()
    prevpageid = models.BigIntegerField()
    nextpageid = models.BigIntegerField()
    qtype = models.SmallIntegerField()
    qoption = models.SmallIntegerField()
    layout = models.SmallIntegerField()
    display = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    title = models.CharField(max_length=255)
    contents = models.TextField()
    contentsformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lesson_pages'


class MdlLessonTimer(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lessonid = models.BigIntegerField()
    userid = models.BigIntegerField()
    starttime = models.BigIntegerField()
    lessontime = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lesson_timer'


class MdlLicense(models.Model):
    id = models.BigIntegerField(primary_key=True)
    shortname = models.CharField(max_length=255, blank=True)
    fullname = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    enabled = models.SmallIntegerField()
    version = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_license'


class MdlLockDb(models.Model):
    id = models.BigIntegerField(primary_key=True)
    resourcekey = models.CharField(unique=True, max_length=255)
    expires = models.BigIntegerField(blank=True, null=True)
    owner = models.CharField(max_length=36, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_lock_db'


class MdlLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    time = models.BigIntegerField()
    userid = models.BigIntegerField()
    ip = models.CharField(max_length=45)
    course = models.BigIntegerField()
    module = models.CharField(max_length=20)
    cmid = models.BigIntegerField()
    action = models.CharField(max_length=40)
    url = models.CharField(max_length=100)
    info = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_log'


class MdlLogDisplay(models.Model):
    id = models.BigIntegerField(primary_key=True)
    module = models.CharField(max_length=20)
    action = models.CharField(max_length=40)
    mtable = models.CharField(max_length=30)
    field = models.CharField(max_length=200)
    component = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mdl_log_display'


class MdlLogQueries(models.Model):
    id = models.BigIntegerField(primary_key=True)
    qtype = models.IntegerField()
    sqltext = models.TextField()
    sqlparams = models.TextField(blank=True)
    error = models.IntegerField()
    info = models.TextField(blank=True)
    backtrace = models.TextField(blank=True)
    exectime = models.DecimalField(max_digits=10, decimal_places=5)
    timelogged = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_log_queries'


class MdlLogstoreStandardLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    eventname = models.CharField(max_length=255)
    component = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    objecttable = models.CharField(max_length=50, blank=True)
    objectid = models.BigIntegerField(blank=True, null=True)
    crud = models.CharField(max_length=1)
    edulevel = models.SmallIntegerField()
    contextid = models.BigIntegerField()
    contextlevel = models.BigIntegerField()
    contextinstanceid = models.BigIntegerField()
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField(blank=True, null=True)
    relateduserid = models.BigIntegerField(blank=True, null=True)
    anonymous = models.SmallIntegerField()
    other = models.TextField(blank=True)
    timecreated = models.BigIntegerField()
    origin = models.CharField(max_length=10, blank=True)
    ip = models.CharField(max_length=45, blank=True)
    realuserid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_logstore_standard_log'


class MdlLti(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    typeid = models.BigIntegerField(blank=True, null=True)
    toolurl = models.TextField()
    securetoolurl = models.TextField(blank=True)
    instructorchoicesendname = models.SmallIntegerField(blank=True, null=True)
    instructorchoicesendemailaddr = models.SmallIntegerField(blank=True, null=True)
    instructorchoiceallowroster = models.SmallIntegerField(blank=True, null=True)
    instructorchoiceallowsetting = models.SmallIntegerField(blank=True, null=True)
    instructorcustomparameters = models.CharField(max_length=255, blank=True)
    instructorchoiceacceptgrades = models.SmallIntegerField(blank=True, null=True)
    grade = models.BigIntegerField()
    launchcontainer = models.SmallIntegerField()
    resourcekey = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    debuglaunch = models.SmallIntegerField()
    showtitlelaunch = models.SmallIntegerField()
    showdescriptionlaunch = models.SmallIntegerField()
    servicesalt = models.CharField(max_length=40, blank=True)
    icon = models.TextField(blank=True)
    secureicon = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_lti'


class MdlLtiSubmission(models.Model):
    id = models.BigIntegerField(primary_key=True)
    ltiid = models.BigIntegerField()
    userid = models.BigIntegerField()
    datesubmitted = models.BigIntegerField()
    dateupdated = models.BigIntegerField()
    gradepercent = models.DecimalField(max_digits=10, decimal_places=5)
    originalgrade = models.DecimalField(max_digits=10, decimal_places=5)
    launchid = models.BigIntegerField()
    state = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lti_submission'


class MdlLtiToolProxies(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    regurl = models.TextField(blank=True)
    state = models.SmallIntegerField()
    guid = models.CharField(unique=True, max_length=255, blank=True)
    secret = models.CharField(max_length=255, blank=True)
    vendorcode = models.CharField(max_length=255, blank=True)
    capabilityoffered = models.TextField()
    serviceoffered = models.TextField()
    toolproxy = models.TextField(blank=True)
    createdby = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lti_tool_proxies'


class MdlLtiToolSettings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    toolproxyid = models.BigIntegerField()
    course = models.BigIntegerField(blank=True, null=True)
    coursemoduleid = models.BigIntegerField(blank=True, null=True)
    settings = models.TextField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_lti_tool_settings'


class MdlLtiTypes(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    baseurl = models.TextField()
    tooldomain = models.CharField(max_length=255)
    state = models.SmallIntegerField()
    course = models.BigIntegerField()
    coursevisible = models.SmallIntegerField()
    createdby = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    toolproxyid = models.BigIntegerField(blank=True, null=True)
    enabledcapability = models.TextField(blank=True)
    parameter = models.TextField(blank=True)
    icon = models.TextField(blank=True)
    secureicon = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_lti_types'


class MdlLtiTypesConfig(models.Model):
    id = models.BigIntegerField(primary_key=True)
    typeid = models.BigIntegerField()
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_lti_types_config'


class MdlMessage(models.Model):
    id = models.BigIntegerField(primary_key=True)
    useridfrom = models.BigIntegerField()
    useridto = models.BigIntegerField()
    fullmessage = models.TextField()
    fullmessageformat = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    subject = models.TextField(blank=True)
    fullmessagehtml = models.TextField(blank=True)
    smallmessage = models.TextField(blank=True)
    notification = models.SmallIntegerField(blank=True, null=True)
    contexturl = models.TextField(blank=True)
    contexturlname = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_message'


class MdlMessageAirnotifierDevices(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userdeviceid = models.BigIntegerField(unique=True)
    enable = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_message_airnotifier_devices'


class MdlMessageContacts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    contactid = models.BigIntegerField()
    blocked = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_message_contacts'


class MdlMessageProcessors(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=166)
    enabled = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_message_processors'


class MdlMessageProviders(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    component = models.CharField(max_length=200)
    capability = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_message_providers'


class MdlMessageRead(models.Model):
    id = models.BigIntegerField(primary_key=True)
    useridfrom = models.BigIntegerField()
    useridto = models.BigIntegerField()
    fullmessage = models.TextField()
    fullmessageformat = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timeread = models.BigIntegerField()
    subject = models.TextField(blank=True)
    fullmessagehtml = models.TextField(blank=True)
    smallmessage = models.TextField(blank=True)
    notification = models.SmallIntegerField(blank=True, null=True)
    contexturl = models.TextField(blank=True)
    contexturlname = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_message_read'


class MdlMessageWorking(models.Model):
    id = models.BigIntegerField(primary_key=True)
    unreadmessageid = models.BigIntegerField()
    processorid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_message_working'


class MdlMessageinboundDatakeys(models.Model):
    id = models.BigIntegerField(primary_key=True)
    handler = models.BigIntegerField()
    datavalue = models.BigIntegerField()
    datakey = models.CharField(max_length=64, blank=True)
    timecreated = models.BigIntegerField()
    expires = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_messageinbound_datakeys'


class MdlMessageinboundHandlers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    component = models.CharField(max_length=100)
    classname = models.CharField(unique=True, max_length=255)
    defaultexpiration = models.BigIntegerField()
    validateaddress = models.SmallIntegerField()
    enabled = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_messageinbound_handlers'


class MdlMessageinboundMessagelist(models.Model):
    id = models.BigIntegerField(primary_key=True)
    messageid = models.TextField()
    userid = models.BigIntegerField()
    address = models.TextField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_messageinbound_messagelist'


class MdlMnetApplication(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    xmlrpc_server_url = models.CharField(max_length=255)
    sso_land_url = models.CharField(max_length=255)
    sso_jump_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_mnet_application'


class MdlMnetHost(models.Model):
    id = models.BigIntegerField(primary_key=True)
    deleted = models.SmallIntegerField()
    wwwroot = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=45)
    name = models.CharField(max_length=80)
    public_key = models.TextField()
    public_key_expires = models.BigIntegerField()
    transport = models.SmallIntegerField()
    last_connect_time = models.BigIntegerField()
    last_log_id = models.BigIntegerField()
    applicationid = models.BigIntegerField()
    force_theme = models.SmallIntegerField()
    theme = models.CharField(max_length=100, blank=True)
    portno = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_mnet_host'


class MdlMnetHost2Service(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hostid = models.BigIntegerField()
    serviceid = models.BigIntegerField()
    publish = models.SmallIntegerField()
    subscribe = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_mnet_host2service'


class MdlMnetLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hostid = models.BigIntegerField()
    remoteid = models.BigIntegerField()
    time = models.BigIntegerField()
    userid = models.BigIntegerField()
    ip = models.CharField(max_length=45)
    course = models.BigIntegerField()
    coursename = models.CharField(max_length=40)
    module = models.CharField(max_length=20)
    cmid = models.BigIntegerField()
    action = models.CharField(max_length=40)
    url = models.CharField(max_length=100)
    info = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_mnet_log'


class MdlMnetRemoteRpc(models.Model):
    id = models.BigIntegerField(primary_key=True)
    functionname = models.CharField(max_length=40)
    xmlrpcpath = models.CharField(max_length=80)
    plugintype = models.CharField(max_length=20)
    pluginname = models.CharField(max_length=20)
    enabled = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_mnet_remote_rpc'


class MdlMnetRemoteService2Rpc(models.Model):
    id = models.BigIntegerField(primary_key=True)
    serviceid = models.BigIntegerField()
    rpcid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_mnet_remote_service2rpc'


class MdlMnetRpc(models.Model):
    id = models.BigIntegerField(primary_key=True)
    functionname = models.CharField(max_length=40)
    xmlrpcpath = models.CharField(max_length=80)
    plugintype = models.CharField(max_length=20)
    pluginname = models.CharField(max_length=20)
    enabled = models.SmallIntegerField()
    help = models.TextField()
    profile = models.TextField()
    filename = models.CharField(max_length=100)
    classname = models.CharField(max_length=150, blank=True)
    static = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_mnet_rpc'


class MdlMnetService(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=40)
    apiversion = models.CharField(max_length=10)
    offer = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_mnet_service'


class MdlMnetService2Rpc(models.Model):
    id = models.BigIntegerField(primary_key=True)
    serviceid = models.BigIntegerField()
    rpcid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_mnet_service2rpc'


class MdlMnetSession(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    username = models.CharField(max_length=100)
    token = models.CharField(unique=True, max_length=40)
    mnethostid = models.BigIntegerField()
    useragent = models.CharField(max_length=40)
    confirm_timeout = models.BigIntegerField()
    session_id = models.CharField(max_length=40)
    expires = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_mnet_session'


class MdlMnetSsoAccessControl(models.Model):
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=100)
    mnet_host_id = models.BigIntegerField()
    accessctrl = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'mdl_mnet_sso_access_control'


class MdlMnetserviceEnrolCourses(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hostid = models.BigIntegerField()
    remoteid = models.BigIntegerField()
    categoryid = models.BigIntegerField()
    categoryname = models.CharField(max_length=255)
    sortorder = models.BigIntegerField()
    fullname = models.CharField(max_length=254)
    shortname = models.CharField(max_length=100)
    idnumber = models.CharField(max_length=100)
    summary = models.TextField()
    summaryformat = models.SmallIntegerField(blank=True, null=True)
    startdate = models.BigIntegerField()
    roleid = models.BigIntegerField()
    rolename = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_mnetservice_enrol_courses'


class MdlMnetserviceEnrolEnrolments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hostid = models.BigIntegerField()
    userid = models.BigIntegerField()
    remotecourseid = models.BigIntegerField()
    rolename = models.CharField(max_length=255)
    enroltime = models.BigIntegerField()
    enroltype = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'mdl_mnetservice_enrol_enrolments'


class MdlModules(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    cron = models.BigIntegerField()
    lastcron = models.BigIntegerField()
    search = models.CharField(max_length=255)
    visible = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_modules'


class MdlMyPages(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=200)
    private = models.SmallIntegerField()
    sortorder = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_my_pages'


class MdlPage(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()
    content = models.TextField(blank=True)
    contentformat = models.SmallIntegerField()
    legacyfiles = models.SmallIntegerField()
    legacyfileslast = models.BigIntegerField(blank=True, null=True)
    display = models.SmallIntegerField()
    displayoptions = models.TextField(blank=True)
    revision = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_page'


class MdlPortfolioInstance(models.Model):
    id = models.BigIntegerField(primary_key=True)
    plugin = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    visible = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_portfolio_instance'


class MdlPortfolioInstanceConfig(models.Model):
    id = models.BigIntegerField(primary_key=True)
    instance = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_portfolio_instance_config'


class MdlPortfolioInstanceUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    instance = models.BigIntegerField()
    userid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_portfolio_instance_user'


class MdlPortfolioLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    time = models.BigIntegerField()
    portfolio = models.BigIntegerField()
    caller_class = models.CharField(max_length=150)
    caller_file = models.CharField(max_length=255)
    caller_sha1 = models.CharField(max_length=255)
    tempdataid = models.BigIntegerField()
    returnurl = models.CharField(max_length=255)
    continueurl = models.CharField(max_length=255)
    caller_component = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_portfolio_log'


class MdlPortfolioMaharaQueue(models.Model):
    id = models.BigIntegerField(primary_key=True)
    transferid = models.BigIntegerField()
    token = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mdl_portfolio_mahara_queue'


class MdlPortfolioTempdata(models.Model):
    id = models.BigIntegerField(primary_key=True)
    data = models.TextField(blank=True)
    expirytime = models.BigIntegerField()
    userid = models.BigIntegerField()
    instance = models.BigIntegerField(blank=True, null=True)
    queued = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_portfolio_tempdata'


class MdlPost(models.Model):
    id = models.BigIntegerField(primary_key=True)
    module = models.CharField(max_length=20)
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    moduleid = models.BigIntegerField()
    coursemoduleid = models.BigIntegerField()
    subject = models.CharField(max_length=128)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    uniquehash = models.CharField(max_length=255)
    rating = models.BigIntegerField()
    format = models.BigIntegerField()
    attachment = models.CharField(max_length=100, blank=True)
    publishstate = models.CharField(max_length=20)
    lastmodified = models.BigIntegerField()
    created = models.BigIntegerField()
    usermodified = models.BigIntegerField(blank=True, null=True)
    summaryformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_post'


class MdlProfiling(models.Model):
    id = models.BigIntegerField(primary_key=True)
    runid = models.CharField(unique=True, max_length=32)
    url = models.CharField(max_length=255)
    data = models.TextField()
    totalexecutiontime = models.BigIntegerField()
    totalcputime = models.BigIntegerField()
    totalcalls = models.BigIntegerField()
    totalmemory = models.BigIntegerField()
    runreference = models.SmallIntegerField()
    runcomment = models.CharField(max_length=255)
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_profiling'


class MdlQtypeEssayOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionid = models.BigIntegerField(unique=True)
    responseformat = models.CharField(max_length=16)
    responsefieldlines = models.SmallIntegerField()
    attachments = models.SmallIntegerField()
    graderinfo = models.TextField(blank=True)
    graderinfoformat = models.SmallIntegerField()
    responsetemplate = models.TextField(blank=True)
    responsetemplateformat = models.SmallIntegerField()
    responserequired = models.SmallIntegerField()
    attachmentsrequired = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_qtype_essay_options'


class MdlQtypeMatchOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionid = models.BigIntegerField(unique=True)
    shuffleanswers = models.SmallIntegerField()
    correctfeedback = models.TextField()
    correctfeedbackformat = models.SmallIntegerField()
    partiallycorrectfeedback = models.TextField()
    partiallycorrectfeedbackformat = models.SmallIntegerField()
    incorrectfeedback = models.TextField()
    incorrectfeedbackformat = models.SmallIntegerField()
    shownumcorrect = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_qtype_match_options'


class MdlQtypeMatchSubquestions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionid = models.BigIntegerField()
    questiontext = models.TextField()
    answertext = models.CharField(max_length=255)
    questiontextformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_qtype_match_subquestions'


class MdlQtypeMultichoiceOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionid = models.BigIntegerField(unique=True)
    layout = models.SmallIntegerField()
    single = models.SmallIntegerField()
    shuffleanswers = models.SmallIntegerField()
    correctfeedback = models.TextField()
    partiallycorrectfeedback = models.TextField()
    incorrectfeedback = models.TextField()
    answernumbering = models.CharField(max_length=10)
    correctfeedbackformat = models.SmallIntegerField()
    partiallycorrectfeedbackformat = models.SmallIntegerField()
    incorrectfeedbackformat = models.SmallIntegerField()
    shownumcorrect = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_qtype_multichoice_options'


class MdlQtypeRandomsamatchOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionid = models.BigIntegerField(unique=True)
    choose = models.BigIntegerField()
    subcats = models.SmallIntegerField()
    correctfeedback = models.TextField()
    correctfeedbackformat = models.SmallIntegerField()
    partiallycorrectfeedback = models.TextField()
    partiallycorrectfeedbackformat = models.SmallIntegerField()
    incorrectfeedback = models.TextField()
    incorrectfeedbackformat = models.SmallIntegerField()
    shownumcorrect = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_qtype_randomsamatch_options'


class MdlQtypeShortanswerOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionid = models.BigIntegerField(unique=True)
    usecase = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_qtype_shortanswer_options'


class MdlQuestion(models.Model):
    id = models.BigIntegerField(primary_key=True)
    category = models.BigIntegerField()
    parent = models.BigIntegerField()
    name = models.CharField(max_length=255)
    questiontext = models.TextField()
    questiontextformat = models.SmallIntegerField()
    generalfeedback = models.TextField()
    defaultmark = models.DecimalField(max_digits=12, decimal_places=7)
    penalty = models.DecimalField(max_digits=12, decimal_places=7)
    qtype = models.CharField(max_length=20)
    length = models.BigIntegerField()
    stamp = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    hidden = models.SmallIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    createdby = models.BigIntegerField(blank=True, null=True)
    modifiedby = models.BigIntegerField(blank=True, null=True)
    generalfeedbackformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question'


class MdlQuestionAnswers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    answer = models.TextField()
    fraction = models.DecimalField(max_digits=12, decimal_places=7)
    feedback = models.TextField()
    answerformat = models.SmallIntegerField()
    feedbackformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_answers'


class MdlQuestionAttemptStepData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    attemptstepid = models.BigIntegerField()
    name = models.CharField(max_length=32)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_question_attempt_step_data'


class MdlQuestionAttemptSteps(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionattemptid = models.BigIntegerField()
    sequencenumber = models.BigIntegerField()
    state = models.CharField(max_length=13)
    fraction = models.DecimalField(max_digits=12, decimal_places=7, blank=True, null=True)
    timecreated = models.BigIntegerField()
    userid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_question_attempt_steps'


class MdlQuestionAttempts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionusageid = models.BigIntegerField()
    slot = models.BigIntegerField()
    behaviour = models.CharField(max_length=32)
    questionid = models.BigIntegerField()
    maxmark = models.DecimalField(max_digits=12, decimal_places=7)
    minfraction = models.DecimalField(max_digits=12, decimal_places=7)
    flagged = models.SmallIntegerField()
    questionsummary = models.TextField(blank=True)
    rightanswer = models.TextField(blank=True)
    responsesummary = models.TextField(blank=True)
    timemodified = models.BigIntegerField()
    variant = models.BigIntegerField()
    maxfraction = models.DecimalField(max_digits=12, decimal_places=7)

    class Meta:
        managed = False
        db_table = 'mdl_question_attempts'


class MdlQuestionCalculated(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    answer = models.BigIntegerField()
    tolerance = models.CharField(max_length=20)
    tolerancetype = models.BigIntegerField()
    correctanswerlength = models.BigIntegerField()
    correctanswerformat = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_calculated'


class MdlQuestionCalculatedOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    synchronize = models.SmallIntegerField()
    single = models.SmallIntegerField()
    shuffleanswers = models.SmallIntegerField()
    correctfeedback = models.TextField(blank=True)
    partiallycorrectfeedback = models.TextField(blank=True)
    incorrectfeedback = models.TextField(blank=True)
    answernumbering = models.CharField(max_length=10)
    correctfeedbackformat = models.SmallIntegerField()
    partiallycorrectfeedbackformat = models.SmallIntegerField()
    incorrectfeedbackformat = models.SmallIntegerField()
    shownumcorrect = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_calculated_options'


class MdlQuestionCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    info = models.TextField()
    stamp = models.CharField(max_length=255)
    parent = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    contextid = models.BigIntegerField()
    infoformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_categories'


class MdlQuestionDatasetDefinitions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    category = models.BigIntegerField()
    name = models.CharField(max_length=255)
    type = models.BigIntegerField()
    options = models.CharField(max_length=255)
    itemcount = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_dataset_definitions'


class MdlQuestionDatasetItems(models.Model):
    id = models.BigIntegerField(primary_key=True)
    definition = models.BigIntegerField()
    itemnumber = models.BigIntegerField()
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_question_dataset_items'


class MdlQuestionDatasets(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    datasetdefinition = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_datasets'


class MdlQuestionHints(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionid = models.BigIntegerField()
    hint = models.TextField()
    hintformat = models.SmallIntegerField()
    shownumcorrect = models.SmallIntegerField(blank=True, null=True)
    clearwrong = models.SmallIntegerField(blank=True, null=True)
    options = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_question_hints'


class MdlQuestionMultianswer(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    sequence = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_question_multianswer'


class MdlQuestionNumerical(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    answer = models.BigIntegerField()
    tolerance = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_question_numerical'


class MdlQuestionNumericalOptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    showunits = models.SmallIntegerField()
    unitsleft = models.SmallIntegerField()
    unitgradingtype = models.SmallIntegerField()
    unitpenalty = models.DecimalField(max_digits=12, decimal_places=7)

    class Meta:
        managed = False
        db_table = 'mdl_question_numerical_options'


class MdlQuestionNumericalUnits(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    multiplier = models.DecimalField(max_digits=40, decimal_places=20)
    unit = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mdl_question_numerical_units'


class MdlQuestionResponseAnalysis(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hashcode = models.CharField(max_length=40)
    timemodified = models.BigIntegerField()
    questionid = models.BigIntegerField()
    subqid = models.CharField(max_length=100)
    aid = models.CharField(max_length=100, blank=True)
    response = models.TextField(blank=True)
    credit = models.DecimalField(max_digits=15, decimal_places=5)
    variant = models.BigIntegerField(blank=True, null=True)
    whichtries = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_question_response_analysis'


class MdlQuestionResponseCount(models.Model):
    id = models.BigIntegerField(primary_key=True)
    analysisid = models.BigIntegerField()
    try_field = models.BigIntegerField(db_column='try')  # Field renamed because it was a Python reserved word.
    rcount = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_response_count'


class MdlQuestionStatistics(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hashcode = models.CharField(max_length=40)
    timemodified = models.BigIntegerField()
    questionid = models.BigIntegerField()
    slot = models.BigIntegerField(blank=True, null=True)
    subquestion = models.SmallIntegerField()
    s = models.BigIntegerField()
    effectiveweight = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    negcovar = models.SmallIntegerField()
    discriminationindex = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    discriminativeefficiency = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    sd = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True)
    facility = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True)
    subquestions = models.TextField(blank=True)
    maxmark = models.DecimalField(max_digits=12, decimal_places=7, blank=True, null=True)
    positions = models.TextField(blank=True)
    randomguessscore = models.DecimalField(max_digits=12, decimal_places=7, blank=True, null=True)
    variant = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_question_statistics'


class MdlQuestionTruefalse(models.Model):
    id = models.BigIntegerField(primary_key=True)
    question = models.BigIntegerField()
    trueanswer = models.BigIntegerField()
    falseanswer = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_question_truefalse'


class MdlQuestionUsages(models.Model):
    id = models.BigIntegerField(primary_key=True)
    component = models.CharField(max_length=255)
    contextid = models.BigIntegerField()
    preferredbehaviour = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'mdl_question_usages'


class MdlQuiz(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    timeopen = models.BigIntegerField()
    timeclose = models.BigIntegerField()
    attempts = models.IntegerField()
    attemptonlast = models.SmallIntegerField()
    grademethod = models.SmallIntegerField()
    decimalpoints = models.SmallIntegerField()
    questionsperpage = models.BigIntegerField()
    shufflequestions = models.SmallIntegerField()
    shuffleanswers = models.SmallIntegerField()
    sumgrades = models.DecimalField(max_digits=10, decimal_places=5)
    grade = models.DecimalField(max_digits=10, decimal_places=5)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    password = models.CharField(max_length=255)
    subnet = models.CharField(max_length=255)
    delay1 = models.BigIntegerField()
    delay2 = models.BigIntegerField()
    timelimit = models.BigIntegerField()
    showuserpicture = models.SmallIntegerField()
    questiondecimalpoints = models.SmallIntegerField()
    introformat = models.SmallIntegerField()
    showblocks = models.SmallIntegerField()
    preferredbehaviour = models.CharField(max_length=32)
    reviewattempt = models.IntegerField()
    reviewcorrectness = models.IntegerField()
    reviewmarks = models.IntegerField()
    reviewspecificfeedback = models.IntegerField()
    reviewgeneralfeedback = models.IntegerField()
    reviewrightanswer = models.IntegerField()
    reviewoverallfeedback = models.IntegerField()
    browsersecurity = models.CharField(max_length=32)
    navmethod = models.CharField(max_length=16)
    overduehandling = models.CharField(max_length=16)
    graceperiod = models.BigIntegerField()
    completionattemptsexhausted = models.SmallIntegerField(blank=True, null=True)
    completionpass = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_quiz'


class MdlQuizAttempts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    uniqueid = models.BigIntegerField(unique=True)
    quiz = models.BigIntegerField()
    userid = models.BigIntegerField()
    attempt = models.IntegerField()
    sumgrades = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    timestart = models.BigIntegerField()
    timefinish = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    layout = models.TextField()
    preview = models.SmallIntegerField()
    currentpage = models.BigIntegerField()
    state = models.CharField(max_length=16)
    timecheckstate = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_quiz_attempts'


class MdlQuizFeedback(models.Model):
    id = models.BigIntegerField(primary_key=True)
    quizid = models.BigIntegerField()
    feedbacktext = models.TextField()
    mingrade = models.DecimalField(max_digits=10, decimal_places=5)
    maxgrade = models.DecimalField(max_digits=10, decimal_places=5)
    feedbacktextformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_quiz_feedback'


class MdlQuizGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    quiz = models.BigIntegerField()
    userid = models.BigIntegerField()
    grade = models.DecimalField(max_digits=10, decimal_places=5)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_quiz_grades'


class MdlQuizOverrides(models.Model):
    id = models.BigIntegerField(primary_key=True)
    quiz = models.BigIntegerField()
    groupid = models.BigIntegerField(blank=True, null=True)
    userid = models.BigIntegerField(blank=True, null=True)
    timeopen = models.BigIntegerField(blank=True, null=True)
    timeclose = models.BigIntegerField(blank=True, null=True)
    timelimit = models.BigIntegerField(blank=True, null=True)
    attempts = models.IntegerField(blank=True, null=True)
    password = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_quiz_overrides'


class MdlQuizOverviewRegrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    questionusageid = models.BigIntegerField()
    newfraction = models.DecimalField(max_digits=12, decimal_places=7, blank=True, null=True)
    oldfraction = models.DecimalField(max_digits=12, decimal_places=7, blank=True, null=True)
    regraded = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    slot = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_quiz_overview_regrades'


class MdlQuizReports(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255, blank=True)
    displayorder = models.BigIntegerField()
    capability = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_quiz_reports'


class MdlQuizSlots(models.Model):
    id = models.BigIntegerField(primary_key=True)
    quizid = models.BigIntegerField()
    questionid = models.BigIntegerField()
    maxmark = models.DecimalField(max_digits=12, decimal_places=7)
    slot = models.BigIntegerField()
    page = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_quiz_slots'


class MdlQuizStatistics(models.Model):
    id = models.BigIntegerField(primary_key=True)
    hashcode = models.CharField(max_length=40)
    whichattempts = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    firstattemptscount = models.BigIntegerField()
    highestattemptscount = models.BigIntegerField()
    lastattemptscount = models.BigIntegerField()
    allattemptscount = models.BigIntegerField()
    firstattemptsavg = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    highestattemptsavg = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    lastattemptsavg = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    allattemptsavg = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    median = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    standarddeviation = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    skewness = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True)
    kurtosis = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
    cic = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True)
    errorratio = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True)
    standarderror = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_quiz_statistics'


class MdlRating(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    itemid = models.BigIntegerField()
    scaleid = models.BigIntegerField()
    rating = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    component = models.CharField(max_length=100)
    ratingarea = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mdl_rating'


class MdlRegistrationHubs(models.Model):
    id = models.BigIntegerField(primary_key=True)
    token = models.CharField(max_length=255)
    hubname = models.CharField(max_length=255)
    huburl = models.CharField(max_length=255)
    confirmed = models.SmallIntegerField()
    secret = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_registration_hubs'


class MdlRepository(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=255)
    visible = models.SmallIntegerField(blank=True, null=True)
    sortorder = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_repository'


class MdlRepositoryInstanceConfig(models.Model):
    id = models.BigIntegerField(primary_key=True)
    instanceid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_repository_instance_config'


class MdlRepositoryInstances(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    typeid = models.BigIntegerField()
    userid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    timecreated = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    readonly = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_repository_instances'


class MdlResource(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    timemodified = models.BigIntegerField()
    introformat = models.SmallIntegerField()
    tobemigrated = models.SmallIntegerField()
    legacyfiles = models.SmallIntegerField()
    legacyfileslast = models.BigIntegerField(blank=True, null=True)
    display = models.SmallIntegerField()
    displayoptions = models.TextField(blank=True)
    filterfiles = models.SmallIntegerField()
    revision = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_resource'


class MdlResourceOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30)
    reference = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()
    alltext = models.TextField()
    popup = models.TextField()
    options = models.CharField(max_length=255)
    timemodified = models.BigIntegerField()
    oldid = models.BigIntegerField(unique=True)
    cmid = models.BigIntegerField(blank=True, null=True)
    newmodule = models.CharField(max_length=50, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)
    migrated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_resource_old'


class MdlRole(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    shortname = models.CharField(unique=True, max_length=100)
    description = models.TextField()
    sortorder = models.BigIntegerField(unique=True)
    archetype = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'mdl_role'


class MdlRoleAllowAssign(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    allowassign = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_role_allow_assign'


class MdlRoleAllowOverride(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    allowoverride = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_role_allow_override'


class MdlRoleAllowSwitch(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    allowswitch = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_role_allow_switch'


class MdlRoleAssignments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    component = models.CharField(max_length=100)
    sortorder = models.BigIntegerField()
    itemid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_role_assignments'


class MdlRoleCapabilities(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    roleid = models.BigIntegerField()
    capability = models.CharField(max_length=255)
    permission = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    modifierid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_role_capabilities'


class MdlRoleContextLevels(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    contextlevel = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_role_context_levels'


class MdlRoleNames(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_role_names'


class MdlRoleSortorder(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    roleid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    sortoder = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_role_sortorder'


class MdlScale(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    userid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    scale = models.TextField()
    description = models.TextField()
    timemodified = models.BigIntegerField()
    descriptionformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_scale'


class MdlScaleHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.BigIntegerField()
    oldid = models.BigIntegerField()
    source = models.CharField(max_length=255, blank=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    loggeduser = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField()
    userid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    scale = models.TextField()
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_scale_history'


class MdlScorm(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    intro = models.TextField()
    version = models.CharField(max_length=9)
    maxgrade = models.FloatField()
    grademethod = models.SmallIntegerField()
    maxattempt = models.BigIntegerField()
    updatefreq = models.SmallIntegerField()
    md5hash = models.CharField(max_length=32)
    launch = models.BigIntegerField()
    skipview = models.SmallIntegerField()
    hidebrowse = models.SmallIntegerField()
    hidetoc = models.SmallIntegerField()
    auto = models.SmallIntegerField()
    popup = models.SmallIntegerField()
    options = models.CharField(max_length=255)
    width = models.BigIntegerField()
    height = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    whatgrade = models.BigIntegerField()
    scormtype = models.CharField(max_length=50)
    sha1hash = models.CharField(max_length=40, blank=True)
    revision = models.BigIntegerField()
    forcecompleted = models.SmallIntegerField()
    forcenewattempt = models.SmallIntegerField()
    lastattemptlock = models.SmallIntegerField()
    displayattemptstatus = models.SmallIntegerField()
    displaycoursestructure = models.SmallIntegerField()
    timeopen = models.BigIntegerField()
    timeclose = models.BigIntegerField()
    introformat = models.SmallIntegerField()
    completionstatusrequired = models.SmallIntegerField(blank=True, null=True)
    completionscorerequired = models.SmallIntegerField(blank=True, null=True)
    nav = models.SmallIntegerField()
    navpositionleft = models.BigIntegerField(blank=True, null=True)
    navpositiontop = models.BigIntegerField(blank=True, null=True)
    displayactivityname = models.SmallIntegerField()
    autocommit = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_scorm'


class MdlScormAiccSession(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    scormid = models.BigIntegerField()
    hacpsession = models.CharField(max_length=255)
    scoid = models.BigIntegerField(blank=True, null=True)
    scormmode = models.CharField(max_length=50, blank=True)
    scormstatus = models.CharField(max_length=255, blank=True)
    attempt = models.BigIntegerField(blank=True, null=True)
    lessonstatus = models.CharField(max_length=255, blank=True)
    sessiontime = models.CharField(max_length=255, blank=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_scorm_aicc_session'


class MdlScormScoes(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scorm = models.BigIntegerField()
    manifest = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    parent = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255)
    launch = models.TextField()
    scormtype = models.CharField(max_length=5)
    title = models.CharField(max_length=255)
    sortorder = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_scorm_scoes'


class MdlScormScoesData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scoid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_scorm_scoes_data'


class MdlScormScoesTrack(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    scormid = models.BigIntegerField()
    scoid = models.BigIntegerField()
    attempt = models.BigIntegerField()
    element = models.CharField(max_length=255)
    value = models.TextField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_scorm_scoes_track'


class MdlScormSeqMapinfo(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scoid = models.BigIntegerField()
    objectiveid = models.BigIntegerField()
    targetobjectiveid = models.BigIntegerField()
    readsatisfiedstatus = models.SmallIntegerField()
    readnormalizedmeasure = models.SmallIntegerField()
    writesatisfiedstatus = models.SmallIntegerField()
    writenormalizedmeasure = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_scorm_seq_mapinfo'


class MdlScormSeqObjective(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scoid = models.BigIntegerField()
    primaryobj = models.SmallIntegerField()
    objectiveid = models.CharField(max_length=255)
    satisfiedbymeasure = models.SmallIntegerField()
    minnormalizedmeasure = models.FloatField()

    class Meta:
        managed = False
        db_table = 'mdl_scorm_seq_objective'


class MdlScormSeqRolluprule(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scoid = models.BigIntegerField()
    childactivityset = models.CharField(max_length=15)
    minimumcount = models.BigIntegerField()
    minimumpercent = models.FloatField()
    conditioncombination = models.CharField(max_length=3)
    action = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'mdl_scorm_seq_rolluprule'


class MdlScormSeqRolluprulecond(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scoid = models.BigIntegerField()
    rollupruleid = models.BigIntegerField()
    operator = models.CharField(max_length=5)
    cond = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'mdl_scorm_seq_rolluprulecond'


class MdlScormSeqRulecond(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scoid = models.BigIntegerField()
    ruleconditionsid = models.BigIntegerField()
    refrencedobjective = models.CharField(max_length=255)
    measurethreshold = models.FloatField()
    operator = models.CharField(max_length=5)
    cond = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'mdl_scorm_seq_rulecond'


class MdlScormSeqRuleconds(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scoid = models.BigIntegerField()
    conditioncombination = models.CharField(max_length=3)
    ruletype = models.SmallIntegerField()
    action = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'mdl_scorm_seq_ruleconds'


class MdlSessions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    state = models.BigIntegerField()
    sid = models.CharField(unique=True, max_length=128)
    userid = models.BigIntegerField()
    sessdata = models.TextField(blank=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    firstip = models.CharField(max_length=45, blank=True)
    lastip = models.CharField(max_length=45, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_sessions'


class MdlStatsDaily(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    timeend = models.BigIntegerField()
    roleid = models.BigIntegerField()
    stattype = models.CharField(max_length=20)
    stat1 = models.BigIntegerField()
    stat2 = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_stats_daily'


class MdlStatsMonthly(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    timeend = models.BigIntegerField()
    roleid = models.BigIntegerField()
    stattype = models.CharField(max_length=20)
    stat1 = models.BigIntegerField()
    stat2 = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_stats_monthly'


class MdlStatsUserDaily(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    userid = models.BigIntegerField()
    roleid = models.BigIntegerField()
    timeend = models.BigIntegerField()
    statsreads = models.BigIntegerField()
    statswrites = models.BigIntegerField()
    stattype = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'mdl_stats_user_daily'


class MdlStatsUserMonthly(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    userid = models.BigIntegerField()
    roleid = models.BigIntegerField()
    timeend = models.BigIntegerField()
    statsreads = models.BigIntegerField()
    statswrites = models.BigIntegerField()
    stattype = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'mdl_stats_user_monthly'


class MdlStatsUserWeekly(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    userid = models.BigIntegerField()
    roleid = models.BigIntegerField()
    timeend = models.BigIntegerField()
    statsreads = models.BigIntegerField()
    statswrites = models.BigIntegerField()
    stattype = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'mdl_stats_user_weekly'


class MdlStatsWeekly(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    timeend = models.BigIntegerField()
    roleid = models.BigIntegerField()
    stattype = models.CharField(max_length=20)
    stat1 = models.BigIntegerField()
    stat2 = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_stats_weekly'


class MdlSurvey(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    template = models.BigIntegerField()
    days = models.IntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    questions = models.CharField(max_length=255)
    introformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_survey'


class MdlSurveyAnalysis(models.Model):
    id = models.BigIntegerField(primary_key=True)
    survey = models.BigIntegerField()
    userid = models.BigIntegerField()
    notes = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_survey_analysis'


class MdlSurveyAnswers(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    survey = models.BigIntegerField()
    question = models.BigIntegerField()
    time = models.BigIntegerField()
    answer1 = models.TextField()
    answer2 = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_survey_answers'


class MdlSurveyQuestions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    text = models.CharField(max_length=255)
    shorttext = models.CharField(max_length=30)
    multi = models.CharField(max_length=100)
    intro = models.CharField(max_length=50)
    type = models.SmallIntegerField()
    options = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_survey_questions'


class MdlTag(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    tagtype = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField()
    flag = models.SmallIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    rawname = models.CharField(max_length=255)
    userid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tag'


class MdlTagCorrelation(models.Model):
    id = models.BigIntegerField(primary_key=True)
    correlatedtags = models.TextField()
    tagid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tag_correlation'


class MdlTagInstance(models.Model):
    id = models.BigIntegerField(primary_key=True)
    itemtype = models.CharField(max_length=255)
    timemodified = models.BigIntegerField()
    tagid = models.BigIntegerField()
    itemid = models.BigIntegerField()
    ordering = models.BigIntegerField(blank=True, null=True)
    tiuserid = models.BigIntegerField()
    component = models.CharField(max_length=100, blank=True)
    contextid = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tag_instance'


class MdlTaskAdhoc(models.Model):
    id = models.BigIntegerField(primary_key=True)
    component = models.CharField(max_length=255)
    classname = models.CharField(max_length=255)
    nextruntime = models.BigIntegerField()
    faildelay = models.BigIntegerField(blank=True, null=True)
    customdata = models.TextField(blank=True)
    blocking = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_task_adhoc'


class MdlTaskScheduled(models.Model):
    id = models.BigIntegerField(primary_key=True)
    component = models.CharField(max_length=255)
    classname = models.CharField(unique=True, max_length=255)
    lastruntime = models.BigIntegerField(blank=True, null=True)
    nextruntime = models.BigIntegerField(blank=True, null=True)
    blocking = models.SmallIntegerField()
    minute = models.CharField(max_length=25)
    hour = models.CharField(max_length=25)
    day = models.CharField(max_length=25)
    month = models.CharField(max_length=25)
    dayofweek = models.CharField(max_length=25)
    faildelay = models.BigIntegerField(blank=True, null=True)
    customised = models.SmallIntegerField()
    disabled = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_task_scheduled'


class MdlTimezone(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    year = models.BigIntegerField()
    tzrule = models.CharField(max_length=20)
    gmtoff = models.BigIntegerField()
    dstoff = models.BigIntegerField()
    dst_month = models.SmallIntegerField()
    dst_startday = models.SmallIntegerField()
    dst_weekday = models.SmallIntegerField()
    dst_skipweeks = models.SmallIntegerField()
    dst_time = models.CharField(max_length=6)
    std_month = models.SmallIntegerField()
    std_startday = models.SmallIntegerField()
    std_weekday = models.SmallIntegerField()
    std_skipweeks = models.SmallIntegerField()
    std_time = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'mdl_timezone'


class MdlToolCustomlang(models.Model):
    id = models.BigIntegerField(primary_key=True)
    lang = models.CharField(max_length=20)
    componentid = models.BigIntegerField()
    stringid = models.CharField(max_length=255)
    original = models.TextField()
    master = models.TextField(blank=True)
    local = models.TextField(blank=True)
    timemodified = models.BigIntegerField()
    timecustomized = models.BigIntegerField(blank=True, null=True)
    outdated = models.SmallIntegerField(blank=True, null=True)
    modified = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_tool_customlang'


class MdlToolCustomlangComponents(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_tool_customlang_components'


class MdlToolMonitorEvents(models.Model):
    id = models.BigIntegerField(primary_key=True)
    eventname = models.CharField(max_length=254)
    contextid = models.BigIntegerField()
    contextlevel = models.BigIntegerField()
    contextinstanceid = models.BigIntegerField()
    link = models.CharField(max_length=254)
    courseid = models.BigIntegerField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tool_monitor_events'


class MdlToolMonitorHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    sid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timesent = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tool_monitor_history'


class MdlToolMonitorRules(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField()
    name = models.CharField(max_length=254)
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField()
    plugin = models.CharField(max_length=254)
    eventname = models.CharField(max_length=254)
    template = models.TextField()
    templateformat = models.SmallIntegerField()
    frequency = models.SmallIntegerField()
    timewindow = models.IntegerField()
    timemodified = models.BigIntegerField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tool_monitor_rules'


class MdlToolMonitorSubscriptions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    courseid = models.BigIntegerField()
    ruleid = models.BigIntegerField()
    cmid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    lastnotificationsent = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tool_monitor_subscriptions'


class MdlUnittestCourseModules(models.Model):
    id = models.BigIntegerField(primary_key=True)
    groupmembersonly = models.SmallIntegerField()
    groupingid = models.BigIntegerField()
    groupmode = models.SmallIntegerField()
    visibleold = models.SmallIntegerField()
    visible = models.SmallIntegerField()
    indent = models.IntegerField()
    score = models.SmallIntegerField()
    added = models.BigIntegerField()
    idnumber = models.CharField(max_length=100, blank=True)
    section = models.BigIntegerField()
    instance = models.BigIntegerField()
    module = models.BigIntegerField()
    course = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_course_modules'


class MdlUnittestGradeCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    timemodified = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    aggregatesubcats = models.SmallIntegerField()
    aggregateoutcomes = models.SmallIntegerField()
    aggregateonlygraded = models.SmallIntegerField()
    droplow = models.BigIntegerField()
    keephigh = models.BigIntegerField()
    aggregation = models.BigIntegerField()
    fullname = models.CharField(max_length=255)
    path = models.CharField(max_length=255, blank=True)
    depth = models.BigIntegerField()
    parent = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_categories'


class MdlUnittestGradeCategoriesHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    aggregatesubcats = models.SmallIntegerField()
    aggregateoutcomes = models.SmallIntegerField()
    aggregateonlygraded = models.SmallIntegerField()
    droplow = models.BigIntegerField()
    keephigh = models.BigIntegerField()
    aggregation = models.BigIntegerField()
    fullname = models.CharField(max_length=255)
    path = models.CharField(max_length=255, blank=True)
    depth = models.BigIntegerField()
    parent = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField()
    loggeduser = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)
    oldid = models.BigIntegerField()
    action = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_categories_history'


class MdlUnittestGradeGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField(blank=True, null=True)
    informationformat = models.BigIntegerField()
    information = models.TextField(blank=True)
    feedbackformat = models.BigIntegerField()
    feedback = models.TextField(blank=True)
    excluded = models.BigIntegerField()
    overridden = models.BigIntegerField()
    exported = models.BigIntegerField()
    locktime = models.BigIntegerField()
    locked = models.BigIntegerField()
    hidden = models.BigIntegerField()
    finalgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    usermodified = models.BigIntegerField(blank=True, null=True)
    rawscaleid = models.BigIntegerField(blank=True, null=True)
    rawgrademin = models.DecimalField(max_digits=10, decimal_places=5)
    rawgrademax = models.DecimalField(max_digits=10, decimal_places=5)
    rawgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    userid = models.BigIntegerField()
    itemid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_grades'


class MdlUnittestGradeGradesHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    informationformat = models.BigIntegerField()
    information = models.TextField(blank=True)
    feedbackformat = models.BigIntegerField()
    feedback = models.TextField(blank=True)
    excluded = models.BigIntegerField()
    overridden = models.BigIntegerField()
    exported = models.BigIntegerField()
    locktime = models.BigIntegerField()
    locked = models.BigIntegerField()
    hidden = models.BigIntegerField()
    finalgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    usermodified = models.BigIntegerField(blank=True, null=True)
    rawscaleid = models.BigIntegerField(blank=True, null=True)
    rawgrademin = models.DecimalField(max_digits=10, decimal_places=5)
    rawgrademax = models.DecimalField(max_digits=10, decimal_places=5)
    rawgrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    userid = models.BigIntegerField()
    itemid = models.BigIntegerField()
    loggeduser = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)
    oldid = models.BigIntegerField()
    action = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_grades_history'


class MdlUnittestGradeItems(models.Model):
    id = models.BigIntegerField(primary_key=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField(blank=True, null=True)
    needsupdate = models.BigIntegerField()
    deleted = models.BigIntegerField()
    locktime = models.BigIntegerField()
    locked = models.BigIntegerField()
    hidden = models.BigIntegerField()
    decimals = models.SmallIntegerField(blank=True, null=True)
    display = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    plusfactor = models.DecimalField(max_digits=10, decimal_places=5)
    multfactor = models.DecimalField(max_digits=10, decimal_places=5)
    gradepass = models.DecimalField(max_digits=10, decimal_places=5)
    outcomeid = models.BigIntegerField(blank=True, null=True)
    scaleid = models.BigIntegerField(blank=True, null=True)
    grademin = models.DecimalField(max_digits=10, decimal_places=5)
    grademax = models.DecimalField(max_digits=10, decimal_places=5)
    gradetype = models.SmallIntegerField()
    calculation = models.TextField(blank=True)
    idnumber = models.CharField(max_length=255, blank=True)
    iteminfo = models.TextField(blank=True)
    itemnumber = models.BigIntegerField(blank=True, null=True)
    iteminstance = models.BigIntegerField(blank=True, null=True)
    itemmodule = models.CharField(max_length=30, blank=True)
    itemtype = models.CharField(max_length=30)
    itemname = models.CharField(max_length=255, blank=True)
    categoryid = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_items'


class MdlUnittestGradeItemsHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    needsupdate = models.BigIntegerField()
    locktime = models.BigIntegerField()
    locked = models.BigIntegerField()
    hidden = models.BigIntegerField()
    decimals = models.SmallIntegerField(blank=True, null=True)
    display = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    plusfactor = models.DecimalField(max_digits=10, decimal_places=5)
    multfactor = models.DecimalField(max_digits=10, decimal_places=5)
    gradepass = models.DecimalField(max_digits=10, decimal_places=5)
    outcomeid = models.BigIntegerField(blank=True, null=True)
    scaleid = models.BigIntegerField(blank=True, null=True)
    grademin = models.DecimalField(max_digits=10, decimal_places=5)
    grademax = models.DecimalField(max_digits=10, decimal_places=5)
    gradetype = models.SmallIntegerField()
    calculation = models.TextField(blank=True)
    idnumber = models.CharField(max_length=255, blank=True)
    iteminfo = models.TextField(blank=True)
    itemnumber = models.BigIntegerField(blank=True, null=True)
    iteminstance = models.BigIntegerField(blank=True, null=True)
    itemmodule = models.CharField(max_length=30, blank=True)
    itemtype = models.CharField(max_length=30)
    itemname = models.CharField(max_length=255, blank=True)
    categoryid = models.BigIntegerField(blank=True, null=True)
    courseid = models.BigIntegerField(blank=True, null=True)
    loggeduser = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)
    oldid = models.BigIntegerField()
    action = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_items_history'


class MdlUnittestGradeOutcomes(models.Model):
    id = models.BigIntegerField(primary_key=True)
    usermodified = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField(blank=True, null=True)
    scaleid = models.BigIntegerField(blank=True, null=True)
    fullname = models.TextField()
    shortname = models.CharField(max_length=255)
    courseid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_outcomes'


class MdlUnittestGradeOutcomesHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    scaleid = models.BigIntegerField(blank=True, null=True)
    fullname = models.TextField()
    shortname = models.CharField(max_length=255)
    courseid = models.BigIntegerField(blank=True, null=True)
    loggeduser = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)
    oldid = models.BigIntegerField()
    action = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_grade_outcomes_history'


class MdlUnittestModules(models.Model):
    id = models.BigIntegerField(primary_key=True)
    visible = models.SmallIntegerField()
    search = models.CharField(max_length=255)
    lastcron = models.BigIntegerField()
    cron = models.BigIntegerField()
    version = models.BigIntegerField()
    name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'mdl_unittest_modules'


class MdlUnittestQuiz(models.Model):
    id = models.BigIntegerField(primary_key=True)
    delay2 = models.BigIntegerField()
    delay1 = models.BigIntegerField()
    popup = models.SmallIntegerField()
    subnet = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    timelimit = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    grade = models.BigIntegerField()
    sumgrades = models.BigIntegerField()
    questions = models.TextField()
    shuffleanswers = models.SmallIntegerField()
    shufflequestions = models.SmallIntegerField()
    questionsperpage = models.BigIntegerField()
    review = models.BigIntegerField()
    decimalpoints = models.SmallIntegerField()
    grademethod = models.SmallIntegerField()
    attemptonlast = models.SmallIntegerField()
    attempts = models.IntegerField()
    penaltyscheme = models.SmallIntegerField()
    optionflags = models.BigIntegerField()
    timeclose = models.BigIntegerField()
    timeopen = models.BigIntegerField()
    intro = models.TextField()
    name = models.CharField(max_length=255)
    course = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_quiz'


class MdlUnittestScale(models.Model):
    id = models.BigIntegerField(primary_key=True)
    timemodified = models.BigIntegerField()
    description = models.TextField()
    scale = models.TextField()
    name = models.CharField(max_length=255)
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_scale'


class MdlUnittestScaleHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.TextField()
    scale = models.TextField()
    name = models.CharField(max_length=255)
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField()
    loggeduser = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)
    oldid = models.BigIntegerField()
    action = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_unittest_scale_history'


class MdlUpgradeLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.BigIntegerField()
    plugin = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=100, blank=True)
    targetversion = models.CharField(max_length=100, blank=True)
    info = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    backtrace = models.TextField(blank=True)
    userid = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_upgrade_log'


class MdlUrl(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()
    externalurl = models.TextField()
    display = models.SmallIntegerField()
    displayoptions = models.TextField(blank=True)
    parameters = models.TextField(blank=True)
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_url'


class MdlUser(models.Model):
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


class MdlUserDevices(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    appid = models.CharField(max_length=128)
    name = models.CharField(max_length=32)
    model = models.CharField(max_length=32)
    platform = models.CharField(max_length=32)
    version = models.CharField(max_length=32)
    pushid = models.CharField(max_length=255)
    uuid = models.CharField(max_length=255)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_user_devices'


class MdlUserEnrolments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    status = models.BigIntegerField()
    enrolid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timestart = models.BigIntegerField()
    timeend = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_user_enrolments'


class MdlUserInfoCategory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    sortorder = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_user_info_category'


class MdlUserInfoData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    fieldid = models.BigIntegerField()
    data = models.TextField()
    dataformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_user_info_data'


class MdlUserInfoField(models.Model):
    id = models.BigIntegerField(primary_key=True)
    shortname = models.CharField(max_length=255)
    name = models.TextField()
    datatype = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    categoryid = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    required = models.SmallIntegerField()
    locked = models.SmallIntegerField()
    visible = models.SmallIntegerField()
    defaultdata = models.TextField(blank=True)
    param1 = models.TextField(blank=True)
    param2 = models.TextField(blank=True)
    param3 = models.TextField(blank=True)
    param4 = models.TextField(blank=True)
    param5 = models.TextField(blank=True)
    forceunique = models.SmallIntegerField()
    signup = models.SmallIntegerField()
    defaultdataformat = models.SmallIntegerField()
    descriptionformat = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_user_info_field'


class MdlUserLastaccess(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField()
    timeaccess = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_user_lastaccess'


class MdlUserPasswordResets(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    timerequested = models.BigIntegerField()
    timererequested = models.BigIntegerField()
    token = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'mdl_user_password_resets'


class MdlUserPreferences(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=1333)

    class Meta:
        managed = False
        db_table = 'mdl_user_preferences'


class MdlUserPrivateKey(models.Model):
    id = models.BigIntegerField(primary_key=True)
    script = models.CharField(max_length=128)
    value = models.CharField(max_length=128)
    userid = models.BigIntegerField()
    instance = models.BigIntegerField(blank=True, null=True)
    iprestriction = models.CharField(max_length=255, blank=True)
    validuntil = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_user_private_key'


class MdlWebdavLocks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    token = models.CharField(unique=True, max_length=255)
    path = models.CharField(max_length=255)
    expiry = models.BigIntegerField()
    userid = models.BigIntegerField()
    recursive = models.SmallIntegerField()
    exclusivelock = models.SmallIntegerField()
    created = models.BigIntegerField()
    modified = models.BigIntegerField()
    owner = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_webdav_locks'


class MdlWiki(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    timemodified = models.BigIntegerField()
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()
    firstpagetitle = models.CharField(max_length=255)
    wikimode = models.CharField(max_length=20)
    defaultformat = models.CharField(max_length=20)
    forceformat = models.SmallIntegerField()
    editbegin = models.BigIntegerField()
    editend = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_wiki'


class MdlWikiLinks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    subwikiid = models.BigIntegerField()
    frompageid = models.BigIntegerField()
    topageid = models.BigIntegerField()
    tomissingpage = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_wiki_links'


class MdlWikiLocks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pageid = models.BigIntegerField()
    sectionname = models.CharField(max_length=255, blank=True)
    userid = models.BigIntegerField()
    lockedat = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_wiki_locks'


class MdlWikiPages(models.Model):
    id = models.BigIntegerField(primary_key=True)
    subwikiid = models.BigIntegerField()
    title = models.CharField(max_length=255)
    cachedcontent = models.TextField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    timerendered = models.BigIntegerField()
    userid = models.BigIntegerField()
    pageviews = models.BigIntegerField()
    readonly = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_wiki_pages'


class MdlWikiSubwikis(models.Model):
    id = models.BigIntegerField(primary_key=True)
    wikiid = models.BigIntegerField()
    groupid = models.BigIntegerField()
    userid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_wiki_subwikis'


class MdlWikiSynonyms(models.Model):
    id = models.BigIntegerField(primary_key=True)
    subwikiid = models.BigIntegerField()
    pageid = models.BigIntegerField()
    pagesynonym = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'mdl_wiki_synonyms'


class MdlWikiVersions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pageid = models.BigIntegerField()
    content = models.TextField()
    contentformat = models.CharField(max_length=20)
    version = models.IntegerField()
    timecreated = models.BigIntegerField()
    userid = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_wiki_versions'


class MdlWorkshop(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField(blank=True)
    introformat = models.SmallIntegerField()
    instructauthors = models.TextField(blank=True)
    instructauthorsformat = models.SmallIntegerField()
    instructreviewers = models.TextField(blank=True)
    instructreviewersformat = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    phase = models.SmallIntegerField(blank=True, null=True)
    useexamples = models.SmallIntegerField(blank=True, null=True)
    usepeerassessment = models.SmallIntegerField(blank=True, null=True)
    useselfassessment = models.SmallIntegerField(blank=True, null=True)
    grade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    gradinggrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    strategy = models.CharField(max_length=30)
    gradedecimals = models.SmallIntegerField(blank=True, null=True)
    nattachments = models.SmallIntegerField(blank=True, null=True)
    latesubmissions = models.SmallIntegerField(blank=True, null=True)
    maxbytes = models.BigIntegerField(blank=True, null=True)
    examplesmode = models.SmallIntegerField(blank=True, null=True)
    submissionstart = models.BigIntegerField(blank=True, null=True)
    submissionend = models.BigIntegerField(blank=True, null=True)
    assessmentstart = models.BigIntegerField(blank=True, null=True)
    assessmentend = models.BigIntegerField(blank=True, null=True)
    evaluation = models.CharField(max_length=30)
    phaseswitchassessment = models.SmallIntegerField()
    conclusion = models.TextField(blank=True)
    conclusionformat = models.SmallIntegerField()
    overallfeedbackmode = models.SmallIntegerField(blank=True, null=True)
    overallfeedbackfiles = models.SmallIntegerField(blank=True, null=True)
    overallfeedbackmaxbytes = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop'


class MdlWorkshopAggregations(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    userid = models.BigIntegerField()
    gradinggrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    timegraded = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_aggregations'


class MdlWorkshopAssessments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    submissionid = models.BigIntegerField()
    reviewerid = models.BigIntegerField()
    weight = models.BigIntegerField()
    timecreated = models.BigIntegerField(blank=True, null=True)
    timemodified = models.BigIntegerField(blank=True, null=True)
    grade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    gradinggrade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    gradinggradeover = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    gradinggradeoverby = models.BigIntegerField(blank=True, null=True)
    feedbackauthor = models.TextField(blank=True)
    feedbackauthorformat = models.SmallIntegerField(blank=True, null=True)
    feedbackreviewer = models.TextField(blank=True)
    feedbackreviewerformat = models.SmallIntegerField(blank=True, null=True)
    feedbackauthorattachment = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_assessments'


class MdlWorkshopAssessmentsOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    submissionid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timegraded = models.BigIntegerField()
    timeagreed = models.BigIntegerField()
    grade = models.FloatField()
    gradinggrade = models.SmallIntegerField()
    teachergraded = models.SmallIntegerField()
    mailed = models.SmallIntegerField()
    resubmission = models.SmallIntegerField()
    donotuse = models.SmallIntegerField()
    generalcomment = models.TextField()
    teachercomment = models.TextField()
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_assessments_old'


class MdlWorkshopCommentsOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    assessmentid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    mailed = models.SmallIntegerField()
    comments = models.TextField()
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_comments_old'


class MdlWorkshopElementsOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    elementno = models.SmallIntegerField()
    description = models.TextField()
    scale = models.SmallIntegerField()
    maxscore = models.SmallIntegerField()
    weight = models.SmallIntegerField()
    stddev = models.FloatField()
    totalassessments = models.BigIntegerField()
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_elements_old'


class MdlWorkshopGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assessmentid = models.BigIntegerField()
    strategy = models.CharField(max_length=30)
    dimensionid = models.BigIntegerField()
    grade = models.DecimalField(max_digits=10, decimal_places=5)
    peercomment = models.TextField(blank=True)
    peercommentformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_grades'


class MdlWorkshopGradesOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    assessmentid = models.BigIntegerField()
    elementno = models.BigIntegerField()
    feedback = models.TextField()
    grade = models.SmallIntegerField()
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_grades_old'


class MdlWorkshopOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    wtype = models.SmallIntegerField()
    nelements = models.SmallIntegerField()
    nattachments = models.SmallIntegerField()
    phase = models.SmallIntegerField()
    format = models.SmallIntegerField()
    gradingstrategy = models.SmallIntegerField()
    resubmit = models.SmallIntegerField()
    agreeassessments = models.SmallIntegerField()
    hidegrades = models.SmallIntegerField()
    anonymous = models.SmallIntegerField()
    includeself = models.SmallIntegerField()
    maxbytes = models.BigIntegerField()
    submissionstart = models.BigIntegerField()
    assessmentstart = models.BigIntegerField()
    submissionend = models.BigIntegerField()
    assessmentend = models.BigIntegerField()
    releasegrades = models.BigIntegerField()
    grade = models.SmallIntegerField()
    gradinggrade = models.SmallIntegerField()
    ntassessments = models.SmallIntegerField()
    assessmentcomps = models.SmallIntegerField()
    nsassessments = models.SmallIntegerField()
    overallocation = models.SmallIntegerField()
    timemodified = models.BigIntegerField()
    teacherweight = models.SmallIntegerField()
    showleaguetable = models.SmallIntegerField()
    usepassword = models.SmallIntegerField()
    password = models.CharField(max_length=32)
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_old'


class MdlWorkshopRubricsOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    elementno = models.BigIntegerField()
    rubricno = models.SmallIntegerField()
    description = models.TextField()
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_rubrics_old'


class MdlWorkshopStockcommentsOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    elementno = models.BigIntegerField()
    comments = models.TextField()
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_stockcomments_old'


class MdlWorkshopSubmissions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    example = models.SmallIntegerField(blank=True, null=True)
    authorid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    contentformat = models.SmallIntegerField()
    contenttrust = models.SmallIntegerField()
    attachment = models.SmallIntegerField(blank=True, null=True)
    grade = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    gradeover = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    gradeoverby = models.BigIntegerField(blank=True, null=True)
    feedbackauthor = models.TextField(blank=True)
    feedbackauthorformat = models.SmallIntegerField(blank=True, null=True)
    timegraded = models.BigIntegerField(blank=True, null=True)
    published = models.SmallIntegerField(blank=True, null=True)
    late = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_workshop_submissions'


class MdlWorkshopSubmissionsOld(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    userid = models.BigIntegerField()
    title = models.CharField(max_length=100)
    timecreated = models.BigIntegerField()
    mailed = models.SmallIntegerField()
    description = models.TextField()
    gradinggrade = models.SmallIntegerField()
    finalgrade = models.SmallIntegerField()
    late = models.SmallIntegerField()
    nassessments = models.BigIntegerField()
    newplugin = models.CharField(max_length=28, blank=True)
    newid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshop_submissions_old'


class MdlWorkshopallocationScheduled(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField(unique=True)
    enabled = models.SmallIntegerField()
    submissionend = models.BigIntegerField()
    timeallocated = models.BigIntegerField(blank=True, null=True)
    settings = models.TextField(blank=True)
    resultstatus = models.BigIntegerField(blank=True, null=True)
    resultmessage = models.CharField(max_length=1333, blank=True)
    resultlog = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopallocation_scheduled'


class MdlWorkshopevalBestSettings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField(unique=True)
    comparison = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopeval_best_settings'


class MdlWorkshopformAccumulative(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    sort = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)
    grade = models.BigIntegerField()
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopform_accumulative'


class MdlWorkshopformComments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    sort = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopform_comments'


class MdlWorkshopformNumerrors(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    sort = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)
    descriptiontrust = models.BigIntegerField(blank=True, null=True)
    grade0 = models.CharField(max_length=50, blank=True)
    grade1 = models.CharField(max_length=50, blank=True)
    weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopform_numerrors'


class MdlWorkshopformNumerrorsMap(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    nonegative = models.BigIntegerField()
    grade = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'mdl_workshopform_numerrors_map'


class MdlWorkshopformRubric(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField()
    sort = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    descriptionformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopform_rubric'


class MdlWorkshopformRubricConfig(models.Model):
    id = models.BigIntegerField(primary_key=True)
    workshopid = models.BigIntegerField(unique=True)
    layout = models.CharField(max_length=30, blank=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopform_rubric_config'


class MdlWorkshopformRubricLevels(models.Model):
    id = models.BigIntegerField(primary_key=True)
    dimensionid = models.BigIntegerField()
    grade = models.DecimalField(max_digits=10, decimal_places=5)
    definition = models.TextField(blank=True)
    definitionformat = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_workshopform_rubric_levels'
