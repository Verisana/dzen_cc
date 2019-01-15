systemctl restart nginx
systemctl restart uwsgi
supervisorctl restart dzen-cc-celery-groups:*