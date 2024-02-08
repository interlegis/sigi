import datetime
import docutils.core
import traceback
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django_extensions.management.jobs import BaseJob


class MisconfiguredError(Exception):
    pass


class QuarterDailyJob(BaseJob):
    when = "quarter_daily"


class JobReportMixin:
    error_report_template = "emails/report_error.rst"
    report_template = "emails/base_report.rst"
    report_data = None
    sys_user = None
    send_report_mail = True

    def execute(self):
        start_time = datetime.datetime.now()

        try:
            from sigi.apps.servidores.models import Servidor

            self.sys_user = Servidor.objects.get(sigi=True).user
        except Exception:
            pass

        try:
            self.do_job()
        except Exception as e:
            self.report_error(e)
            return
        end_time = datetime.datetime.now()
        self.report(start_time, end_time)

    def do_job(self):
        raise NotImplementedError("Job needs to implement the 'do_job' method")

    def _admin_log(self, object, action_flag, message=""):
        if self.sys_user is None:
            return  # No admin log
        LogEntry.objects.log_action(
            user_id=self.sys_user.id,
            content_type_id=ContentType.objects.get_for_model(type(object)).pk,
            object_id=object.id,
            object_repr=str(object),
            action_flag=action_flag,
            change_message=message,
        )

    def admin_log_addition(self, object, message=""):
        self._admin_log(object, ADDITION, message)

    def admin_log_change(self, object, message=""):
        self._admin_log(object, CHANGE, message)

    def report_error(self, error):
        rst = render_to_string(
            self.error_report_template,
            {
                "title": self.help,
                "traceback": traceback.format_exception(error),
            },
        )
        html = docutils.core.publish_string(
            rst,
            writer_name="html5",
            settings_overrides={
                "input_encoding": "unicode",
                "output_encoding": "unicode",
            },
        )
        mail_admins(
            subject=self.help,
            message=rst,
            html_message=html,
            fail_silently=True,
        )
        print(rst)

    def prepare_report(self, start_time, end_time):
        """Prepara RST e HTML do relatório do JOB

        Args:
            start_time (datetime): Timestamp do início da execução
            end_time (datetime): Timestamp do término da execução

        Returns:
            tupla(rst: str, html:str): Retorna o relatório do job formatado em
                                       RST e HTML.
        """
        rst = render_to_string(
            self.report_template,
            {
                "title": self.help,
                "start_time": start_time,
                "end_time": end_time,
                "report_data": self.report_data,
            },
        )
        html = docutils.core.publish_string(
            rst,
            writer_name="html5",
            settings_overrides={
                "input_encoding": "unicode",
                "output_encoding": "unicode",
            },
        )
        return (rst, html)

    def report(self, start_time, end_time):
        if self.report_data is None:
            raise MisconfiguredError(
                "Job needs to define 'report_data' property"
            )

        rst, html = self.prepare_report(start_time, end_time)

        if self.send_report_mail:
            mail_admins(
                subject=f"JOB: {self.help}",
                message=rst,
                html_message=html,
                fail_silently=True,
            )
        print(rst)
