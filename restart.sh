systemctl restart nginx
systemctl restart uwsgi
supervisorctl restart dzen_cc-celery-groups:*