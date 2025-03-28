# -*- coding: utf-8 -*-
{
    "name": "Report Sale Order and Invoice",
    "summary": "Change SO report and Invoice report",
    "version": "1.0.0",
    "website": "",
    "author": "Tri Nguyen",
    "depends": ['sale', 'purchase', 'account','l10n_sg_hr_payroll'],
    "data": [
        'views/purchase_view.xml',
    ],
    "application": True,
    "installable": True,
    "sequence": 1,
}
