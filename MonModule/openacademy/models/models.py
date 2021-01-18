# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, exceptions, _
from random import *


class OpenAcademy(models.Model):
    _name = 'openacademy.openacademy'
    name = fields.Char()


class Course(models.Model):
    _name = 'openacademy.course'
    _description = "OpenAcademy Courses"

    name = fields.Char(string="Title==", required=True)
    description = fields.Text()

    responsible_id = fields.Many2one('res.users',
        ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many(
        'openacademy.session', 'course_id', string="Sessions")

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', _(u"Copy of {}%").format(self.name))])
        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "Le titre du cours et la description doit être différent !!!"),

        ('name_unique',
         'UNIQUE(name)',
         "Le titre du cours doit être unique !!!"),
    ]


class Session(models.Model):
    _name = 'openacademy.session'
    _description = "OpenAcademy Sessions"

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Durée en jour(s)")
    seats = fields.Integer(string="Nombre de sièges")
    active = fields.Boolean(default=True)
    color = fields.Integer()

    instructor_id = fields.Many2one('res.partner', string="Professeur(e)",
        domain = ['|', ('instructor', '=', True),
            ('category_id.name', 'ilike', "Teacher")])
    course_id = fields.Many2one('openacademy.course',
        ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.One2many('res.partner.session', 'session_id', string="🙋 🙋‍ Participants-")

    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    satisfaction = fields.Float(string="Satisfaction", compute='_satisfaction', mode='determinate')
    end_date = fields.Date(string="End Date", store=True,
        compute='_get_end_date', inverse='_set_end_date')

    attendees_count = fields.Integer(
        string="🙋 🙋 Nombre de participants", compute='_get_attendees_count', store=True)

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    def _satisfaction(self):  # Permet de générer aléatoirement le taux de satisfaction
        for session in self:
            nbvotants = 0
            satisfaction = 0
            for participants in session.attendee_ids:
                if participants.votant == 1:
                    nbvotants = nbvotants + 1
                    if participants.satisfaction == 1:
                        satisfaction += 1
            if nbvotants >= 1:
                session.satisfaction = satisfaction*100 / nbvotants
            else:
                nbvotants = 1
                session.satisfaction = satisfaction * 100 / nbvotants

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': _("⚠ ERREUR : La valeur des sièges est incorecte !!!"),
                    'message': _("Le nombre de sièges ne peut-être négatif."),
                },
            }
        if self.seats < len(self.attendee_ids):
            import pdb # Sert au débogage
            # pdb.set_trace()
            assupr = self.attendee_ids[self.seats: ]
            for strop in assupr:
                self.attendee_ids = [(3, strop.id, 0)]
            return {
                'warning': {
                        'title': _("⚠ ERREUR : TROP DE PARTICIPANTS INITIALEMENT !!!"),
                        'message': _(" ↪️Veillez vérifier les participants de la session et si nécessaire, "
                                     "changer la capacité d'accueil des participants"),
                },
            }

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.end_date - r.start_date).days + 1

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            for p in r.attendee_ids:
                if r.instructor_id == p.respartner_id:
                    raise exceptions.ValidationError(_("⚠ ERREUR : Un enseigant ne peut-être en même temps un élève !!!"))


class ResPartnerSession(models.Model):
    _name = 'res.partner.session'
    _description = "OpenAcademy Partenaires Sessions"


    session_id = fields.Many2one('openacademy.session', string="🖥️ Session : ")
    respartner_id = fields.Many2one('res.partner', string="🚻 Participants : ")
    satisfaction = fields.Boolean('👍 Satisfaction : ')
    votant = fields.Boolean('☑ A voté : ')
