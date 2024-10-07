#! /usr/bin/env python3
"""
Identify Redmine tickets which are assigned to users, and notify those users.
'The ball's in your court on this one'.
"""
import argparse
import email
import logging
import smtplib
import sys

import jinja2
from redminelib import Redmine

from .config import settings

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def send_html_email(to, subject, text_body, html_body):
    msg = email.message.EmailMessage()
    msg['Subject'] = subject
    msg['From'] = settings.smtp_from
    msg['To'] = to
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype='html')
    with smtplib.SMTP_SSL(settings.smtp_server, port=settings.smtp_port) as smtp:
        # smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)

def main():
    # Allow some options to be ovverridden by command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--list_projects', action='store_true', 
                        help='List projects and exit - a good test of credentials')
    parser.add_argument('-u', '--list_users', action='store_true', 
                        help='List users and exit - the first field gives the username that can be used to generate individual reports.')
    parser.add_argument('-n', '--dry_run', action='store_true', help='Do not send emails')
    parser.add_argument('-d', '--debug_email', metavar="ADDR", help='Send all emails to this address, instead of each user, for debugging purposes.')

    args = parser.parse_args(sys.argv[1:])
    settings.update(vars(args))

    redmine = Redmine(settings.url, key=settings.key)

    if settings.list_projects:
        projects = redmine.project.all()
        for project in projects:
            print(f"{project.identifier} {project.name}")
        return
    
    if settings.list_users:
        users = redmine.user.all()
        for user in users:
            print(f"{user.login} <{user.mail}> {user.firstname} {user.lastname}")
        return
    
    subject_template = jinja2.Template(settings.subject_template)
    text_template = jinja2.Template(settings.text_report_template)
    html_template = jinja2.Template(settings.html_report_template)

    # Let's do some filtering of users and projects
    all_users = redmine.user.all()
    all_projects = redmine.project.all()
    
    # You can specify lists of usernames in the settings file
    # to include or exclude. The default is to include all users.
    if 'include_users' in settings:
        users = [ u for u in all_users if u.login in settings.include_users ]
    else:
        users  = all_users
    if 'exclude_users' in settings:
        users = [ u for u in users if u.login not in settings.exclude_users ]
    
    # You can specify lists of project identifiers in the settings
    # to include or exclude. The default is to include all projects.
    if 'include_projects' in settings:
        projects = [ p for p in all_projects if p.identifier in settings.include_projects ]
    else:
        projects = all_projects
    if 'exclude_projects' in settings:
        projects = [ p for p in projects if p.identifier not in settings.exclude_projects ]
    project_ids = [ p.id for p in projects ]

    for user in users:
        # Can't notify users without an email address
        # if user.mail is None:
        #    continue
        issues = redmine.issue.filter(assigned_to_id=user.id, status_id='open', sort='priority:desc')
        issues = [ i for i in issues if i.project.id in project_ids ]

        if issues:
            log.info(f"User {user.id} ({user.login} {user.mail}) has {len(issues)} open issues - generating report")
            env = {'settings': settings, 'user': user, 'issues': issues}

            subject = subject_template.render(env)
            text_report = text_template.render(env)
            html_report = html_template.render(env)

            if settings.dry_run:
                print(f"This is a dry run - NOT sending the following email to {user.mail}:")
                print(f"Subject: {subject}")
                print(html_report)
            else:
                if settings.debug_email:
                    print(f"Sending email to debug address {settings.debug_email} instead of {user.mail}")
                    send_html_email(settings.debug_email, subject, text_report, html_report)
                else:
                    log.info(f"Sending email to {user.mail}")
                    send_html_email(user.mail, subject, text_report, html_report)
        else:
            log.debug(f"User {user.id} ({user.login} {user.mail}) has no issues")

if __name__ == "__main__":
    main()

