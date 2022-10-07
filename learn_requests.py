# "requests" document:
# [ref] https://requests.readthedocs.io/en/latest/user/quickstart/

import requests

r = requests.get('https://api.github.com/events')
# print(r)

""" 
# "underscore meaning"
# [ref] https://towardsdatascience.com/whats-the-meaning-of-single-and-double-underscores-in-python-3d27d57d6bd1

import datetime

class Employee:
    def __init__(self, first_name, last_name, start_date):
        self.first_name = first_name
        self.last_name = last_name
        self.start_date = start_date
        self._seniority = self._get_seniority(start_date)

    def _get_seniority(self, start_date):
        today_date = datetime.datetime.today().date()
        seniority = (today_date - start_date).days
        return seniority
    
    def compute_compensation_package(self):
        # use self._seniority here.
        pass

first_name = "John"
last_name = "Doe"
start_date = datetime.date(2022, 9, 1)
employee = Employee(first_name, last_name, start_date)

print(employee._seniority) 
"""