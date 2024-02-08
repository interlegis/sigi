from parsel import Selector
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django_extensions.management.jobs import get_job


@login_required
@user_passes_test(lambda user: user.is_superuser)
def user_run_job(request, job_name):
    job = get_job(None, job_name)()
    start_time = timezone.localtime()
    job.do_job()
    end_time = timezone.localtime()
    rst, html = job.prepare_report(start_time, end_time)
    dp = Selector(text=html)

    return render(
        request,
        "admin/jobs/job_result.html",
        {"content": dp.xpath("//body/*").get()},
    )
