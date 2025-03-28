{
    'name': 'Batch Expenses',
    'version': '2.0',
    'category': 'Accounting/Expenses',
    'sequence': 95,
    'summary': 'Submit, validate and reinvoice employee expenses',
    'description': """This application allows you to manage batch expenses""",
    'website': 'https://www.odoo.com/page/expenses',
    'depends': ['hr_expense', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/batch_hr_expnse.xml',
        'views/hr_expense_view.xml',
    ],
    'installable': True,
    'application': True,
}
