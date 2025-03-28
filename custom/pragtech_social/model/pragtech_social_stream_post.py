# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, models, fields
from odoo.tools.misc import format_date, _format_time_ago


class PragtechSocialStreamPost(models.Model):

    _name = 'pragtech.social.stream.post'
    _description = 'Pragtech Linked Page Post'

    stream_post_message = fields.Text("Message")
    stream_post_author_name = fields.Char('Author Name')
    stream_post_stream_id = fields.Many2one(
        'pragtech.social.stream',
        string="Linked Page",
        ondelete="cascade")
    formatted_published_date = fields.Char(
        string='Published Formatted Date',
        compute='_compute_published_date')
    stream_post_published_date = fields.Datetime(
        string='Published date')
    stream_post_account_id = fields.Many2one(
        related='stream_post_stream_id.stream_account_id',
        string='Related Linked Account',
        store=True)
    image_ids = fields.One2many(
        'pragtech.social.stream.post.image',
        'stream_post_id',
        string="Stream Post Images")

    @api.depends('stream_post_published_date')
    def _compute_published_date(self):
        for line in self:
            date_new = False
            if line.stream_post_published_date:
                if (datetime.now() - line.stream_post_published_date) < timedelta(hours=12):
                    date_new = _format_time_ago(self.env, (datetime.now() - line.stream_post_published_date),
                                            add_direction=False)
                else:
                    date_new = format_date(self.env, line.stream_post_published_date)
            matches = ['minutes', 'hours', 'minute', 'hour', 'seconds']
            if any(x in date_new for x in matches):
                date_new = fields.Date.today()
                line.formatted_published_date = date_new.strftime('%d %B %Y')
            else:
                convert_date = datetime.strptime(date_new, '%m/%d/%Y')
                line.formatted_published_date = convert_date.strftime('%d %B %Y')


class SocialStreamAttachment(models.Model):
    _name = 'pragtech.social.stream.post.image'
    _description = 'Linked Page Post Image Attachment'

    image_url = fields.Char(
        string="URL",
        readonly=True,
        required=True)
    stream_post_id = fields.Many2one(
        'pragtech.social.stream.post',
        string="Stream Post",
        ondelete="cascade")