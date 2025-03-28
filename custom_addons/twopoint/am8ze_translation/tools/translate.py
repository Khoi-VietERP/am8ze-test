import os, polib

for dirname, dirnames, filenames in os.walk('../i18n/'):
    for filename in filenames:
        try: ext = filename.rsplit('.', 1)[1]
        except: ext = ''
        if ext == 'po':
            pofile = polib.pofile(os.path.join(dirname, filename))
            for entry in pofile:
                if entry.msgid and 'Odoo' in entry.msgid or 'odoo' in entry.msgid:
                    entry.msgstr = entry.msgstr.replace('Am8ze', 'Alphabricks')
                    entry.msgstr = entry.msgstr.replace('am8ze', 'alphabricks')
            pofile.save()