#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name': 'Document Management System',
    'summary': """Document Management System to manage your company documents inside odoo properly.
    """,
    'description': """
    Document Management System to manage your company documents inside odoo properly. document management software document directory document access acs
    document management system documents manage document attachment management manage attachments. Document revisions document revision management almightycs
    document preview manage documents manage attachments document portal management portal document access

    Document Management System, um Ihre Unternehmensdokumente in odoo richtig zu verwalten. Dokumentverwaltungssoftware Dokumentverzeichnis Dokumentzugriff acs
     Dokumentverwaltungssystemdokumente Verwalten Sie die Verwaltung von Anhängen. Dokumentrevisionen Dokumentverwaltungsmanagement-Allmächtige
     Dokumentvorschau Dokumente verwalten Anhänge verwalten Dokumentportal-Verwaltungsportal Dokumentzugriff
    
    Système de gestion de documents pour gérer les documents de votre entreprise dans odoo correctement. logiciel de gestion de documents répertoire de documents accès aux documents acs
     système de gestion des documents documents gérer la gestion des pièces jointes, gérer les pièces jointes. Révisions de document gestion de révision de document tout-puissant
     aperçu des documents gérer les documents gérer les pièces jointes portail de documents portail de gestion accès aux documents

    Sistema de gestión de documentos para gestionar adecuadamente los documentos de su empresa dentro de odoo. software de gestión de documentos directorio de documentos acceso a documentos acs
     sistema de gestión de documentos documentos de gestión de documentos adjuntos gestión de archivos adjuntos. Revisiones de documentos revisión de documentos gestión almightycs
     Vista previa de documentos Administrar documentos Administrar archivos adjuntos Portal de administración Acceso a documentos del portal
    """,
    'version': '1.0.6',
    'category': 'Document Management',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/multi_document_view.xml',
        'views/document_management_view.xml',
        'views/menu_item.xml',
    ],
    'images': [
        'static/description/document_management_cover.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 26,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: