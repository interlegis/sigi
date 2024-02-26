import docutils.core
import io
from contextlib import redirect_stdout, redirect_stderr
from parsel import Selector
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django_extensions.management.jobs import get_job
from sigi.apps.utils.models import JobSchedule


@login_required
@user_passes_test(lambda user: user.is_superuser)
def user_run_job(request, job_name):
    job = get_job(None, job_name)()
    start_time = timezone.localtime()
    if hasattr(job, "do_job"):
        job.do_job()
        end_time = timezone.localtime()
        rst, html = job.prepare_report(start_time, end_time)
    else:
        with io.StringIO() as so_buf, io.StringIO() as se_buf, redirect_stdout(
            so_buf
        ), redirect_stderr(se_buf):
            job.execute()
            messages = so_buf.getvalue()
            errors = se_buf.getvalue()
        report_data = ["", "MENSAGENS", "---------", ""]
        if messages:
            report_data.extend(messages.splitlines())
        else:
            report_data.extend(["Nenhuma mensagem gerada", ""])
        report_data.extend(["", "ERROS", "-----", ""])
        if errors:
            report_data.extend(errors.splitlines())
        else:
            report_data.extend(["Nenhum erro gerado", ""])
        end_time = timezone.localtime()
        rst = render_to_string(
            "emails/base_report.rst",
            {
                "title": job.help,
                "start_time": start_time,
                "end_time": end_time,
                "report_data": report_data,
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

    dp = Selector(text=html)

    return render(
        request,
        "admin/jobs/job_result.html",
        {"content": dp.xpath("//body/*").get()},
    )
